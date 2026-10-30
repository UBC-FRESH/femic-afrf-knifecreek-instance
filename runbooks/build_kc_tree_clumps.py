#!/usr/bin/env python3
"""Empirical clump baseline from the eight Marshal tree maps.

This is the ground-truth comparison for the LiDAR clump proxy.  Trees are
grouped when their stem centres are within a spacing threshold; the resulting
groups are summarized by size and DBH threshold.

Outputs are private and live in the DataLad store.

Usage::

    python runbooks/build_kc_tree_clumps.py \
      --trees external/ubc-research-forests-data/processed/kc_spatial/kc_marshal_trees.parquet \
      --out external/ubc-research-forests-data/processed/kc_spatial/kc_marshal_tree_clumps.csv
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


def _clusters(points: np.ndarray, spacing_m: float) -> list[list[int]]:
    """Single-linkage clusters of points within spacing_m."""
    parent = list(range(len(points)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for left in range(len(points)):
        for right in range(left + 1, len(points)):
            dx = points[left, 0] - points[right, 0]
            dy = points[left, 1] - points[right, 1]
            if dx * dx + dy * dy <= spacing_m * spacing_m:
                union(left, right)
    groups: dict[int, list[int]] = defaultdict(list)
    for index in range(len(points)):
        groups[find(index)].append(index)
    return list(groups.values())


def main() -> None:
    """Write clump-size distributions for alternative spacing thresholds."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    trees = pd.read_parquet(args.trees)
    trees = trees[trees.source_plot.isin(range(1, 9))]
    rows = []
    for plot, group in trees.groupby("source_plot"):
        for spacing in (2.0, 3.0, 5.0):
            for min_dbh in (0.0, 10.0, 15.0, 20.0):
                subset = group[group.dbh_cm >= min_dbh]
                points = subset[["utm_e", "utm_n"]].to_numpy()
                groups = _clusters(points, spacing) if len(points) else []
                sizes = [len(cluster) for cluster in groups]
                legal = [size for size in sizes if 4 <= size <= 10]
                rows.append(
                    {
                        "source_plot": int(plot),
                        "spacing_m": spacing,
                        "min_dbh_cm": min_dbh,
                        "n_trees": len(subset),
                        "clump_count": len(sizes),
                        "mean_clump_size": float(np.mean(sizes)) if sizes else np.nan,
                        "max_clump_size": int(max(sizes)) if sizes else 0,
                        "clump_4_10": len(legal),
                        "clump_gt10": sum(size > 10 for size in sizes),
                        "trees_in_4_10": sum(legal),
                    }
                )
    result = pd.DataFrame(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out, index=False)
    print(result[(result.spacing_m == 3.0) & (result.min_dbh_cm == 10.0)].to_string(index=False))


if __name__ == "__main__":
    main()
