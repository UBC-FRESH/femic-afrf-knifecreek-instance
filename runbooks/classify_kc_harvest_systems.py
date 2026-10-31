#!/usr/bin/env python3
"""Classify Knife Creek blocks by slope and candidate harvest system.

The 2007 management plan says ground-based systems dominate, cable systems are
expected where a substantial area exceeds 30% slope, and areas above 60% slope
are generally inaccessible. This runbook measures those fractions from the
2024 LidarBC 1 m DEM and records a screening class. It is not a field
operability determination.

Usage::

    python runbooks/classify_kc_harvest_systems.py \
      --blocks data/patchworks_knifecreek/spatial_split/fragments.shp \
      --dem-dir data/lidar/raw/2024 \
      --out-dir data/harvest_systems
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.merge import merge
from scipy.ndimage import distance_transform_edt, uniform_filter

NODATA = -32767.0
SLOPE_30 = 30.0
SLOPE_60 = 60.0


def _slope_percent(dem: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Return slope percent after filling small voids and smoothing the DEM."""
    if not valid.any():
        return np.full(dem.shape, np.nan, dtype=np.float32)
    indices = distance_transform_edt(~valid, return_distances=False, return_indices=True)
    filled = dem[tuple(indices)].astype(np.float32)
    smoothed = uniform_filter(filled, size=3, mode="nearest")
    gradient_y, gradient_x = np.gradient(smoothed, 1.0, 1.0)
    slope = np.sqrt(gradient_x**2 + gradient_y**2) * 100.0
    slope[~valid] = np.nan
    return slope.astype(np.float32)


def main() -> None:
    """Measure slope fractions and write the candidate harvest-system table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--blocks",
        type=Path,
        default=Path("data/patchworks_knifecreek/spatial_split/fragments.shp"),
    )
    parser.add_argument("--dem-dir", type=Path, default=Path("data/lidar/raw/2024"))
    parser.add_argument("--out-dir", type=Path, default=Path("data/harvest_systems"))
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    blocks = gpd.read_file(args.blocks)
    if "BLOCK" not in blocks.columns:
        raise SystemExit("blocks must carry a BLOCK column")
    blocks = blocks[["BLOCK", "AREA_HA", "geometry"]].copy()
    blocks["block_id"] = blocks["BLOCK"].astype(int)
    max_id = int(blocks["block_id"].max())
    blocks_metric = blocks.to_crs(6653)

    dem_paths = sorted(
        path for path in glob.glob(str(args.dem_dir / "*.tif")) if not path.endswith("_dsm.tif")
    )
    if not dem_paths:
        raise SystemExit(f"no DEM tiles in {args.dem_dir}")

    bounds = tuple(blocks_metric.total_bounds)
    datasets = []
    for path in dem_paths:
        dataset = rasterio.open(path)
        tile = dataset.bounds
        if (
            tile.left < bounds[2]
            and tile.right > bounds[0]
            and tile.bottom < bounds[3]
            and tile.top > bounds[1]
        ):
            datasets.append(dataset)
        else:
            dataset.close()
    try:
        dem_array, transform = merge(
            datasets,
            bounds=bounds,
            res=1.0,
            nodata=NODATA,
            dtype="float32",
        )
    finally:
        for dataset in datasets:
            dataset.close()
    dem = dem_array[0].astype(np.float32)
    valid = np.isfinite(dem) & (dem != NODATA)
    slope = _slope_percent(dem, valid)
    shapes = (
        (geom, int(block_id))
        for geom, block_id in zip(blocks_metric.geometry, blocks_metric["block_id"], strict=True)
    )
    ids = rasterize(
        shapes,
        out_shape=dem.shape,
        transform=transform,
        fill=0,
        dtype=np.int32,
    )
    mask = valid & (ids > 0) & np.isfinite(slope)
    valid_count = np.bincount(ids[mask], minlength=max_id + 1)
    flat_slope = slope[mask]
    gt30_count = np.bincount(ids[mask][flat_slope > SLOPE_30], minlength=max_id + 1)
    gt60_count = np.bincount(ids[mask][flat_slope > SLOPE_60], minlength=max_id + 1)
    slope_sum = np.bincount(ids[mask], weights=flat_slope, minlength=max_id + 1)
    tile_count = len(dem_paths)

    pixel_area_ha = 1.0 / 10_000.0
    rows: list[dict[str, object]] = []
    for _, block in blocks.iterrows():
        block_id = int(block["block_id"])
        count = int(valid_count[block_id])
        if count == 0:
            rows.append(
                {
                    "block_id": block_id,
                    "block_area_ha": float(block["AREA_HA"]),
                    "valid_slope_area_ha": 0.0,
                    "mean_slope_pct": None,
                    "pct_area_gt30": None,
                    "pct_area_gt60": None,
                    "candidate_system": "unknown",
                    "classification_basis": "no valid DEM pixels",
                }
            )
            continue
        pct30 = 100.0 * gt30_count[block_id] / count
        pct60 = 100.0 * gt60_count[block_id] / count
        if pct60 >= 50.0:
            candidate = "inaccessible_candidate"
        elif pct30 >= 50.0:
            candidate = "cable_candidate"
        else:
            candidate = "ground_based_candidate"
        rows.append(
            {
                "block_id": block_id,
                "block_area_ha": float(block["AREA_HA"]),
                "valid_slope_area_ha": count * pixel_area_ha,
                "mean_slope_pct": float(slope_sum[block_id] / count),
                "pct_area_gt30": pct30,
                "pct_area_gt60": pct60,
                "candidate_system": candidate,
                "classification_basis": (
                    "screening rule: >=50% area >60% inaccessible; "
                    ">=50% area >30% cable; otherwise ground-based"
                ),
            }
        )

    table = pd.DataFrame(rows).sort_values("block_id")
    table.to_csv(args.out_dir / "kc_blocks_slope_2024.csv", index=False)

    output = blocks.merge(table, on="block_id", how="left")
    output.to_file(args.out_dir / "kc_blocks_slope_2024.gpkg", driver="GPKG")

    metadata = {
        "source": "LidarBC 2024 1 m DEM",
        "dem_tiles": len(dem_paths),
        "tiles_used": tile_count,
        "blocks": len(table),
        "slope_method": "3x3 mean smoothing; np.gradient; percent slope",
        "thresholds": {"cable_candidate_pct_area_gt30": 50.0, "inaccessible_pct_area_gt60": 50.0},
        "crs": "EPSG:6653",
        "caveats": [
            "Screening classification, not a field operability or cable feasibility determination.",
            "The 2007 plan uses 'substantial area' rather than a fixed "
            "percentage; the 50% rule is a reproducible screening choice.",
            "DEM voids are filled to the nearest valid pixel before smoothing.",
        ],
    }
    (args.out_dir / "harvest_systems_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )
    print(table["candidate_system"].value_counts().to_string())
    print(f"blocks={len(table)} tiles_used={tile_count}")


if __name__ == "__main__":
    main()
