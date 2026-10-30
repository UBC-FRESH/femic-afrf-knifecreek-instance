#!/usr/bin/env python3
"""Build multi-entry AU selection curves for KC.

Each matched FAIB plot gets repeated GWM entries at cycles 4, 7, 10, 13, 16 and
19 (nominally years 30 to 180), followed by residual growth to year 200. The
entry residual state is taken from the FVS summary (`ATBA`, `ATQMD`, `ATCCF`,
removed TPH and removed volume), not from the pre-cut stand.

Usage::

    python runbooks/build_kc_au_multientry_200y.py \
      --au-table data/kc_au/kc_au_table.csv \
      --matches data/psp/kc_au_200y/kc_au_plot_matches.csv \
      --panel data/psp/idf_cariboo_space_for_time_plots.csv \
      --raw-dir /path/to/faib/raw \
      --out-dir data/psp/kc_au_200y \
      --regime GWM_MODERATE
"""

from __future__ import annotations

import argparse
import json
import shutil
from itertools import pairwise
from pathlib import Path

import numpy as np
import pandas as pd
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.nemora import crown_class
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import resolve_species

HORIZON_YEARS = 200
STEP_YEARS = 10
CYCLES = (4, 7, 10, 13, 16, 19)
ENTRY_YEARS = tuple((cycle - 1) * STEP_YEARS for cycle in CYCLES)
FT2_PER_M2 = 4.356
REGIMES = {
    # The q field is the FVS THINQFA target, not the measured legal q. The
    # FVS target is set above the legal midpoint so the tree-list 5 cm q lands
    # inside the legal range; measured q is reported separately.
    "GWM_LOW": {"B": 16.0, "large": 6.0, "reserve": 1.6, "D": 50.0, "q": 1.55},
    "GWM_MODERATE": {"B": 22.0, "large": 11.0, "reserve": 2.2, "D": 60.0, "q": 1.50},
}
SPECIES_MAP = {"FDI": "FD", "PLI": "PL", "SX": "SW", "AT": "AT"}
LARGE_THRESHOLD = 37.5


def _reserved_ids(after: pd.DataFrame, regime: str) -> set[int]:
    """Return the above-D tree indexes left by the reserve cut."""
    if after.empty:
        return set()
    d_target = REGIMES[regime]["D"]
    return {int(value) for value in after.loc[after["DBH"] > d_target, "TreeIndex"]}


def _reserve_metrics(frame: pd.DataFrame, ids: set[int]) -> tuple[float, float]:
    """Return reserve BA and TPH for the retained tree indexes."""
    if frame.empty or not ids:
        return 0.0, 0.0
    selected = frame[frame["TreeIndex"].astype(int).isin(ids)].copy()
    if selected.empty:
        return 0.0, 0.0
    ba = float((0.00007854 * selected["DBH"] ** 2 * selected["TPH"]).sum())
    return ba, float(selected["TPH"].sum())


