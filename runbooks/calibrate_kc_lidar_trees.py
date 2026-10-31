#!/usr/bin/env python3
"""Calibrate 2019 CHM tree detection against the Marshal tree maps.

The objective is not perfect individual-tree reconstruction. It is to choose a
defensible local-maxima parameter set for canopy trees and clumps, using the
eight georeferenced tree maps as ground truth.

Outputs are private and live in the DataLad store.

Usage::

    python runbooks/calibrate_kc_lidar_trees.py \
      --trees external/ubc-research-forests-data/processed/kc_spatial/kc_marshal_trees.parquet \
      --plots external/ubc-research-forests-data/processed/kc_spatial/kc_marshal_plots.gpkg \
      --chm path/to/ubc_chm/w001001.adf \
      --out-dir external/ubc-research-forests-data/processed/kc_spatial
"""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask
from rasterio.transform import Affine
from scipy import ndimage
from scipy.spatial import cKDTree


def _detect_peaks(
    values: np.ndarray,
    transform: Affine,
    *,
    window: int,
    minimum_height: float,
    nms_radius_m: float,
) -> np.ndarray:
    """Return NMS-filtered local-maxima coordinates in map units."""
    valid = np.isfinite(values) & (values >= minimum_height) & (values < 200)
    maxima = values == ndimage.maximum_filter(values, size=window)
    candidate = valid & maxima
    labels, count = ndimage.label(candidate, structure=np.ones((3, 3)))
    centers = ndimage.center_of_mass(candidate, labels, range(1, count + 1))
    points = []
    for row, column in centers:
        x, y = transform * (column + 0.5, row + 0.5)
        points.append((x, y, float(values[int(row), int(column)])))
    points.sort(key=lambda item: item[2], reverse=True)
    kept = []
    for x, y, height in points:
        if all((x - kx) ** 2 + (y - ky) ** 2 > nms_radius_m**2 for kx, ky, _ in kept):
            kept.append((x, y, height))
    return np.array([(x, y) for x, y, _ in kept], dtype=float)


def _match(
    detected: np.ndarray, observed: np.ndarray, tolerance_m: float
) -> tuple[float, float, float]:
    """Return precision, recall and F1 using mutual nearest matching."""
    if len(detected) == 0 or len(observed) == 0:
        return 0.0, 0.0, 0.0
    distance, index = cKDTree(observed).query(detected, distance_upper_bound=tolerance_m)
    matched = np.isfinite(distance)
    precision = float(matched.mean())
    matched_observed = len(set(index[matched].tolist()))
    recall = matched_observed / len(observed)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def main() -> None:
    """Tune detection parameters and write the calibration table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--plots", type=Path, required=True)
    parser.add_argument("--chm", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    trees = pd.read_parquet(args.trees)
    trees = trees[trees.source_plot.isin(range(1, 9))]
    plots = gpd.read_file(args.plots)
    plots["PLOT_ID"] = pd.to_numeric(plots.PLOT_ID, errors="coerce").astype(int)
    target_trees = trees[trees.dbh_cm >= 15.0].copy()
    points = gpd.GeoDataFrame(
        target_trees,
        geometry=gpd.points_from_xy(target_trees.utm_e, target_trees.utm_n),
        crs=26910,
    )
    rows = []
    with rasterio.open(args.chm) as source:
        points = points.to_crs(source.crs)
        for plot_id, group in points.groupby("source_plot"):
            polygon = plots.loc[int(plot_id) == plots.PLOT_ID].geometry.iloc[0]
            values, out_transform = mask(source, [polygon], crop=True, filled=False)
            array = values[0].astype(float).filled(np.nan)
            observed = np.array([(p.x, p.y) for p in group.geometry])
            for window in (3, 5, 7, 9):
                for minimum_height in (3.0, 5.0, 8.0, 10.0):
                    for nms_radius in (1.5, 2.5, 3.5):
                        detected = _detect_peaks(
                            array,
                            out_transform,
                            window=window,
                            minimum_height=minimum_height,
                            nms_radius_m=nms_radius,
                        )
                        precision, recall, f1 = _match(detected, observed, 3.0)
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
    result.to_csv(args.out_dir / "kc_lidar_tree_calibration.csv", index=False)
    summary.to_csv(args.out_dir / "kc_lidar_tree_calibration_summary.csv", index=False)
    print(summary.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
