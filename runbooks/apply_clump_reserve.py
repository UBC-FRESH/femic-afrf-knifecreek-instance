#!/usr/bin/env python3
"""Apply a clump-reserve marking rule to the GWM retain-above-D pilot.

FVS cannot protect individual reserve trees. This script starts from the
after-treatment tree list of the GWM retain-above-D runs, groups trees >=37.5 cm
into DBH-ranked chunks of six (a non-spatial clump proxy), reserves the largest
three trees above D in each chunk, and removes the remaining trees above D.

The result is a retrospective marking scenario, not a new FVS growth run and
not a legal-compliance test. The rank-based clump proxy is replaced by a
spatial clump when KC stem maps exist.

Usage::

    PYTHONPATH=/path/to/fresh-fvsbc/src \
      python runbooks/apply_clump_reserve.py \
      --runtime-dir runtime/gwm_pilot_v0 \
      --out-dir ws4/gwm_pilot_v0
"""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
from fresh_fvsbc.outputs import UnknownTableError, read_table

REGIMES = {
    "GWM_HIGH": {"B": 29.0, "large_ba": 16.0, "D": 70.0, "q": (1.20, 1.35)},
    "GWM_MODERATE": {"B": 22.0, "large_ba": 11.0, "D": 60.0, "q": (1.25, 1.35)},
    "GWM_LOW": {"B": 16.0, "large_ba": 6.0, "D": 50.0, "q": (1.25, 1.40)},
}
LARGE_THRESHOLD = 37.5
CLUMP_SIZE = 6
RESERVE_TREES = 3


def _q_factor(rows: pd.DataFrame) -> float:
    """Return the median q-factor from 5 cm TPH classes."""
    if rows.empty:
        return float("nan")
    classes = (rows["DBH"] // 5 * 5 + 2.5).astype(float)
    density = rows.assign(dbh_class=classes).groupby("dbh_class")["TPH"].sum()
    all_classes = np.arange(classes.min(), classes.max() + 5.0, 5.0)
    density = density.reindex(all_classes, fill_value=0.0)
    ratios = []
    for lower, upper in itertools.pairwise(all_classes):
        if density.loc[lower] > 0 and density.loc[upper] > 0:
            ratios.append(float(density.loc[lower] / density.loc[upper]))
    return float(np.median(ratios)) if ratios else float("nan")


def _apply(after: pd.DataFrame, regime: str) -> tuple[pd.DataFrame, dict[str, float]]:
    """Return the kept tree list and marking metrics for one case."""
    spec = REGIMES[regime]
    large = after[after["DBH"] >= LARGE_THRESHOLD].sort_values("DBH", ascending=False)
    harvest_indices: set[int] = set()
    reserved_indices: set[int] = set()
    for start in range(0, len(large), CLUMP_SIZE):
        chunk = large.iloc[start : start + CLUMP_SIZE]
        above_d = chunk[chunk["DBH"] > spec["D"]]
        reserved_indices.update(above_d.head(RESERVE_TREES).index)
        harvest_indices.update(above_d.iloc[RESERVE_TREES:].index)
    kept = after[~after.index.isin(harvest_indices)].copy()
    kept_ba = float(kept["ba"].sum())
    kept_large = kept[kept["DBH"] >= LARGE_THRESHOLD]
    reserve = kept[kept["DBH"] > spec["D"]]
    q_lo, q_hi = spec["q"]
    q_factor = _q_factor(kept)
    metrics = {
        "post_ba_m2_ha": kept_ba,
        "post_large_ba_m2_ha": float(kept_large["ba"].sum()),
        "post_large_tph": float(kept_large["TPH"].sum()),
        "post_max_dbh_cm": float(kept["DBH"].max()) if len(kept) else np.nan,
        "post_q_factor": q_factor,
        "reserve_ba_m2_ha": float(reserve["ba"].sum()),
        "reserved_trees": float(len(reserved_indices)),
        "harvested_trees": float(len(harvest_indices)),
        "removed_large_ba_m2_ha": float(after["ba"].sum() - kept_ba),
        "removed_large_tph": float(
            after.loc[list(harvest_indices), "TPH"].sum() if harvest_indices else 0.0
        ),
        "total_ba_ok": bool(kept_ba >= spec["B"]),
        "large_ba_ok": bool(float(kept_large["ba"].sum()) >= spec["large_ba"]),
        "max_dbh_ok": bool(float(kept["DBH"].max()) >= spec["D"] if len(kept) else False),
        "q_ok": bool(q_lo <= q_factor <= q_hi),
    }
    metrics["stand_structure_pass"] = all(
        metrics[name] for name in ("total_ba_ok", "large_ba_ok", "max_dbh_ok", "q_ok")
    )
    return kept, metrics


def main() -> None:
    """Apply the clump-reserve proxy and write the result table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for case_dir in sorted(args.runtime_dir.glob("*__retain_above_d")):
        stand, regime, _ = case_dir.name.split("__")
        try:
            atrt = read_table(case_dir / "FVSOut.db", "FVS_ATRTList_Metric")
        except UnknownTableError:
            continue
        after = atrt[atrt["Year"] == 30].copy()
        if after.empty:
            continue
        after["ba"] = 0.00007854 * after["DBH"] ** 2 * after["TPH"]
        _, metrics = _apply(after, regime)
        rows.append(
            {
                "stand": stand,
                "regime": regime,
                "basis": "GWM_2007",
                "clump_proxy": "DBH-ranked chunks of 6",
                "clump_size": CLUMP_SIZE,
                "reserve_trees_per_clump": RESERVE_TREES,
                **metrics,
                "legal_compliance": False,
            }
        )
    out = pd.DataFrame(rows)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out_dir / "clump_reserve.csv", index=False)
    summary = (
        out.groupby("regime")
        .agg(
            n=("stand", "size"),
            mean_post_ba=("post_ba_m2_ha", "mean"),
            mean_large_ba=("post_large_ba_m2_ha", "mean"),
            mean_reserve=("reserve_ba_m2_ha", "mean"),
            mean_q=("post_q_factor", "mean"),
            mean_max_dbh=("post_max_dbh_cm", "mean"),
            mean_removed_ba=("removed_large_ba_m2_ha", "mean"),
            pass_n=("stand_structure_pass", "sum"),
        )
        .reset_index()
    )
    summary.to_csv(args.out_dir / "clump_reserve_summary.csv", index=False)
    print(f"cases={len(out)} pass={int(out['stand_structure_pass'].sum())}/{len(out)}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
