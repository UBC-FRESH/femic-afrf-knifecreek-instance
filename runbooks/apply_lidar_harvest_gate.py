#!/usr/bin/env python3
"""Apply a block-level LiDAR harvest gate to a GWM schedule.

Blocks whose LiDAR reserve scenario has no harvest trees are removed. This is
a block-level gate, not a replacement for the FVS clump-reserve proxy.

Usage::

    python runbooks/apply_lidar_harvest_gate.py \
      --schedule /tmp/knife_gwm_schedule.csv \
      --block-features ws4/dataset_kc_spatial_v5/block_features.csv \
      --out /tmp/knife_gwm_lidar_schedule.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _as_float(value: object) -> float:
    """Return a float from a pandas scalar."""
    return float(str(value))


def apply_gate(schedule: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
    """Return schedule rows for blocks with at least one LiDAR harvest tree."""
    if len(features) != 160:
        raise ValueError(f"expected 160 block features, found {len(features)}")
    allowed = {
        index + 1
        for index, row in enumerate(features.itertuples(index=False))
        if _as_float(row.harvest_tph) > 0.0
    }
    return schedule[schedule["block_id"].isin(allowed)].copy()


def main() -> None:
    """Filter a schedule and write the result."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--block-features", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    schedule = pd.read_csv(args.schedule)
    features = pd.read_csv(args.block_features)
    gated = apply_gate(schedule, features)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    gated.to_csv(args.out, index=False)
    print(
        f"scheduled_blocks={gated['block_id'].nunique()} "
        f"events={len(gated)} "
        f"removed_blocks={schedule['block_id'].nunique() - gated['block_id'].nunique()}"
    )


if __name__ == "__main__":
    main()
