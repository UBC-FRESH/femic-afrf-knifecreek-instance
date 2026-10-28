#!/usr/bin/env python3
"""Derive block-level canopy and clump features from the LidarBC inventory.

The output is a VRI-polygon crosswalk with tree density, estimated BA and the
10 m-linkage clump metrics for trees >=20 m. It is a canopy feature table, not
a CFI or a growth calibration.

Usage::

    python runbooks/lidar_block_features.py \
      --trees data/lidar/kc_2024/trees.parquet \
      --vri data/inventory/vri_2025_kc.gpkg \
      --sup data/boundaries/knife_creek_sup_S15382.gpkg \
      --out-dir data/lidar/kc_2024
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


def _find(parent: list[int], node: int) -> int:
    while parent[node] != node:
        parent[node] = parent[parent[node]]
        node = parent[node]
    return node


def _union(parent: list[int], a: int, b: int) -> None:
    root_a, root_b = _find(parent, a), _find(parent, b)
    if root_a != root_b:
        parent[root_b] = root_a


def _clump_metrics(xy: np.ndarray, area_ha: float) -> dict[str, float]:
    if len(xy) < 2:
        return {
            "large_clumps": 0.0,
            "large_mean_clump_size": 0.0,
            "large_clumps_4_10": 0.0,
            "large_singletons": float(len(xy)),
            "large_clumps_per_ha": 0.0,
            "large_trees_in_4_10": 0.0,
        }
    parent = list(range(len(xy)))
    for a, b in cKDTree(xy).query_pairs(10.0):
        _union(parent, a, b)
    groups = Counter(_find(parent, i) for i in range(len(xy)))
    sizes = list(groups.values())
    in_4_10 = sum(size for size in sizes if 4 <= size <= 10)
    return {
        "large_clumps": float(len(sizes)),
        "large_mean_clump_size": float(np.mean(sizes)),
        "large_clumps_4_10": float(sum(1 for size in sizes if 4 <= size <= 10)),
        "large_singletons": float(sum(1 for size in sizes if size == 1)),
        "large_clumps_per_ha": float(len(sizes) / area_ha) if area_ha > 0 else 0.0,
        "large_trees_in_4_10": float(in_4_10),
    }


def main() -> None:
    """Write the block-level LiDAR feature table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--vri", type=Path, required=True)
    parser.add_argument("--sup", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    trees = pd.read_parquet(args.trees)
    tree_gdf = gpd.GeoDataFrame(
        trees,
        geometry=gpd.points_from_xy(trees["x"], trees["y"]),
        crs=6653,
    ).to_crs(3005)
    vri = gpd.read_file(args.vri).to_crs(3005)
    sup = gpd.read_file(args.sup).to_crs(3005)
    blocks = gpd.overlay(vri, sup[["geometry"]], how="intersection")
    blocks["area_ha"] = blocks.geometry.area / 10000.0
    blocks = blocks[
        (blocks["area_ha"] >= 0.1)
        & (blocks["BASAL_AREA"].fillna(0) > 0)
        & (blocks["VRI_LIVE_STEMS_PER_HA"].fillna(0) > 0)
    ].copy()
    joined = gpd.sjoin(
        tree_gdf,
        blocks[["POLYGON_ID", "geometry"]],
        how="inner",
        predicate="within",
    )
    rows = []
    for row in blocks.itertuples(index=False):
        subset = joined[joined["POLYGON_ID"] == row.POLYGON_ID]
        area_ha = float(row.area_ha)
        large = subset[subset["height_m"] >= 20.0]
        xy = np.column_stack([large.geometry.x, large.geometry.y])
        metrics = _clump_metrics(xy, area_ha)
        ba = float((0.00007854 * subset["dbh_cm_est"] ** 2).sum()) if len(subset) else 0.0
        large_ba = float((0.00007854 * large["dbh_cm_est"] ** 2).sum()) if len(large) else 0.0
        rows.append(
            {
                "POLYGON_ID": row.POLYGON_ID,
                "area_ha": area_ha,
                "lidar_coverage": bool(len(subset) > 0),
                "trees": len(subset),
                "tph": len(subset) / area_ha,
                "large_trees_ge20": len(large),
                "large_tph_ge20": len(large) / area_ha,
                "ba_est_m2_ha": ba / area_ha,
                "large_ba_est_m2_ha": large_ba / area_ha,
                **metrics,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(args.out_dir / "block_tree_summary.csv", index=False)
    covered = out[out["lidar_coverage"]]
    summary = {
        "blocks": len(out),
        "blocks_with_lidar": int(out["lidar_coverage"].sum()),
        "area_ha": float(out["area_ha"].sum()),
        "covered_area_ha": float(covered["area_ha"].sum()),
        "mean_tph": float(covered["tph"].mean()),
        "mean_large_tph": float(covered["large_tph_ge20"].mean()),
        "mean_clumps_4_10_per_ha": float(covered["large_clumps_per_ha"].mean()),
        "total_clumps_4_10": int(covered["large_clumps_4_10"].sum()),
        "caveats": [
            "LiDAR canopy features only; no species, understory or measured DBH.",
            "DBH and BA are height-allometry estimates, not calibration targets.",
            "Clumps use 10 m linkage for trees >=20 m within each VRI polygon.",
            "Polygon-edge clumps can be split across block boundaries.",
        ],
    }
    (args.out_dir / "block_tree_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
