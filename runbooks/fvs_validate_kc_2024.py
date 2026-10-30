#!/usr/bin/env python3
"""Backtest the 2013-calibrated FVS-BC parameters against 2024/2025.

The v1 calibration was fitted to the 2013 measurements.  This script starts
from the 2013 interior tree list, runs one no-cut interval to each plot's
2024/2025 remeasurement year, and compares predicted BA/TPH/QMD with the new
observed summary.  It is a temporal out-of-sample diagnostic, not a
whole-block validation or a legal-compliance claim.

Usage::

    python runbooks/fvs_validate_kc_2024.py \
      --trees data/private/afrf_kc_psp/trees_long.csv \
      --observed data/psp/kc_afrf_psp_plot_summary_2024.csv \
      --parameters ws4/kc_psp_calibration/calibration_parameters.json \
      --out-dir ws4/kc_psp_validation_2024 \
      --runtime-dir runtime/kc_psp_validation_2024
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import pandas as pd
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fvs_validate_afrf_kc_psp import _record

INTERVAL_START = 2013
TREE_AGE = 0.0
STAND_AGE = 0.0


def _keywords(
    plot: int,
    interval: int,
    ba_multipliers: dict[str, float] | None = None,
    mort_multipliers: dict[str, float] | None = None,
) -> list[Keyword]:
    """Build a one-interval no-cut FVS key set."""
    return [
        Keyword(
            "DATABASE",
            (),
            ("DSNOut", "FVSOut.db", "TreeLIDB", "CutLIDB", "ATRTLIDB", "Summary"),
        ),
        Keyword("STDIDENT", (f"KC PSP 2024 PLOT {plot}",)),
        Keyword("STDINFO", ("712", "CHS131", str(round(STAND_AGE)), str(interval), "35", "16")),
        Keyword("MANAGED", ("0", "1")),
        Keyword("INVYEAR", (str(INTERVAL_START),)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("1", str(interval))),
        Keyword("NUMCYCLE", ("1",)),
        Keyword("RANNSEED", ("1",)),
        *(
            [
                Keyword("BAIMULT", ("1", species, f"{multiplier:.4f}"))
                for species, multiplier in (ba_multipliers or {}).items()
            ]
        ),
        *(
            [
                Keyword("MORTMULT", ("1", species, f"{multiplier:.4f}", "0", "999"))
                for species, multiplier in (mort_multipliers or {}).items()
            ]
        ),
        Keyword("TREELIST", ("1",)),
        Keyword("PROCESS"),
        Keyword("STOP"),
    ]


def _expand(values: dict[str, float]) -> dict[str, float]:
    """Expand species-group values to individual FVS species codes."""
    groups = {"FD": ("FD",), "SE": ("SE",), "PL": ("PL",), "HW": ("EP", "AT", "OH")}
    return {
        species: float(values[group])
        for group, species_plan in groups.items()
        for species in species_plan
    }


def _run_set(
    initial: pd.DataFrame,
    observed: pd.DataFrame,
    *,
    label: str,
    ba: dict[str, float] | None,
    mort: dict[str, float] | None,
    runtime_dir: Path,
) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    """Run every plot for one parameter set."""
    rows = []
    runs = []
    end_years = observed.set_index("plot")["end_year"].to_dict()
    for plot, group in initial.groupby("plot"):
        end_year = int(end_years[int(plot)])
        interval = end_year - INTERVAL_START
        case_dir = runtime_dir / f"{label}" / f"plot_{int(plot):02d}"
        if case_dir.exists():
            shutil.rmtree(case_dir)
        records = [
            _record(row, plot_id=int(plot), tree_num=index + 1, tree_age=TREE_AGE)
            for index, (_, row) in enumerate(group.iterrows())
        ]
        result = run_case(
            records,
            _keywords(
                int(plot),
                interval,
                _expand(ba) if ba else None,
                _expand(mort) if mort else None,
            ),
            directory=case_dir,
        )
        summary = read_table(result.database, "FVS_Summary_Metric")
        summary = summary[summary["CaseID"] == result.provenance.case_id]
        final = summary[summary["Year"] == end_year]
        if final.empty:
            raise ValueError(f"missing FVS summary at year {end_year} for plot {plot}")
        point = final.iloc[0]
        rows.append(
            {
                "plot": int(plot),
                "start_year": INTERVAL_START,
                "end_year": end_year,
                "years": interval,
                "pred_ba_m2_ha": float(point["BA"]),
                "pred_tph": float(point["Tph"]),
                "pred_qmd_cm": float(point["QMD"]),
                "pred_ccf": float(point["CCF"]),
            }
        )
        runs.append(
            {
                "plot": int(plot),
                "case_id": result.provenance.case_id,
                "keyword_hash": result.provenance.keyword_set_hash,
                "treelist_hash": result.provenance.treelist_hash,
            }
        )
    return pd.DataFrame(rows), runs


def _evaluate(predicted: pd.DataFrame, observed: pd.DataFrame) -> pd.DataFrame:
    """Join predictions to observations and add residuals."""
    joined = observed.merge(predicted, on=["plot", "end_year", "years"], how="inner")
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
    """Run the calibrated and uncalibrated 2013->2024 backtests."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--observed", type=Path, required=True)
    parser.add_argument("--parameters", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    args = parser.parse_args()

    trees = pd.read_csv(args.trees)
    initial = trees[
        (trees["year"] == INTERVAL_START) & (trees["position"] == "I") & trees["dbh_cm"].notna()
    ].copy()
    observed = pd.read_csv(args.observed)
    observed = observed[observed["plot"].isin(initial["plot"].unique())].copy()
    observed = observed.rename(columns={"year": "end_year"})
    observed["years"] = observed["end_year"] - INTERVAL_START
    parameters = json.loads(args.parameters.read_text())
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.runtime_dir.mkdir(parents=True, exist_ok=True)

    uncal_pred, uncal_runs = _run_set(
        initial,
        observed,
        label="uncalibrated",
        ba=None,
        mort=None,
        runtime_dir=args.runtime_dir,
    )
    cal_pred, cal_runs = _run_set(
        initial,
        observed,
        label="calibrated",
        ba=parameters["ba_multiplier"],
        mort=parameters["mortality_multiplier"],
        runtime_dir=args.runtime_dir,
    )
    uncal = _evaluate(uncal_pred, observed)
    cal = _evaluate(cal_pred, observed)
    uncal.to_csv(args.out_dir / "validation_uncalibrated.csv", index=False)
    cal.to_csv(args.out_dir / "validation_calibrated.csv", index=False)
    _summary(uncal).to_csv(args.out_dir / "summary_uncalibrated.csv", index=False)
    _summary(cal).to_csv(args.out_dir / "summary_calibrated.csv", index=False)
    manifest = {
        "validation": "afrf-kc-psp-2024-backtest-v1",
        "status": "temporal-out-of-sample-diagnostic",
        "start_year": INTERVAL_START,
        "plots": int(observed["plot"].nunique()),
        "end_years": observed["end_year"].value_counts().to_dict(),
        "parameters": str(args.parameters),
        "calibrated_runs": cal_runs,
        "uncalibrated_runs": uncal_runs,
        "caveats": [
            "The calibration was fitted to 2013 on these same plots; 2024 is a "
            "temporal holdout, not an independent site holdout.",
            "No cutting is simulated.",
            "No stand age or site index is assigned.",
            "The 24-plot thinning experiment is not a whole-block sample.",
            "Not a legal-compliance or production-growth claim.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("uncalibrated")
    print(_summary(uncal).to_string(index=False))
    print("calibrated")
    print(_summary(cal).to_string(index=False))


if __name__ == "__main__":
    main()
