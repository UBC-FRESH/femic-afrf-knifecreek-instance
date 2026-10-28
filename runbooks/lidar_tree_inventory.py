#!/usr/bin/env python3
"""Build a canopy-tree inventory and clump summary from LidarBC DEM/DSM.

The input is a LidarBC 1 m DEM and DSM pair. The CHM is DSM - DEM, clipped to a
boundary. Trees are local maxima on a smoothed CHM, with a minimum spacing and
height threshold. DBH is a height-allometry estimate; species and understory are
unknown. This is a canopy inventory, not a CFI.

Usage::

    python runbooks/lidar_tree_inventory.py \
      --dem data/lidar/raw/kc_dem_093a001_2_4_3.tif \
      --dsm data/lidar/raw/kc_dsm_093a001_2_4_3.tif \
      --boundary data/boundaries/knife_creek_sup_S15382.gpkg \
      --allometry data/psp/idf_cariboo_psp_conditional_stemlists.csv \
      --out-dir data/lidar/pilot_093a001_2_4_3
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


def _clump_summary(trees: gpd.GeoDataFrame, area_ha: float) -> pd.DataFrame:
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


def main() -> None:
    """Write tree inventory, summary and clump table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dem", type=Path, required=True)
    parser.add_argument("--dsm", type=Path, required=True)
    parser.add_argument("--boundary", type=Path, required=True)
    parser.add_argument("--allometry", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--min-height", type=float, default=5.0)
    parser.add_argument("--min-spacing", type=int, default=9)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with rasterio.open(args.dem) as src:
        dem = src.read(1).astype("float32")
        transform = src.transform
        crs = src.crs
        nodata = src.nodata
    with rasterio.open(args.dsm) as src:
        dsm = src.read(1).astype("float32")
    chm = dsm - dem
    valid = (dem != nodata) & (dsm != nodata) & np.isfinite(chm) & (chm >= 0) & (chm < 80)
    boundary = gpd.read_file(args.boundary).to_crs(crs)
    mask = geometry_mask(boundary.geometry, out_shape=chm.shape, transform=transform, invert=True)
    valid &= mask
    chm = np.where(valid, chm, 0).astype("float32")
    with rasterio.open(
        args.out_dir / "chm.tif",
        "w",
        driver="GTiff",
        height=chm.shape[0],
        width=chm.shape[1],
        count=1,
        dtype="float32",
        crs=crs,
        transform=transform,
        nodata=0,
    ) as dst:
        dst.write(chm, 1)

    smooth = gaussian_filter(chm, 0.7)
    peaks = (
        (smooth >= maximum_filter(smooth, size=args.min_spacing) - 1e-6)
        & (smooth >= args.min_height)
        & valid
    )
    labels, count = label(peaks)
    centres = center_of_mass(peaks, labels, range(1, count + 1))
    points = []
    for row, col in centres:
        row_index = round(row)
        col_index = round(col)
        height = float(smooth[row_index, col_index])
        if height < args.min_height:
            continue
        x, y = rasterio.transform.xy(transform, row_index, col_index, offset="center")
        points.append((x, y, height))
    xy = np.array([(x, y) for x, y, _ in points])
    distances, _ = cKDTree(xy).query(xy, k=2)
    radii = np.minimum(np.maximum(distances[:, 1] / 2.0, 1.0), 8.0)
    heights = np.array([height for _, _, height in points])
    stem = pd.read_csv(args.allometry)
    stem = stem[(stem["species"] == "FD") & (stem["height_m"] > 5)]
    design = np.column_stack([np.ones(len(stem)), np.log(stem["height_m"])])
    intercept, slope = np.linalg.lstsq(design, np.log(stem["dbh_cm"]), rcond=None)[0]
    dbh = np.exp(intercept + slope * np.log(heights))
    trees = gpd.GeoDataFrame(
        {
            "tree_id": range(1, len(points) + 1),
            "x": [x for x, _, _ in points],
            "y": [y for _, y, _ in points],
            "height_m": heights,
            "crown_radius_m": radii,
            "dbh_cm_est": dbh,
            "species": "UNK",
            "source": f"LidarBC CHM DSM-DEM, maximum_filter {args.min_spacing}",
        },
        geometry=gpd.points_from_xy([x for x, _, _ in points], [y for _, y, _ in points]),
        crs=crs,
    )
    trees.to_file(args.out_dir / "trees.gpkg", driver="GPKG")
    trees.drop(columns="geometry").to_csv(args.out_dir / "trees.csv", index=False)
    area_ha = float(valid.sum() * abs(transform.a * transform.e) / 10000.0)
    clumps = _clump_summary(trees, area_ha)
    clumps.to_csv(args.out_dir / "clump_analysis.csv", index=False)
    summary = {
        "tile": args.dem.stem,
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
            "mean": float(dbh.mean()),
            "p50": float(np.median(dbh)),
            "max": float(dbh.max()),
        },
        "large_trees_ge20m": int((heights >= 20).sum()),
        "allometry_log_dbh": {"intercept": float(intercept), "slope": float(slope)},
        "caveats": [
            "Canopy tree inventory, not a CFI: no species, understory or measured DBH.",
            "DBH is height-allometry from PSP conditional FD trees; not a BA calibration.",
            (
                "1 m DSM local maxima can split crowns; minimum spacing reduces "
                "but does not eliminate over-segmentation."
            ),
        ],
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
