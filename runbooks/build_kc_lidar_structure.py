#!/usr/bin/env python3
"""Derive canopy structure metrics for the Marshal plot polygons.

The 2019 UBC canopy grid is an ArcInfo grid with an integer sentinel.  This
script masks the sentinel, reprojects the 24 plot polygons to the grid CRS, and
summarizes canopy height, cover and gap fraction inside each plot.

Outputs are private and live in the DataLad store.

Usage::

    python runbooks/build_kc_lidar_structure.py \
      --plots external/ubc-research-forests-data/processed/kc_spatial/kc_marshal_plots.gpkg \
      --chm path/to/ubc_chm/w001001.adf \
      --out path/to/kc_marshal_lidar_structure.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask


def _stats(plot_id: int, values: np.ndarray) -> dict[str, object]:
    """Summarize one plot's valid canopy-height pixels."""
    valid = values[np.isfinite(values)]
    valid = valid[(valid >= 0) & (valid < 200)]
    if valid.size == 0:
        return {
            "plot_id": plot_id,
            "valid_pixels": 0,
            "mean_height_m": np.nan,
            "median_height_m": np.nan,
            "p90_height_m": np.nan,
            "p95_height_m": np.nan,
            "max_height_m": np.nan,
            "cover_2m": np.nan,
            "cover_5m": np.nan,
            "gap_2m": np.nan,
        }
    return {
        "plot_id": plot_id,
        "valid_pixels": int(valid.size),
        "mean_height_m": float(valid.mean()),
        "median_height_m": float(np.median(valid)),
        "p90_height_m": float(np.percentile(valid, 90)),
        "p95_height_m": float(np.percentile(valid, 95)),
        "max_height_m": float(valid.max()),
        "cover_2m": float((valid >= 2).mean()),
        "cover_5m": float((valid >= 5).mean()),
        "gap_2m": float((valid < 2).mean()),
    }


def main() -> None:
    """Write plot-level 2019 canopy metrics."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plots", type=Path, required=True)
    parser.add_argument("--chm", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    plots = gpd.read_file(args.plots)
    with rasterio.open(args.chm) as source:
        plots = plots.to_crs(source.crs)
        rows = []
        for row in plots.itertuples(index=False):
            geometry = row.geometry
            try:
                values, _ = mask(source, [geometry], crop=True, filled=False)
                array = values[0].astype(float).filled(np.nan)
            except Exception:
                array = np.array([np.nan])
            rows.append(_stats(int(row.PLOT_ID), array))
    summary = pd.DataFrame(rows).sort_values("plot_id")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.out, index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
