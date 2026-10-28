#!/usr/bin/env python3
"""Assign a spatial clump-reserve scenario from the LidarBC tree inventory.

For each VRI block, mature trees (height >=20 m) are connected at 10 m. Each
4-10-tree clump reserves its three largest trees; trees above 10 per component
are split into 10-tree chunks by height. Components smaller than four trees are
left intact.

This is a spatial canopy reserve scenario. It does not apply the legal D floor
or infer species/understory; DBH is height-allometry only.

Usage::

    python runbooks/lidar_reserve_scenario.py \
      --trees data/lidar/kc_2024/trees.parquet \
      --vri data/inventory/vri_2025_kc.gpkg \
      --sup data/boundaries/knife_creek_sup_S15382.gpkg \
      --out-dir data/lidar/kc_2024
"""

from __future__ import annotations

import argparse
import json
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


def _components(xy: np.ndarray, eps: float = 10.0) -> list[list[int]]:
    parent = list(range(len(xy)))
    for a, b in cKDTree(xy).query_pairs(eps):
        _union(parent, a, b)
    groups: dict[int, list[int]] = {}
    for index in range(len(xy)):
        groups.setdefault(_find(parent, index), []).append(index)
    return list(groups.values())


def main() -> None:
    """Write reserve-tree assignments and block summaries."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--vri", type=Path, required=True)
    parser.add_argument("--sup", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--reserve-trees", type=int, default=3)
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
        blocks[["POLYGON_ID", "area_ha", "geometry"]],
        how="inner",
        predicate="within",
    )
    assignments = []
    summaries = []
    for block in blocks.itertuples(index=False):
        subset = joined[joined["POLYGON_ID"] == block.POLYGON_ID].copy()
        large = subset[subset["height_m"] >= 20.0].copy()
        large = large.sort_values(["height_m", "dbh_cm_est"], ascending=False)
        clump_id = 0
        reserve_indices = set()
        harvest_indices = set()
        if len(large):
            xy = np.column_stack([large.geometry.x, large.geometry.y])
            for component in _components(xy):
                members = large.iloc[component]
                # Split very large components into 10-tree chunks by height.
                chunks = [members.iloc[start : start + 10] for start in range(0, len(members), 10)]
                for chunk in chunks:
                    clump_id += 1
                    take = len(chunk) if len(chunk) < 4 else min(args.reserve_trees, len(chunk))
                    reserve_indices.update(chunk.head(take).index)
                    harvest_indices.update(chunk.iloc[take:].index)
        reserve = subset.loc[list(reserve_indices)] if reserve_indices else subset.iloc[0:0]
        harvest = subset.loc[list(harvest_indices)] if harvest_indices else subset.iloc[0:0]
        for frame, role in ((reserve, "reserve"), (harvest, "harvest")):
            for row in frame.itertuples(index=False):
                assignments.append(
                    {
                        "tree_id": int(row.tree_id),
                        "block_id": int(block.POLYGON_ID),
                        "role": role,
                        "height_m": float(row.height_m),
                        "dbh_cm_est": float(row.dbh_cm_est),
                        "crown_radius_m": float(row.crown_radius_m),
                        "x": float(row.geometry.x),
                        "y": float(row.geometry.y),
                    }
                )
        area_ha = float(block.area_ha)
        reserve_ba = float((0.00007854 * reserve["dbh_cm_est"] ** 2).sum()) if len(reserve) else 0.0
        harvest_ba = float((0.00007854 * harvest["dbh_cm_est"] ** 2).sum()) if len(harvest) else 0.0
        summaries.append(
            {
                "POLYGON_ID": int(block.POLYGON_ID),
                "area_ha": area_ha,
                "large_trees": len(large),
                "clumps": int(clump_id),
                "reserve_trees": len(reserve),
                "harvest_trees": len(harvest),
                "reserve_tph": float(len(reserve) / area_ha),
                "harvest_tph": float(len(harvest) / area_ha),
                "reserve_ba_est_m2_ha": reserve_ba / area_ha,
                "harvest_ba_est_m2_ha": harvest_ba / area_ha,
                "reserve_share_pct": float(len(reserve) / len(large) * 100) if len(large) else 0.0,
            }
        )
    pd.DataFrame(assignments).to_parquet(args.out_dir / "reserve_trees.parquet", index=False)
    summary = pd.DataFrame(summaries)
    summary.to_csv(args.out_dir / "block_reserve_summary.csv", index=False)
    total_area = float(summary["area_ha"].sum())
    meta = {
        "blocks": len(summary),
        "area_ha": total_area,
        "large_trees": int(summary["large_trees"].sum()),
        "clumps": int(summary["clumps"].sum()),
        "reserve_trees": int(summary["reserve_trees"].sum()),
        "harvest_trees": int(summary["harvest_trees"].sum()),
        "reserve_tph_mean": float(summary["reserve_tph"].mean()),
        "harvest_tph_mean": float(summary["harvest_tph"].mean()),
        "reserve_ba_mean_m2_ha": float(summary["reserve_ba_est_m2_ha"].mean()),
        "caveats": [
            "Spatial reserve scenario only; not a legal D-floor check.",
            "Mature tree proxy is height >=20 m; DBH is height-allometry only.",
            "No species, understory, damage or mortality.",
            "Components >10 trees are split into 10-tree height-ranked chunks.",
            "Small components (<4 trees) are left intact.",
        ],
    }
    (args.out_dir / "reserve_summary.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
