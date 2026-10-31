#!/usr/bin/env python3
"""Calibrate 2013 LAS tree detection against the Marshal tree maps.

The 2013 point cloud is closer in time to the tree maps than the 2019 CHM.
This script builds a 1 m canopy-height surface for each mapped plot from the
2013 LAS (max z minus ground/min z), detects local maxima, and scores the
detections against measured DBH >=15 cm trees.

Usage::

    python runbooks/calibrate_kc_lidar_2013.py \
      --las-dir external/.../LiDAR/2013 \
      --trees external/.../processed/kc_spatial/kc_marshal_trees.parquet \
      --plots external/.../processed/kc_spatial/kc_marshal_plots.gpkg \
      --out-dir external/.../processed/kc_spatial
"""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import laspy
import numpy as np
import pandas as pd
from rasterio.transform import Affine
from scipy import ndimage
from scipy.spatial import cKDTree
from shapely import contains_xy
from shapely.geometry.base import BaseGeometry


def _las_files(las_dir: Path, bounds: tuple[float, float, float, float]) -> list[Path]:
    """Return LAS tiles whose header bounds intersect a plot envelope."""
    minx, miny, maxx, maxy = bounds
    selected = []
    for path in sorted(las_dir.glob("*.las")):
        try:
            with laspy.open(path) as reader:
                header = reader.header
                tile_minx, tile_miny = header.mins[0], header.mins[1]
                tile_maxx, tile_maxy = header.maxs[0], header.maxs[1]
        except Exception:
            continue
        if tile_maxx < minx or tile_minx > maxx or tile_maxy < miny or tile_miny > maxy:
            continue
        selected.append(path)
    return selected


def _canopy_grid(polygon: BaseGeometry, las_dir: Path) -> tuple[np.ndarray, Affine]:
    """Build a 1 m canopy-height grid for one plot polygon."""
    minx, miny, maxx, maxy = polygon.bounds
    width = int(np.ceil(maxx - minx))
    height = int(np.ceil(maxy - miny))
    max_grid = np.full((height, width), -np.inf, dtype=float)
    min_grid = np.full((height, width), np.inf, dtype=float)
    ground_grid = np.full((height, width), np.inf, dtype=float)
    for path in _las_files(las_dir, polygon.bounds):
        cloud = laspy.read(path)
        x = np.asarray(cloud.x)
        y = np.asarray(cloud.y)
        z = np.asarray(cloud.z)
        classification = np.asarray(cloud.classification)
        inside = contains_xy(polygon, x, y)
        x, y, z = x[inside], y[inside], z[inside]
        classification = classification[inside]
        if len(x) == 0:
            continue
        columns = np.floor(x - minx).astype(int)
        rows = np.floor(maxy - y).astype(int)
        valid = (columns >= 0) & (columns < width) & (rows >= 0) & (rows < height)
        rows, columns, z, classification = (
            rows[valid],
            columns[valid],
            z[valid],
            classification[valid],
        )
        np.maximum.at(max_grid, (rows, columns), z)
        np.minimum.at(min_grid, (rows, columns), z)
        ground = classification == 2
        if ground.any():
            np.minimum.at(ground_grid, (rows[ground], columns[ground]), z[ground])
    ground = np.where(np.isfinite(ground_grid), ground_grid, min_grid)
    with np.errstate(invalid="ignore"):
        canopy = max_grid - ground
    canopy[~np.isfinite(canopy)] = np.nan
    return canopy, Affine(1.0, 0.0, minx, 0.0, -1.0, maxy)


def _detect_peaks(
    values: np.ndarray,
    transform: Affine,
    window: int,
    minimum_height: float,
    nms_radius_m: float,
) -> np.ndarray:
    """Return NMS-filtered local maxima in map coordinates."""
    valid = np.isfinite(values) & (values >= minimum_height) & (values < 200)
    peaks = (values == ndimage.maximum_filter(values, size=window)) & valid
    labels, count = ndimage.label(peaks, structure=np.ones((3, 3)))
    centers = ndimage.center_of_mass(peaks, labels, range(1, count + 1))
    candidates = []
    for row, column in centers:
        x, y = transform * (column + 0.5, row + 0.5)
        candidates.append((x, y, float(values[int(row), int(column)])))
    candidates.sort(key=lambda item: item[2], reverse=True)
    kept = []
    for x, y, height in candidates:
        if all((x - kx) ** 2 + (y - ky) ** 2 > nms_radius_m**2 for kx, ky, _ in kept):
            kept.append((x, y, height))
    return np.array([(x, y) for x, y, _ in kept], dtype=float)


def _f1(
    detected: np.ndarray, observed: np.ndarray, tolerance: float = 3.0
) -> tuple[float, float, float]:
    """Precision, recall and F1 with mutual nearest matching."""
    if len(detected) == 0 or len(observed) == 0:
        return 0.0, 0.0, 0.0
    distance, index = cKDTree(observed).query(detected, distance_upper_bound=tolerance)
    matched = np.isfinite(distance)
    precision = float(matched.mean())
    recall = len(set(index[matched].tolist())) / len(observed)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def main() -> None:
    """Calibrate 2013 LAS detection parameters."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--las-dir", type=Path, required=True)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--plots", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    trees = pd.read_parquet(args.trees)
    trees = trees[(trees.source_plot.isin(range(1, 9))) & (trees.dbh_cm >= 15.0)]
    tree_points = gpd.GeoDataFrame(
        trees,
        geometry=gpd.points_from_xy(trees.utm_e, trees.utm_n),
        crs=26910,
    )
    plots = gpd.read_file(args.plots).to_crs(26910)
    plots["PLOT_ID"] = pd.to_numeric(plots.PLOT_ID, errors="coerce").astype(int)
    rows = []
    for plot_id, group in tree_points.groupby("source_plot"):
        polygon = plots.loc[int(plot_id) == plots.PLOT_ID].geometry.iloc[0]
        canopy, transform = _canopy_grid(polygon, args.las_dir)
        observed = np.array([(point.x, point.y) for point in group.geometry])
        print(
            f"plot {plot_id}: trees={len(observed)} grid={canopy.shape} "
            f"valid={int(np.isfinite(canopy).sum())}",
            flush=True,
        )
        for window in (3, 5, 7, 9):
            for minimum_height in (3.0, 5.0, 8.0, 10.0):
                for nms_radius in (1.5, 2.5, 3.5):
                    detected = _detect_peaks(canopy, transform, window, minimum_height, nms_radius)
                    precision, recall, f1 = _f1(detected, observed)
                    rows.append(
                        {
                            "source_plot": int(plot_id),
                            "window": window,
                            "minimum_height_m": minimum_height,
                            "nms_radius_m": nms_radius,
                            "observed_dbh15": len(observed),
                            "detected": len(detected),
                            "precision": precision,
                            "recall": recall,
                            "f1": f1,
                        }
                    )
    result = pd.DataFrame(rows)
    summary = (
        result.groupby(["window", "minimum_height_m", "nms_radius_m"], as_index=False)
        .agg(
            mean_f1=("f1", "mean"),
            mean_precision=("precision", "mean"),
            mean_recall=("recall", "mean"),
            mean_detected=("detected", "mean"),
            mean_observed=("observed_dbh15", "mean"),
        )
        .sort_values("mean_f1", ascending=False)
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out_dir / "kc_lidar_2013_calibration.csv", index=False)
    summary.to_csv(args.out_dir / "kc_lidar_2013_calibration_summary.csv", index=False)
    print(summary.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
