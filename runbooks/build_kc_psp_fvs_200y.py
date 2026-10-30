#!/usr/bin/env python3
"""Run 200-year no-cut FVS-BC curves for the KC PSP plots.

This uses the private KC PSP tree tallies to build one initial population per
plot, then runs FVS-BC for 200 years. Only derived plot-level curves are written
to ``data/psp``; the raw tree tallies remain under ``data/private``.

The site index and breast-height age are structural placeholders. This is not a
KC calibration.

Usage::

    python runbooks/build_kc_psp_fvs_200y.py \
      --trees data/private/afrf_kc_psp/trees_long.parquet \
      --out data/psp/kc_afrf_psp_fvs_200y_curves.csv \
      --runtime runtime/fvsbc/kc_psp_200y
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.nemora import crown_class
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import resolve_species

TREE_AGE = 60.0
SITE_INDEX = 60
HORIZON_YEARS = 200
STEP_YEARS = 10


def _records(plot: pd.DataFrame, plot_id: int, tree_count: float) -> list[dict[str, object]]:
    """Build FVS tree-list records from one plot's first measurement."""
    records: list[dict[str, object]] = []
    for number, row in enumerate(plot.itertuples(index=False), start=1):
        try:
            species = resolve_species(str(row.species))
        except Exception:
            species = "OH"
        crown = float(row.crown_ratio) if pd.notna(row.crown_ratio) else 0.5
        crown = min(max(crown, 0.05), 0.85)
        height = float(row.height_m) if pd.notna(row.height_m) else 1.3 + 0.5 * float(row.dbh_cm)
        records.append(
            {
                "plot_id": plot_id,
                "tree_num": number,
                "tree_count": float(tree_count),
                "tree_history": 0,
                "species": species,
                "diam": float(row.dbh_cm),
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
                "tree_age": TREE_AGE,
            }
        )
    return records


def _keywords(plot_id: int) -> list[Keyword]:
    """Return a 200-year no-cut FVS-BC key set."""
    return [
        Keyword(
            "DATABASE",
            (),
            ("DSNOut", "FVSOut.db", "Summary"),
        ),
        Keyword("STDIDENT", (f"KC-PSP-PLOT-{plot_id}-200Y",)),
        Keyword("STDINFO", ("712", "CHS131", "0", str(HORIZON_YEARS), "35", "16")),
        Keyword("MANAGED", ("0", "1")),
        Keyword("SITECODE", ("FD", str(SITE_INDEX))),
        Keyword("INVYEAR", ("0",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", str(STEP_YEARS))),
        Keyword("NUMCYCLE", (str(HORIZON_YEARS // STEP_YEARS),)),
        Keyword("RANNSEED", ("1",)),
        Keyword("PROCESS"),
        Keyword("STOP"),
    ]


def main() -> None:
    """Run every KC PSP plot and write the 200-year curve table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    trees = pd.read_parquet(args.trees)
    args.runtime.mkdir(parents=True, exist_ok=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    runs: list[dict[str, object]] = []
    for plot_id in sorted(trees["plot"].unique()):
        first_year = int(trees.loc[trees["plot"] == plot_id, "year"].min())
        plot = trees[
            (trees["plot"] == plot_id)
            & (trees["year"] == first_year)
            & (trees["status"] == 1)
            & (trees["position"] == "I")
            & trees["dbh_cm"].notna()
            & trees["height_m"].notna()
        ].copy()
        if plot.empty:
            continue
        area_ha = 0.05
        tree_count = 1.0 / area_ha
        records = _records(plot, int(plot_id), tree_count)
        run_dir = args.runtime / f"plot_{int(plot_id):02d}_{first_year}"
        if run_dir.exists():
            if not args.overwrite:
                raise FileExistsError(f"{run_dir} exists; pass --overwrite")
            import shutil

            shutil.rmtree(run_dir)
        result = run_case(records, _keywords(int(plot_id)), directory=run_dir)
        summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
        summary = summary[summary["CaseID"] == result.provenance.case_id]
        for point in summary.itertuples(index=False):
            rows.append(
                {
                    "plot": int(plot_id),
                    "block": str(plot["block"].iloc[0]),
                    "treatment": str(plot["treatment"].iloc[0]),
                    "first_year": first_year,
                    "tree_age": TREE_AGE,
                    "site_index": SITE_INDEX,
                    "year": int(point.Year),
                    "ba_m2_ha": float(point.BA),
                    "tph": float(point.Tph),
                    "qmd_cm": float(point.QMD),
                    "volume_m3_ha": float(point.TCuM),
                    "canopy_ccf": float(point.CCF),
                    "case_id": result.provenance.case_id,
                }
            )
        runs.append(
            {
                "plot": int(plot_id),
                "first_year": first_year,
                "trees": len(records),
                "case_id": result.provenance.case_id,
            }
        )
        print(f"plot {plot_id}: {len(records)} trees, {len(summary)} summary rows", flush=True)

    frame = pd.DataFrame(rows)
    frame.to_csv(args.out, index=False)
    manifest = {
        "source": "KC PSP first-measurement live trees",
        "raw_source": str(args.trees),
        "plots": len(runs),
        "horizon_years": HORIZON_YEARS,
        "step_years": STEP_YEARS,
        "tree_age": TREE_AGE,
        "site_index": SITE_INDEX,
        "fvs": "fresh-fvsbc 0.20.0 / FVS-BC",
        "columns": list(frame.columns),
        "runs": runs,
        "caveats": [
            "No-cut FVS-BC projections, not observed growth.",
            "Tree age 60 and site index 60 are structural placeholders.",
            "No KC calibration is claimed.",
            "Raw tree tallies remain private; this is a derived plot curve table.",
        ],
    }
    args.out.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {len(frame)} curve rows for {len(runs)} plots")


if __name__ == "__main__":
    main()
