#!/usr/bin/env python3
"""Derive plot-level LiDAR clump and opening proxies.

This is a first-pass geometry proxy, not the legal spatial clump layout:

- tree tops are local maxima in the 2019 canopy-height grid;
- tops within 3 m are grouped into a clump;
- clumps of 4-10 tops are flagged;
- canopy gaps are connected components below 2 m.

The output is private and lives in the DataLad store.

Usage::

    python runbooks/build_kc_lidar_clumps.py \
      --plots external/ubc-research-forests-data/processed/kc_spatial/kc_marshal_plots.gpkg \
      --chm path/to/ubc_chm/w001001.adf \
      --out external/ubc-research-forests-data/processed/kc_spatial/kc_marshal_lidar_clumps.csv
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask
from rasterio.transform import Affine
from scipy import ndimage


def _cluster_peaks(points: list[tuple[float, float]], radius_m: float) -> list[list[int]]:
    """Single-linkage clusters of peak coordinates within radius_m."""
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

    for left, (x1, y1) in enumerate(points):
        for right in range(left + 1, len(points)):
            x2, y2 = points[right]
            if (x1 - x2) ** 2 + (y1 - y2) ** 2 <= radius_m**2:
                union(left, right)
    groups: dict[int, list[int]] = defaultdict(list)
    for index in range(len(points)):
        groups[find(index)].append(index)
    return list(groups.values())


def _detect_peaks(
    values: np.ndarray,
    transform: Affine,
    window: int,
    minimum_height: float,
    nms_radius_m: float,
) -> list[tuple[float, float]]:
    """Return local-maxima canopy points after non-maximum suppression."""
    valid = np.isfinite(values) & (values >= minimum_height) & (values < 200)
    peaks = (values == ndimage.maximum_filter(values, size=window)) & valid
    labels, count = ndimage.label(peaks, structure=np.ones((3, 3)))
    centers = ndimage.center_of_mass(peaks, labels, range(1, count + 1))
    candidates = []
    for row, col in centers:
        x, y = transform * (col + 0.5, row + 0.5)
        candidates.append((x, y, float(values[int(row), int(col)])))
    candidates.sort(key=lambda item: item[2], reverse=True)
    kept = []
    for x, y, height in candidates:
        if all((x - kx) ** 2 + (y - ky) ** 2 > nms_radius_m**2 for kx, ky, _ in kept):
            kept.append((x, y, height))
    return [(x, y) for x, y, _ in kept]


def _plot_metrics(
    plot_id: int,
    values: np.ndarray,
    transform: Affine,
    window: int,
    minimum_height: float,
    nms_radius_m: float,
    clump_radius_m: float,
) -> dict[str, object]:
    """Compute clump and opening proxies from one masked CHM array."""
    valid = np.isfinite(values) & (values >= 0) & (values < 200)
    points = _detect_peaks(values, transform, window, minimum_height, nms_radius_m)
    clumps = _cluster_peaks(points, radius_m=clump_radius_m)
    sizes = [len(group) for group in clumps]
    legal = [size for size in sizes if 4 <= size <= 10]

    gap_mask = valid & (values < 2.0)
    gap_labels, gap_count = ndimage.label(gap_mask, structure=np.ones((3, 3)))
    gap_areas = np.bincount(gap_labels.ravel())[1:] * abs(transform.a * transform.e)
    gap_areas = gap_areas[gap_areas > 0]

    return {
        "plot_id": plot_id,
        "detected_tree_tops": len(points),
        "clump_count": len(clumps),
        "mean_clump_size": float(np.mean(sizes)) if sizes else np.nan,
        "clump_4_10_fraction": float(len(legal) / len(sizes)) if sizes else np.nan,
        "max_clump_size": int(max(sizes)) if sizes else 0,
        "gap_component_count": int(gap_count),
        "largest_gap_m2": float(gap_areas.max()) if gap_areas.size else 0.0,
        "mean_gap_m2": float(gap_areas.mean()) if gap_areas.size else 0.0,
        "mean_height_m": float(values[valid].mean()) if valid.any() else np.nan,
    }


def main() -> None:
    """Write the plot clump/opening proxy table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plots", type=Path, required=True)
    parser.add_argument("--chm", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--window", type=int, default=5)
    parser.add_argument("--min-height", type=float, default=5.0)
    parser.add_argument("--nms-radius", type=float, default=1.5)
    parser.add_argument("--clump-radius", type=float, default=3.0)
    args = parser.parse_args()
    plots = gpd.read_file(args.plots)
    rows = []
    with rasterio.open(args.chm) as source:
        plots = plots.to_crs(source.crs)
        for row in plots.itertuples(index=False):
            values, _ = mask(source, [row.geometry], crop=True, filled=False)
            array = values[0].astype(float).filled(np.nan)
            rows.append(
                _plot_metrics(
                    int(row.PLOT_ID),
                    array,
                    source.transform,
                    args.window,
                    args.min_height,
                    args.nms_radius,
                    args.clump_radius,
                )
            )
    result = pd.DataFrame(rows).sort_values("plot_id")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out, index=False)
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
