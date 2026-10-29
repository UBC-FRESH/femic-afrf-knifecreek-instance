#!/usr/bin/env python3
"""Run a first FVS-BC backtest against the AFRF Knife Creek PSP plots.

Initialises each plot from the 1993 interior-tree measurement, expands each
tree by 20 (0.05 ha), and grows it without cutting to the 1997/2004/2008/2013
measurements. This is a structural validation, not a calibrated KC model.

The site index (FD 60) and tree age (100) are placeholders until better plot
metadata or KC calibration are available.

Usage::

    python runbooks/fvs_validate_afrf_kc_psp.py \
      --trees data/private/afrf_kc_psp/trees_long.parquet \
      --observed data/psp/kc_afrf_psp_plot_summary.csv \
      --out-dir ws4/kc_psp_validation \
      --runtime-dir runtime/kc_psp_validation
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

YEARS = (1993, 1997, 2004, 2008, 2013)
INTERVALS = (4, 7, 4, 5)
AREA_HA = 0.05


def _record(
    row: pd.Series,
    *,
    plot_id: int,
    tree_num: int,
    tree_age: float,
) -> dict[str, object]:
    """Build one FVS tree record with a 20x expansion factor."""
    height = row["height_m"]
    if not np.isfinite(height) or height <= 1.3:
        height = 1.3 + 0.5 * float(row["dbh_cm"])
    crown = row["crown_ratio"]
    if not np.isfinite(crown):
        crown = 0.5
    crown = float(np.clip(crown, 0.05, 0.85))
    species = str(row["species"]).strip().upper()
    species = {"SX": "SE", "W": "OH"}.get(species, species)
    return {
        "plot_id": plot_id,
        "tree_num": tree_num,
        "tree_count": 1.0 / AREA_HA,
        "tree_history": 0,
        "species": resolve_species(species),
        "diam": float(row["dbh_cm"]),
        "dg_incr": 0.0,
        "live_ht": float(height),
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
        "tree_age": tree_age,
    }


def _keywords(
    plot: int,
    mortality_multiplier: float | None = None,
    site_index: float = 60.0,
) -> list[Keyword]:
    """Build a no-cut 20-year FVS key set."""
    return [
        Keyword(
            "DATABASE",
            (),
            ("DSNOut", "FVSOut.db", "TreeLIDB", "CutLIDB", "ATRTLIDB", "Summary"),
        ),
        Keyword("STDIDENT", (f"KC PSP PLOT {plot}",)),
        Keyword("STDINFO", ("712", "CHS131", "0", "200", "35", "16")),
        Keyword("MANAGED", ("0", "1")),
        Keyword("SITECODE", ("FD", str(site_index))),
        Keyword("INVYEAR", ("1993",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        *(
            Keyword("TIMEINT", (str(cycle), str(interval)))
            for cycle, interval in enumerate(INTERVALS, start=1)
        ),
        Keyword("NUMCYCLE", (str(len(INTERVALS)),)),
        Keyword("RANNSEED", ("1",)),
        *(
            [Keyword("MORTMULT", ("1", "0", str(mortality_multiplier), "0", "999"))]
            if mortality_multiplier is not None
            else []
        ),
        Keyword("TREELIST", (str(len(INTERVALS)),)),
        Keyword("PROCESS"),
        Keyword("STOP"),
    ]


def main() -> None:
    """Run every plot and write observed/predicted validation tables."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--observed", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--tree-age", type=float, default=100.0)
    parser.add_argument("--mortality-multiplier", type=float)
    parser.add_argument("--site-index", type=float, default=60.0)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.runtime_dir.mkdir(parents=True, exist_ok=True)
    trees = pd.read_csv(args.trees)
    initial = trees[
        (trees["year"] == 1993) & (trees["position"] == "I") & trees["dbh_cm"].notna()
    ].copy()
    observed = pd.read_csv(args.observed)
    predicted = []
    runs = []
    for plot, group in initial.groupby("plot"):
        records = [
            _record(row, plot_id=int(plot), tree_num=index + 1, tree_age=args.tree_age)
            for index, (_, row) in enumerate(group.iterrows())
        ]
        case_dir = args.runtime_dir / f"plot_{int(plot):02d}"
        if case_dir.exists():
            shutil.rmtree(case_dir)
        result = run_case(
            records,
            _keywords(int(plot), args.mortality_multiplier, args.site_index),
            directory=case_dir,
        )
        summary = read_table(result.database, "FVS_Summary_Metric")
        summary = summary[summary["CaseID"] == result.provenance.case_id].sort_values("Year")
        for row in summary.itertuples(index=False):
            predicted.append(
                {
                    "plot": int(plot),
                    "year": int(row.Year),
                    "pred_ba_m2_ha": float(row.BA),
                    "pred_tph": float(row.Tph),
                    "pred_qmd_cm": float(row.QMD),
                    "pred_top_height_m": float(row.TopHt),
                    "pred_ccf": float(row.CCF),
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
    pred = pd.DataFrame(predicted)
    pred.to_csv(args.out_dir / "fvs_predictions.csv", index=False)
    joined = observed.merge(pred, on=["plot", "year"], how="inner")
    joined["ba_error"] = joined["pred_ba_m2_ha"] - joined["ba_m2_ha"]
    joined["qmd_error"] = joined["pred_qmd_cm"] - joined["qmd_cm"]
    joined["tph_error"] = joined["pred_tph"] - joined["tph"]
    joined.to_csv(args.out_dir / "validation.csv", index=False)
    summary = (
        joined.groupby("year")
        .agg(
            n=("plot", "size"),
            obs_ba=("ba_m2_ha", "mean"),
            pred_ba=("pred_ba_m2_ha", "mean"),
            ba_bias=("ba_error", "mean"),
            ba_mae=("ba_error", lambda values: float(np.abs(values).mean())),
            obs_qmd=("qmd_cm", "mean"),
            pred_qmd=("pred_qmd_cm", "mean"),
            qmd_bias=("qmd_error", "mean"),
            obs_tph=("tph", "mean"),
            pred_tph=("pred_tph", "mean"),
            tph_bias=("tph_error", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(args.out_dir / "validation_summary.csv", index=False)
    manifest = {
        "validation": "afrf-kc-psp-fvs-backtest-v1",
        "status": "structural-placeholder",
        "plots": int(initial["plot"].nunique()),
        "initial_year": 1993,
        "years": list(YEARS),
        "area_ha": AREA_HA,
        "tree_age": args.tree_age,
        "mortality_multiplier": args.mortality_multiplier,
        "site_index": {"species": "FD", "value": args.site_index},
        "runs": runs,
        "caveats": [
            "Tree age and site index are placeholders.",
            "No KC calibration; species are mapped to BC codes.",
            "Initial population uses only interior trees with 1993 DBH.",
            "Height is filled from DBH when 1993 height is missing.",
            "FVS-BC is distance-independent and no cut is applied.",
            "The 24-plot thinning experiment is not a whole-block sample.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
