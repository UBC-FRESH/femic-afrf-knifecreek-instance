#!/usr/bin/env python3
"""Build a multi-tile LidarBC canopy inventory clipped to a boundary.

Processes every 2024 DEM/DSM pair in a directory, detects local-maximum canopy
trees, clips to the boundary, merges overlaps and summarizes spatial clumps.

This is a canopy-tree inventory, not a CFI. DBH is height-allometry only.

Usage::

    python runbooks/lidar_inventory_all_tiles.py \
      --dem-dir data/lidar/raw/2024 \
      --boundary data/boundaries/knife_creek_sup_S15382.gpkg \
      --allometry data/psp/idf_cariboo_psp_conditional_stemlists.csv \
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
import rasterio
from rasterio.features import geometry_mask
from scipy.ndimage import center_of_mass, gaussian_filter, label, maximum_filter
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


def _clumps(trees: gpd.GeoDataFrame, area_ha: float) -> pd.DataFrame:
    rows = []
    for threshold in (15, 20, 25):
        subset = trees[trees["height_m"] >= threshold].copy()
        xy = np.column_stack([subset.geometry.x, subset.geometry.y])
        if len(xy) < 2:
            continue
        tree = cKDTree(xy)
        for eps in (5, 10, 15):
            parent = list(range(len(subset)))
            for a, b in tree.query_pairs(eps):
                _union(parent, a, b)
            sizes = list(Counter(_find(parent, i) for i in range(len(subset))).values())
            rows.append(
                {
                    "height_threshold_m": threshold,
                    "eps_m": eps,
                    "large_trees": len(subset),
                    "clumps": len(sizes),
                    "mean_clump_size": float(np.mean(sizes)),
                    "max_clump_size": max(sizes),
                    "clumps_size_2_5": sum(1 for size in sizes if 2 <= size <= 5),
                    "clumps_size_4_10": sum(1 for size in sizes if 4 <= size <= 10),
                    "singletons": sum(1 for size in sizes if size == 1),
                    "clumps_per_ha": len(sizes) / area_ha,
                }
            )
    return pd.DataFrame(rows)


def _trees_from_tile(
    dem_path: Path,
    dsm_path: Path,
    boundary: gpd.GeoDataFrame,
    *,
    min_height: float,
    min_spacing: int,
) -> tuple[list[tuple[float, float, float, float]], float]:
    with rasterio.open(dem_path) as src:
        dem = src.read(1).astype("float32")
        transform = src.transform
        crs = src.crs
        nodata = src.nodata
    with rasterio.open(dsm_path) as src:
        dsm = src.read(1).astype("float32")
    chm = dsm - dem
    valid = (dem != nodata) & (dsm != nodata) & np.isfinite(chm) & (chm >= 0) & (chm < 80)
    local_boundary = boundary.to_crs(crs)
    mask = geometry_mask(
        local_boundary.geometry, out_shape=chm.shape, transform=transform, invert=True
    )
    valid &= mask
    area_ha = float(valid.sum() * abs(transform.a * transform.e) / 10000.0)
    chm = np.where(valid, chm, 0).astype("float32")
    smooth = gaussian_filter(chm, 0.7)
    peaks = (
        (smooth >= maximum_filter(smooth, size=min_spacing) - 1e-6) & (smooth >= min_height) & valid
    )
    labels, count = label(peaks)
    centres = center_of_mass(peaks, labels, range(1, count + 1))
    points = []
    for row, col in centres:
        row_index = round(row)
        col_index = round(col)
        height = float(smooth[row_index, col_index])
        if height < min_height:
            continue
        x, y = rasterio.transform.xy(transform, row_index, col_index, offset="center")
        points.append((x, y, height, 0.0))
    return points, area_ha


def main() -> None:
    """Process all DEM/DSM pairs and write the merged inventory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dem-dir", type=Path, required=True)
    parser.add_argument("--boundary", type=Path, required=True)
    parser.add_argument("--allometry", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--min-height", type=float, default=5.0)
    parser.add_argument("--min-spacing", type=int, default=9)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    boundary = gpd.read_file(args.boundary).to_crs(3005)
    dem_files = sorted(
        path for path in args.dem_dir.glob("*.tif") if not path.stem.endswith("_dsm")
    )
    rows = []
    tile_rows = []
    for dem_path in dem_files:
        dsm_path = dem_path.with_name(f"{dem_path.stem}_dsm.tif")
        if not dsm_path.exists():
            continue
        points, area_ha = _trees_from_tile(
            dem_path,
            dsm_path,
            boundary,
            min_height=args.min_height,
            min_spacing=args.min_spacing,
        )
        if not points:
            continue
        tile_rows.append({"tile": dem_path.stem, "area_ha": area_ha, "trees": len(points)})
        rows.extend(
            {
                "x": x,
                "y": y,
                "height_m": h,
                "tile": dem_path.stem,
            }
            for x, y, h, _ in points
        )
    raw = pd.DataFrame(rows)
    # Tile edges can duplicate the same local maximum. Coordinates are aligned
    # to the same 1 m grid, so exact coordinate duplicates are safe to drop.
    raw = raw.drop_duplicates(["x", "y"]).reset_index(drop=True)
    x = raw[["x", "y"]].to_numpy()
    distances, _ = cKDTree(x).query(x, k=2)
    radii = np.minimum(np.maximum(distances[:, 1] / 2.0, 1.0), 8.0)
    stem = pd.read_csv(args.allometry)
    stem = stem[(stem["species"] == "FD") & (stem["height_m"] > 5)]
    design = np.column_stack([np.ones(len(stem)), np.log(stem["height_m"])])
    intercept, slope = np.linalg.lstsq(design, np.log(stem["dbh_cm"]), rcond=None)[0]
    heights = raw["height_m"].to_numpy()
    trees = gpd.GeoDataFrame(
        {
            "tree_id": range(1, len(raw) + 1),
            "x": raw["x"],
            "y": raw["y"],
            "height_m": heights,
            "crown_radius_m": radii,
            "dbh_cm_est": np.exp(intercept + slope * np.log(heights)),
            "species": "UNK",
            "tile": raw["tile"],
        },
        geometry=gpd.points_from_xy(raw["x"], raw["y"]),
        crs=3005,
    )
    trees.to_file(args.out_dir / "trees.gpkg", driver="GPKG")
    trees.drop(columns="geometry").to_csv(args.out_dir / "trees.csv", index=False)
    tile_summary = pd.DataFrame(tile_rows)
    tile_summary.to_csv(args.out_dir / "tile_summary.csv", index=False)
    # Use the boundary area for clump density; not every tile covers the SUP.
    area_ha = float(boundary.to_crs(3005).area.sum() / 10000.0)
    clumps = _clumps(trees, area_ha)
    clumps.to_csv(args.out_dir / "clump_analysis.csv", index=False)
    summary = {
        "tiles_processed": len(tile_summary),
        "area_ha": area_ha,
        "trees": len(trees),
        "tph": len(trees) / area_ha,
        "height_m": {
            "mean": float(heights.mean()),
            "p50": float(np.median(heights)),
            "p95": float(np.percentile(heights, 95)),
            "max": float(heights.max()),
        },
        "crown_radius_m": {
            "mean": float(radii.mean()),
            "p50": float(np.median(radii)),
            "max": float(radii.max()),
        },
        "dbh_cm_est": {
            "mean": float(trees["dbh_cm_est"].mean()),
            "p50": float(trees["dbh_cm_est"].median()),
            "max": float(trees["dbh_cm_est"].max()),
        },
        "large_trees_ge20m": int((heights >= 20).sum()),
        "allometry_log_dbh": {"intercept": float(intercept), "slope": float(slope)},
        "caveats": [
            "Canopy tree inventory, not a CFI: no species, understory or measured DBH.",
            "DBH is height-allometry only; do not use for BA calibration.",
            "1 m DSM local maxima can split crowns.",
            "Tiles are merged by exact coordinate; edge duplicates may remain if grids differ.",
        ],
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
