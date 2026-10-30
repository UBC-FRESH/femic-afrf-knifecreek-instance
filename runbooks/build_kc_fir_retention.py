#!/usr/bin/env python3
"""Audit Douglas-fir retention after the first selection entry.

The legal check is retention of at least 80% of pre-harvest merchantable
Douglas-fir BA before 2026.  The model has no calendar-2026 entry, so this
audit uses the FVS year-0 tree list as the pre-entry state and the first
after-treatment tree list (year 30) as the post-entry state.  It is an AU-level
structural proxy, not a spatial retention or legal-compliance determination.

Usage::

    python runbooks/build_kc_fir_retention.py \
      --run-root data/psp/kc_au_200y/multi_gwm_low_runs \
      --out data/psp/kc_au_200y/kc_au_fir_retention_low.csv
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

FIR_SPECIES = {"PSME", "FD", "FDI", "DF"}
BA_FACTOR = 0.00007854


def _ba(frame: pd.DataFrame, fir_only: bool = False) -> float:
    """Return basal area for a tree list, optionally Douglas-fir only."""
    if frame.empty:
        return 0.0
    selected = frame
    if fir_only:
        species = frame["SpeciesPLANTS"].astype(str).str.upper()
        selected = frame[species.isin(FIR_SPECIES)]
    return float((BA_FACTOR * selected["DBH"] ** 2 * selected["TPH"]).sum())


def main() -> None:
    """Write per-plot and per-AU first-entry retention."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--entry-year", type=int, default=30)
    args = parser.parse_args()

    rows = []
    for run_dir in sorted(args.run_root.iterdir()):
        if not run_dir.is_dir() or "__" not in run_dir.name:
            continue
        au_id, plot_id = run_dir.name.split("__", 1)
        database = run_dir / "FVSOut.db"
        if not database.exists():
            continue
        with sqlite3.connect(database) as connection:
            trees = pd.read_sql("SELECT * FROM FVS_TreeList_Metric WHERE Year = 0", connection)
            after = pd.read_sql(
                "SELECT * FROM FVS_ATRTList_Metric WHERE Year = ?",
                connection,
                params=(args.entry_year,),
            )
        if trees.empty or after.empty:
            continue
        initial_fir = _ba(trees, fir_only=True)
        post_fir = _ba(after, fir_only=True)
        rows.append(
            {
                "au_id": au_id,
                "plot_id": plot_id,
                "initial_ba_m2_ha": _ba(trees),
                "post_ba_m2_ha": _ba(after),
                "initial_fir_ba_m2_ha": initial_fir,
                "post_fir_ba_m2_ha": post_fir,
                "fir_retention": post_fir / initial_fir if initial_fir > 0 else float("nan"),
            }
        )
    per_plot = pd.DataFrame(rows)
    if per_plot.empty:
        raise ValueError(f"no usable FVS runs under {args.run_root}")
    summary = (
        per_plot.groupby("au_id", as_index=False)
        .agg(
            n_plots=("plot_id", "size"),
            initial_fir_ba_m2_ha=("initial_fir_ba_m2_ha", "sum"),
            post_fir_ba_m2_ha=("post_fir_ba_m2_ha", "sum"),
            mean_plot_retention=("fir_retention", "mean"),
            min_plot_retention=("fir_retention", "min"),
        )
        .assign(
            pooled_retention=lambda frame: (
                frame["post_fir_ba_m2_ha"] / frame["initial_fir_ba_m2_ha"]
            ),
            meets_80pct=lambda frame: frame["pooled_retention"] >= 0.8,
        )
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.out, index=False)
    per_plot.to_csv(args.out.with_name(args.out.stem + "_plots.csv"), index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
