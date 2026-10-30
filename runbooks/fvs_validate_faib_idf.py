#!/usr/bin/env python3
"""Validate FVS-BC against repeated FAIB IDFdk3/IDFxm measurements.

This is the independent-site validation set for the KC growth model.  It uses
the public FAIB tree detail, not the 24 Marshall plots.  Sites are restricted to
IDFdk3/IDFxm, at least two measurements at least 10 years apart, and at least
50% Douglas-fir basal area at the first measurement.

Usage::

    python runbooks/fvs_validate_faib_idf.py \
      --raw-dir /path/to/faib/downloads/psp \
      --out-dir ws4/kc_faib_validation \
      --runtime-dir runtime/kc_faib_validation \
      --parameters ws4/kc_psp_calibration/calibration_parameters.json
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.nemora import crown_class
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import resolve_species

SPECIES_MAP = {"SX": "SE", "W": "OH"}
BA_FACTOR = 0.00007854
MIN_YEARS = 10
MIN_FD_SHARE = 0.5


def _record(row: pd.Series, plot_id: int, tree_num: int) -> dict[str, object]:
    """Build one FVS tree record using the FAIB expansion factor."""
    height = float(row["HEIGHT"]) if np.isfinite(row["HEIGHT"]) else 1.3 + 0.5 * float(row["DBH"])
    crown = {"C": 0.65, "I": 0.55, "S": 0.45, "D": 0.30}.get(
        str(row["CR_CL"]).strip().upper(), 0.45
    )
    species = str(row["SPECIES"]).strip().upper()
    species = SPECIES_MAP.get(species, species)
    try:
        species = resolve_species(species)
    except Exception:
        species = "OH"
    return {
        "plot_id": plot_id,
        "tree_num": tree_num,
        "tree_count": float(row["PHF_TREE"]),
        "tree_history": 0,
        "species": species,
        "diam": float(row["DBH"]),
        "dg_incr": 0.0,
        "live_ht": height,
        "trunc_ht": 0.0,
        "htg_incr": 0.0,
        "crown_ratio": crown_class(crown),
        "damage1": 0,
        "severity1": 0,
        "damage2": 0,
        "severity2": 0,
        "damage3": 0,
        "severity3": 0,
        "tree_val": 0,
        "tree_rx": 0,
        "plot_slope": 0,
        "plot_aspect": 0,
        "plot_habitat": 0,
        "plot_topo_pos": 0,
        "plot_site_prep": 0,
        "tree_age": 0.0,
    }


def _keywords(
    site: str,
    start_year: int,
    interval: int,
    ba: dict[str, float] | None,
    mort: dict[str, float] | None,
) -> list[Keyword]:
    """Build a one-interval no-cut key set."""
    return [
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary", "TREELIDB")),
        Keyword("STDIDENT", (f"FAIB {site}",)),
        Keyword("STDINFO", ("712", "CHS131", "0", str(interval), "35", "16")),
        Keyword("MANAGED", ("0", "1")),
        Keyword("INVYEAR", (str(start_year),)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("1", str(interval))),
        Keyword("NUMCYCLE", ("1",)),
        Keyword("RANNSEED", ("1",)),
        *(
            [
                Keyword("BAIMULT", ("1", species, f"{value:.4f}"))
                for species, value in (ba or {}).items()
            ]
        ),
        *(
            [
                Keyword("MORTMULT", ("1", species, f"{value:.4f}", "0", "999"))
                for species, value in (mort or {}).items()
            ]
        ),
        Keyword("TREELIST", ("1",)),
        Keyword("PROCESS"),
        Keyword("STOP"),
    ]


def _metrics(group: pd.DataFrame) -> dict[str, float]:
    """Observed stand metrics from a FAIB live-tree list."""
    if group.empty:
        return {
            "ba_m2_ha": np.nan,
            "tph": np.nan,
            "qmd_cm": np.nan,
            "fd_share": np.nan,
        }
    ba = BA_FACTOR * group["DBH"] ** 2 * group["PHF_TREE"]
    tph = group["PHF_TREE"].sum()
    fd = group["SPECIES"].astype(str).str.upper().isin(["FD", "FDI"])
    return {
        "ba_m2_ha": float(ba.sum()),
        "tph": float(tph),
        "qmd_cm": float(np.sqrt((group["DBH"] ** 2 * group["PHF_TREE"]).sum() / tph)),
        "fd_share": float(ba[fd].sum() / ba.sum()) if ba.sum() else np.nan,
    }


def _expand(values: dict[str, float]) -> dict[str, float]:
    """Expand species-group multipliers to FVS species codes."""
    groups = {"FD": ("FD",), "SE": ("SE",), "PL": ("PL",), "HW": ("EP", "AT", "OH")}
    return {
        species: float(values[group])
        for group, species_plan in groups.items()
        for species in species_plan
    }


def _run_set(
    sites: pd.DataFrame,
    trees: pd.DataFrame,
    *,
    label: str,
    ba: dict[str, float] | None,
    mort: dict[str, float] | None,
    runtime_dir: Path,
) -> pd.DataFrame:
    """Run every site for one parameter set."""
    rows = []
    for site, row in sites.set_index("site").iterrows():
        start = trees[trees["site"] == site]
        interval = int(row["end_year"] - row["start_year"])
        case_dir = runtime_dir / label / str(site)
        if case_dir.exists():
            shutil.rmtree(case_dir)
        records = [
            _record(tree_row, plot_id=int(tree_row["PLOT"]), tree_num=index + 1)
            for index, (_, tree_row) in enumerate(start.iterrows())
        ]
        result = run_case(
            records,
            _keywords(
                str(site),
                int(row["start_year"]),
                interval,
                _expand(ba) if ba else None,
                _expand(mort) if mort else None,
            ),
            directory=case_dir,
        )
        summary = read_table(result.database, "FVS_Summary_Metric")
        summary = summary[summary["CaseID"] == result.provenance.case_id]
        final = summary[summary["Year"] == int(row["end_year"])]
        if final.empty:
            raise ValueError(f"missing FVS summary for {site} at {row['end_year']}")
        point = final.iloc[0]
        rows.append(
            {
                "site": site,
                "start_year": int(row["start_year"]),
                "end_year": int(row["end_year"]),
                "years": interval,
                "pred_ba_m2_ha": float(point["BA"]),
                "pred_tph": float(point["Tph"]),
                "pred_qmd_cm": float(point["QMD"]),
            }
        )
    return pd.DataFrame(rows)


def _evaluate(pred: pd.DataFrame, obs: pd.DataFrame) -> pd.DataFrame:
    """Join predictions and observations and add residuals."""
    joined = obs.merge(pred, on=["site", "start_year", "end_year", "years"], how="inner")
    joined["ba_error"] = joined["pred_ba_m2_ha"] - joined["ba_m2_ha"]
    joined["qmd_error"] = joined["pred_qmd_cm"] - joined["qmd_cm"]
    joined["tph_error"] = joined["pred_tph"] - joined["tph"]
    return joined


def _summary(joined: pd.DataFrame) -> pd.DataFrame:
    """Aggregate bias and MAE."""
    return pd.DataFrame(
        [
            {
                "n": len(joined),
                "obs_ba": joined["ba_m2_ha"].mean(),
                "pred_ba": joined["pred_ba_m2_ha"].mean(),
                "ba_bias": joined["ba_error"].mean(),
                "ba_mae": joined["ba_error"].abs().mean(),
                "obs_qmd": joined["qmd_cm"].mean(),
                "pred_qmd": joined["pred_qmd_cm"].mean(),
                "qmd_bias": joined["qmd_error"].mean(),
                "qmd_mae": joined["qmd_error"].abs().mean(),
                "obs_tph": joined["tph"].mean(),
                "pred_tph": joined["pred_tph"].mean(),
                "tph_bias": joined["tph_error"].mean(),
                "tph_mae": joined["tph_error"].abs().mean(),
            }
        ]
    )


def main() -> None:
    """Build the FAIB validation panel and run the FVS comparison."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--parameters", type=Path, required=True)
    parser.add_argument("--max-sites", type=int, default=0)
    args = parser.parse_args()

    header = pd.read_csv(
        args.raw_dir / "faib_header.csv",
        usecols=["SITE_IDENTIFIER", "BEC_ZONE", "BEC_SBZ", "BEC_VAR"],
    )
    header = header[
        (header["BEC_ZONE"] == "IDF")
        & (((header["BEC_SBZ"] == "dk") & (header["BEC_VAR"] == 3)) | (header["BEC_SBZ"] == "xm"))
    ]
    visits = pd.read_csv(
        args.raw_dir / "faib_sample_byvisit.csv",
        usecols=["SITE_IDENTIFIER", "CLSTR_ID", "VISIT_NUMBER", "MEAS_YR"],
    )
    visits = visits[visits["SITE_IDENTIFIER"].isin(header["SITE_IDENTIFIER"])]
    visits = visits.dropna(subset=["MEAS_YR"]).sort_values(["SITE_IDENTIFIER", "MEAS_YR"])
    counts = visits.groupby("SITE_IDENTIFIER").agg(
        n_visits=("VISIT_NUMBER", "nunique"),
        start_year=("MEAS_YR", "min"),
        end_year=("MEAS_YR", "max"),
    )
    counts = counts[
        (counts["n_visits"] >= 2) & ((counts["end_year"] - counts["start_year"]) >= MIN_YEARS)
    ].reset_index()

    trees = pd.read_csv(
        args.raw_dir / "faib_tree_detail.csv",
        usecols=[
            "SITE_IDENTIFIER",
            "CLSTR_ID",
            "VISIT_NUMBER",
            "PLOT",
            "TREE_NO",
            "SPECIES",
            "DBH",
            "HEIGHT",
            "LV_D",
            "CR_CL",
            "PHF_TREE",
        ],
        low_memory=False,
    )
    trees = trees[
        trees["SITE_IDENTIFIER"].isin(set(counts["SITE_IDENTIFIER"]))
        & (trees["LV_D"] == "L")
        & trees["DBH"].notna()
        & trees["PHF_TREE"].notna()
    ].copy()
    first_last = (
        visits.groupby("SITE_IDENTIFIER")
        .agg(
            start_clstr=("CLSTR_ID", "first"),
            end_clstr=("CLSTR_ID", "last"),
            start_year=("MEAS_YR", "min"),
            end_year=("MEAS_YR", "max"),
        )
        .reset_index()
    )
    first_last = first_last.merge(
        counts[["SITE_IDENTIFIER", "n_visits"]], on="SITE_IDENTIFIER", how="inner"
    )
    start_trees = trees.merge(
        first_last[["SITE_IDENTIFIER", "start_clstr"]],
        left_on=["SITE_IDENTIFIER", "CLSTR_ID"],
        right_on=["SITE_IDENTIFIER", "start_clstr"],
        how="inner",
    )
    metrics = start_trees.groupby("SITE_IDENTIFIER").apply(_metrics, include_groups=False)
    metrics = pd.DataFrame(metrics.tolist(), index=metrics.index).reset_index()
    metrics = metrics.rename(
        columns={
            "SITE_IDENTIFIER": "site",
            "ba_m2_ha": "start_ba_m2_ha",
            "tph": "start_tph",
            "qmd_cm": "start_qmd_cm",
            "fd_share": "start_fd_share",
        }
    )
    sites = first_last.rename(columns={"SITE_IDENTIFIER": "site"})
    sites = sites.merge(metrics, on="site", how="inner")
    sites = sites[sites["start_fd_share"] >= MIN_FD_SHARE].copy()
    if args.max_sites:
        sites = sites.sort_values(["start_fd_share", "n_visits"], ascending=False).head(
            args.max_sites
        )
    if sites.empty:
        raise ValueError("no FAIB sites passed the filter")

    start_rows = start_trees[start_trees["SITE_IDENTIFIER"].isin(set(sites["site"]))].copy()
    start_rows = start_rows.rename(columns={"SITE_IDENTIFIER": "site"})
    end_rows = trees.merge(
        first_last[["SITE_IDENTIFIER", "end_clstr"]],
        left_on=["SITE_IDENTIFIER", "CLSTR_ID"],
        right_on=["SITE_IDENTIFIER", "end_clstr"],
        how="inner",
    )
    end_rows = end_rows[end_rows["SITE_IDENTIFIER"].isin(set(sites["site"]))].copy()
    # Compare against trees present at both measurements.  FVS-BC does not
    # reproduce the FAIB small-tree ingrowth pulse, so total end-of-period TPH
    # would confound model error with recruitment.
    survivor_rows = end_rows.merge(
        start_rows[["site", "TREE_NO"]],
        left_on=["SITE_IDENTIFIER", "TREE_NO"],
        right_on=["site", "TREE_NO"],
        how="inner",
    )
    end_metrics = survivor_rows.groupby("SITE_IDENTIFIER").apply(_metrics, include_groups=False)
    end_metrics = pd.DataFrame(end_metrics.tolist(), index=end_metrics.index).reset_index()
    end_metrics = end_metrics.rename(
        columns={
            "SITE_IDENTIFIER": "site",
            "ba_m2_ha": "ba_m2_ha",
            "tph": "tph",
            "qmd_cm": "qmd_cm",
            "fd_share": "end_fd_share",
        }
    )
    observed = sites.merge(end_metrics, on="site", how="inner")
    observed = observed[
        [
            "site",
            "start_year",
            "end_year",
            "start_fd_share",
            "ba_m2_ha",
            "tph",
            "qmd_cm",
            "end_fd_share",
        ]
    ].copy()
    observed["years"] = observed["end_year"] - observed["start_year"]

    parameters = json.loads(args.parameters.read_text())
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.runtime_dir.mkdir(parents=True, exist_ok=True)
    uncal = _run_set(
        sites,
        start_rows,
        label="uncalibrated",
        ba=None,
        mort=None,
        runtime_dir=args.runtime_dir,
    )
    cal = _run_set(
        sites,
        start_rows,
        label="calibrated",
        ba=parameters["ba_multiplier"],
        mort=parameters["mortality_multiplier"],
        runtime_dir=args.runtime_dir,
    )
    uncal_eval = _evaluate(uncal, observed)
    cal_eval = _evaluate(cal, observed)
    uncal_eval.to_csv(args.out_dir / "validation_uncalibrated.csv", index=False)
    cal_eval.to_csv(args.out_dir / "validation_calibrated.csv", index=False)
    _summary(uncal_eval).to_csv(args.out_dir / "summary_uncalibrated.csv", index=False)
    _summary(cal_eval).to_csv(args.out_dir / "summary_calibrated.csv", index=False)
    sites.to_csv(args.out_dir / "validation_sites.csv", index=False)
    manifest = {
        "validation": "faib-idf-independent-site-v1",
        "sites": len(sites),
        "filter": {
            "BEC": "IDFdk3 and IDFxm",
            "min_visits": 2,
            "min_interval_years": MIN_YEARS,
            "min_fd_share": MIN_FD_SHARE,
        },
        "parameters": str(args.parameters),
        "caveats": [
            "FAIB plots are independent of the 24 Marshall plots but are not a whole-block sample.",
            "Plot designs and expansion factors vary across FAIB sites.",
            "No cutting is simulated.",
            "No age or site index is assigned.",
            "This is a growth-model validation, not a legal-compliance determination.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("uncalibrated")
    print(_summary(uncal_eval).to_string(index=False))
    print("calibrated")
    print(_summary(cal_eval).to_string(index=False))


if __name__ == "__main__":
    main()