def _q_factor(frame: pd.DataFrame) -> float:
    """Return the median 5 cm TPH-class ratio."""
    if frame.empty or frame["TPH"].sum() <= 0:
        return 0.0
    classes = (frame["DBH"] // 5 * 5 + 2.5).astype(float)
    density = frame.assign(dbh_class=classes).groupby("dbh_class")["TPH"].sum()
    grid = np.arange(classes.min(), classes.max() + 5.0, 5.0)
    density = density.reindex(grid, fill_value=0.0)
    ratios = [
        float(density.loc[lower] / density.loc[upper])
        for lower, upper in pairwise(grid)
        if density.loc[lower] > 0 and density.loc[upper] > 0
    ]
    return float(np.median(ratios)) if ratios else 0.0


def _tree_metrics(frame: pd.DataFrame) -> dict[str, float]:
    """Return max DBH and q for one tree list."""
    if frame.empty:
        return {"max_dbh_cm": 0.0, "q_factor": 0.0}
    return {
        "max_dbh_cm": float(frame["DBH"].max()),
        "q_factor": _q_factor(frame),
    }


def _bec_variant(row: pd.Series) -> str:
    """Return the BEC variant string for a FAIB plot."""
    variant = row["BEC_VAR"]
    if pd.isna(variant):
        variant_text = ""
    elif float(variant).is_integer():
        variant_text = str(int(variant))
    else:
        variant_text = str(variant)
    return f"IDF{row['BEC_SBZ']}{variant_text}"


def _records(state: pd.Series, trees: pd.DataFrame) -> list[dict[str, object]]:
    """Build FVS tree records from one FAIB plot state."""
    selected = trees[
        (trees["CLSTR_ID"] == state["CLSTR_ID"]) & (trees["VISIT_NUMBER"] == state["VISIT_NUMBER"])
    ].copy()
    records = []
    for number, row in enumerate(selected.itertuples(index=False), start=1):
        species = str(row.SPECIES).strip().upper()
        species = SPECIES_MAP.get(species, species)
        try:
            species = resolve_species(species)
        except Exception:
            species = "OH"
        crown = {"C": 0.65, "I": 0.55, "S": 0.45, "D": 0.30}.get(
            str(row.CR_CL).strip().upper(), 0.45
        )
        height = float(row.HEIGHT) if np.isfinite(row.HEIGHT) else 1.3 + 0.5 * float(row.DBH)
        records.append(
            {
                "plot_id": 1,
                "tree_num": number,
                "tree_count": float(row.PHF_TREE),
                "tree_history": 0,
                "species": species,
                "diam": float(row.DBH),
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
                "tree_age": float(state["PROJ_AGE_1"]),
            }
        )
    return records


def _keywords(site_index: float, regime: str) -> list[Keyword]:
    """Return the 200-year multi-entry key set."""
    spec = REGIMES[regime]
    thinning = []
    for cycle in CYCLES:
        thinning.append(
            Keyword(
                "THINABA",
                (
                    str(cycle),
                    str(spec["large"]),
                    "1.0",
                    "37.5",
                    str(spec["D"]),
                    "0.0",
                    "999.0",
                ),
            )
        )
        thinning.append(
            Keyword(
                "THINABA",
                (
                    str(cycle),
                    str(spec["reserve"]),
                    "1.0",
                    str(spec["D"]),
                    "999.0",
                    "0.0",
                    "999.0",
                ),
            )
        )
        thinning.append(
            Keyword(
                "THINQFA",
                (
                    str(cycle),
                    "2.5",
                    "37.5",
                    "0",
                    str(spec["q"]),
                    "5.0",
                    str(round((spec["B"] - spec["large"]) * FT2_PER_M2, 2)),
                ),
                supplemental=("0",),
            )
        )
    return [
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary", "TREELIDB", "ATRTLIDB")),
        Keyword("STDIDENT", (f"KC-AU-{regime}-MULTI-200Y",)),
        Keyword("STDINFO", ("712", "CHS131", "0", str(HORIZON_YEARS), "35", "16")),
        Keyword("MANAGED", ("0", "1")),
        Keyword("SITECODE", ("FD", f"{site_index:.1f}")),
        Keyword("INVYEAR", ("0",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", str(STEP_YEARS))),
        Keyword("NUMCYCLE", (str(HORIZON_YEARS // STEP_YEARS),)),
        Keyword("RANNSEED", ("1",)),
        *[Keyword("TREELIST", (str(cycle),)) for cycle in range(1, 21)],
        *[Keyword("ATRTLIST", (str(cycle),)) for cycle in CYCLES],
        *thinning,
        Keyword("PROCESS"),
        Keyword("STOP"),
    ]


def main() -> None:
    """Run the AU multi-entry curves."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--au-table", type=Path, required=True)
    parser.add_argument("--matches", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--regime", choices=sorted(REGIMES), default="GWM_MODERATE")
    args = parser.parse_args()

    au = pd.read_csv(args.au_table).set_index("au_id")
    matches = pd.read_csv(args.matches)
    panel = pd.read_csv(args.panel)
    panel["bec"] = panel.apply(_bec_variant, axis=1)
    panel = panel.set_index(["CLSTR_ID", "VISIT_NUMBER"])
    trees = pd.read_csv(
        args.raw_dir / "faib_tree_detail.csv",
        usecols=[
            "CLSTR_ID",
            "VISIT_NUMBER",
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
        (trees["LV_D"] == "L")
        & (trees["CLSTR_ID"].isin(set(matches["CLSTR_ID"])))
        & trees["DBH"].notna()
        & trees["PHF_TREE"].notna()
    ].copy()

    run_root = args.out_dir / f"multi_{args.regime.lower()}_runs"
    if run_root.exists():
        shutil.rmtree(run_root)
    run_root.mkdir(parents=True)
    rows: list[dict[str, object]] = []
    plot_rows: list[dict[str, object]] = []
    for au_id, group in matches.groupby("au_id"):
        au_row = au.loc[au_id]
        cases = []
        for match in group.itertuples(index=False):
            key = (match.CLSTR_ID, int(match.VISIT_NUMBER))
            if key not in panel.index:
                continue
            state = panel.loc[key]
            if isinstance(state, pd.DataFrame):
                state = state.iloc[0]
            state = state.copy()
            state["CLSTR_ID"] = key[0]
            state["VISIT_NUMBER"] = key[1]
            records = _records(state, trees)
            if not records:
                continue
            result = run_case(
                records,
                _keywords(float(au_row.site_index_median), args.regime),
                directory=run_root / f"{au_id}__{match.CLSTR_ID}",
            )
            summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
            summary = summary[summary["CaseID"] == result.provenance.case_id]
            tree_list = read_table(result.database, "FVS_TreeList_Metric")
            tree_list = tree_list[tree_list["CaseID"] == result.provenance.case_id].copy()
            tree_list["large_ba"] = 0.00007854 * tree_list["DBH"] ** 2 * tree_list["TPH"]
            large = (
                tree_list[tree_list["DBH"] >= 37.5]
                .groupby("Year", as_index=False)
                .agg(large_ba_m2_ha=("large_ba", "sum"), large_tph=("TPH", "sum"))
            )
            summary = summary.merge(large, on="Year", how="left").fillna(
                {"large_ba_m2_ha": 0.0, "large_tph": 0.0}
            )
            try:
                atrt = read_table(result.database, "FVS_ATRTList_Metric")
                atrt = atrt[atrt["CaseID"] == result.provenance.case_id]
            except Exception:
                atrt = pd.DataFrame()
            stage_rows: list[dict[str, object]] = []
            for stage, (_cycle, entry_year) in enumerate(
                zip(CYCLES, ENTRY_YEARS, strict=True), start=1
            ):
                entry = summary[summary["Year"] == entry_year]
                if entry.empty:
                    continue
                entry = entry.iloc[0]
                cut_tph = float(entry["RTph"])
                cut_volume = float(entry["RTCuM"])
                after = atrt[atrt["Year"] == entry_year] if not atrt.empty else pd.DataFrame()
                after_large = 0.0
                if not after.empty:
                    after_large = float(
                        (
                            0.00007854 * after["DBH"] ** 2 * after["TPH"] * (after["DBH"] >= 37.5)
                        ).sum()
                    )
                reserved = _reserved_ids(after, args.regime)
                reserve_ba, reserve_tph = _reserve_metrics(after, reserved)
                residual_metrics = _tree_metrics(after)
                stage_rows.append(
                    {
                        "stage": stage,
                        "year": 0,
                        "ba_m2_ha": float(entry["ATBA"]),
                        "tph": float(entry["Tph"]) - cut_tph,
                        "qmd_cm": float(entry["ATQMD"]),
                        "volume_m3_ha": float(entry["TCuM"]) - cut_volume,
                        "canopy_ccf": float(entry["ATCCF"]),
                        "large_ba_m2_ha": after_large,
                        "large_tph": 0.0,
                        "reserve_ba_m2_ha": reserve_ba,
                        "reserve_tph": reserve_tph,
                        "max_dbh_cm": residual_metrics["max_dbh_cm"],
                        "q_factor": residual_metrics["q_factor"],
                        "cut_tph": cut_tph,
                        "cut_m3_ha": cut_volume,
                    }
                )
                next_year = ENTRY_YEARS[stage] if stage < len(ENTRY_YEARS) else HORIZON_YEARS
                post = summary[(summary["Year"] > entry_year) & (summary["Year"] <= next_year)]
                for point in post.itertuples(index=False):
                    year_trees = tree_list[tree_list["Year"] == int(point.Year)]
                    reserve_ba, reserve_tph = _reserve_metrics(year_trees, reserved)
                    year_metrics = _tree_metrics(year_trees)
                    stage_rows.append(
                        {
                            "stage": stage,
                            "year": int(point.Year - entry_year),
                            "ba_m2_ha": float(point.BA),
                            "tph": float(point.Tph),
                            "qmd_cm": float(point.QMD),
                            "volume_m3_ha": float(point.TCuM),
                            "canopy_ccf": float(point.CCF),
                            "large_ba_m2_ha": float(point.large_ba_m2_ha),
                            "large_tph": float(point.large_tph),
                            "reserve_ba_m2_ha": reserve_ba,
                            "reserve_tph": reserve_tph,
                            "max_dbh_cm": year_metrics["max_dbh_cm"],
                            "q_factor": year_metrics["q_factor"],
                            "cut_tph": 0.0,
                            "cut_m3_ha": 0.0,
                        }
                    )
            if stage_rows:
                stage_frame = pd.DataFrame(stage_rows)
                cases.append(stage_frame)
                for point in stage_frame.itertuples(index=False):
                    plot_rows.append(
                        {
                            "au_id": au_id,
                            "regime": args.regime,
                            "CLSTR_ID": match.CLSTR_ID,
                            "stage": int(point.stage),
                            "year": int(point.year),
                            "ba_m2_ha": float(point.ba_m2_ha),
                            "tph": float(point.tph),
                            "qmd_cm": float(point.qmd_cm),
                            "volume_m3_ha": float(point.volume_m3_ha),
                            "canopy_ccf": float(point.canopy_ccf),
                            "large_ba_m2_ha": float(point.large_ba_m2_ha),
                            "large_tph": float(point.large_tph),
                            "cut_tph": float(point.cut_tph),
                            "cut_m3_ha": float(point.cut_m3_ha),
                        }
                    )
        if not cases:
            raise ValueError(f"no multi-entry FVS cases completed for {au_id}")
        stacked = pd.concat(cases, ignore_index=True)
        aggregations = {
            column: ("max" if column == "max_dbh_cm" else "mean")
            for column in stacked.columns
            if column not in {"stage", "year"}
        }
        mean = stacked.groupby(["stage", "year"], as_index=False).agg(aggregations)
        mean.insert(0, "au_id", au_id)
        mean.insert(1, "si_level", au_row.si_level)
        mean.insert(2, "n_plots", len(cases))
        rows.extend(mean.to_dict(orient="records"))

    curves = pd.DataFrame(rows)
    suffix = (
        "moderate" if args.regime == "GWM_MODERATE" else args.regime.lower().removeprefix("gwm_")
    )
    curves.to_csv(args.out_dir / f"kc_au_multientry_{suffix}_200y.csv", index=False)
    manifest = {
        "au_table": str(args.au_table),
        "matches": str(args.matches),
        "regime": args.regime,
        "horizon_years": HORIZON_YEARS,
        "entries": list(zip(CYCLES, ENTRY_YEARS, strict=True)),
        "aus": int(curves["au_id"].nunique()),
        "curve_rows": len(curves),
        "caveats": [
            "Six entries, then residual growth to 200 years.",
            "Residual x=0 uses ATBA, ATQMD, ATCCF and pre-cut minus removed TPH/volume.",
            "No calibration or legal-compliance claim.",
        ],
    }
    pd.DataFrame(plot_rows).to_csv(
        args.out_dir / f"kc_au_multientry_{suffix}_plot_states.csv", index=False
    )
    (args.out_dir / f"multientry_{suffix}_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
