#!/usr/bin/env python3
"""Audit which acquired LiDAR products cover Knife Creek and Gavin Lake.

The OneDrive LiDAR payload mixes standard LAS/LAZ, 1 m rasters, and legacy
FUSION LIDARBIN. This runbook checks the readable products against both block
bounds and records the legacy files that the current pipeline cannot read.

Usage::

    python runbooks/audit_afrf_lidar_coverage.py \
      --out data/lidar/afrf_lidar_coverage_audit.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import geopandas as gpd
import laspy
import rasterio
from pyproj import Transformer

LIDAR_ROOT = Path(
    "external/ubc-research-forests-data/raw/ubc-research-forests-modelling-dropbox/LiDAR"
)


def _bounds_3005(
    bounds: tuple[float, float, float, float],
    source_crs: str,
) -> tuple[float, float, float, float]:
    """Transform a bounds tuple from a source CRS to EPSG:3005."""
    transformer = Transformer.from_crs(source_crs, "EPSG:3005", always_xy=True)
    left, bottom = transformer.transform(bounds[0], bounds[1])
    right, top = transformer.transform(bounds[2], bounds[3])
    return (min(left, right), min(bottom, top), max(left, right), max(bottom, top))


def _overlap_ha(
    bounds: tuple[float, float, float, float],
    block_bounds: tuple[float, float, float, float],
) -> float:
    """Return the overlap area in hectares."""
    left = max(bounds[0], block_bounds[0])
    bottom = max(bounds[1], block_bounds[1])
    right = min(bounds[2], block_bounds[2])
    top = min(bounds[3], block_bounds[3])
    if right <= left or top <= bottom:
        return 0.0
    return float((right - left) * (top - bottom) / 10_000.0)


def _record(
    path: Path, block_bounds: dict[str, tuple[float, float, float, float]]
) -> dict[str, Any] | None:
    """Read one LiDAR product and return its coverage record."""
    suffix = path.suffix.lower()
    if suffix == ".lasd":
        return {
            "path": str(path.relative_to(LIDAR_ROOT.parent)),
            "format": "FUSION LIDARBIN index",
            "readable": True,
            "laspy_readable": False,
            "fusion_readable": True,
            "reason": "valid FUSION index; use FUSION/LDV, not laspy",
        }
    if suffix in {".las", ".laz"}:
        with path.open("rb") as handle:
            signature = handle.read(8)
        if signature == b"LIDARBIN":
            return {
                "path": str(path.relative_to(LIDAR_ROOT.parent)),
                "format": "FUSION LIDARBIN",
                "readable": True,
                "laspy_readable": False,
                "fusion_readable": True,
                "reason": (
                    "valid FUSION/LDA binary with a .las suffix; use FUSION/LDV "
                    "or LDA2LAS, not a standard LAS reader"
                ),
            }
        try:
            with laspy.open(path) as handle:
                header = handle.header
                source_crs = "EPSG:26910" if path.parent.name == "2013" else "EPSG:3005"
                bounds = _bounds_3005(
                    (header.mins[0], header.mins[1], header.maxs[0], header.maxs[1]),
                    source_crs,
                )
                return {
                    "path": str(path.relative_to(LIDAR_ROOT.parent)),
                    "format": suffix.lstrip(".").upper(),
                    "readable": True,
                    "laspy_readable": True,
                    "fusion_readable": True,
                    "source_crs": source_crs,
                    "bounds_3005": bounds,
                    "intersects": {
                        name: _overlap_ha(bounds, target) for name, target in block_bounds.items()
                    },
                }
        except Exception as exc:  # pragma: no cover - depends on external files
            return {
                "path": str(path.relative_to(LIDAR_ROOT.parent)),
                "format": suffix.lstrip(".").upper(),
                "readable": False,
                "reason": str(exc),
            }
    if suffix in {".tif", ".tiff"}:
        try:
            with rasterio.open(path) as source:
                bounds = _bounds_3005(
                    (
                        source.bounds.left,
                        source.bounds.bottom,
                        source.bounds.right,
                        source.bounds.top,
                    ),
                    str(source.crs),
                )
                return {
                    "path": str(path.relative_to(LIDAR_ROOT.parent)),
                    "format": "GeoTIFF",
                    "readable": True,
                    "laspy_readable": False,
                    "fusion_readable": False,
                    "source_crs": str(source.crs),
                    "bounds_3005": bounds,
                    "intersects": {
                        name: _overlap_ha(bounds, target) for name, target in block_bounds.items()
                    },
                }
        except Exception as exc:  # pragma: no cover - depends on external files
            return {
                "path": str(path.relative_to(LIDAR_ROOT.parent)),
                "format": "GeoTIFF",
                "readable": False,
                "reason": str(exc),
            }
    return None


def main() -> None:
    """Write the coverage audit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--kc-blocks",
        type=Path,
        default=Path("data/patchworks_knifecreek/spatial_split/fragments.shp"),
    )
    parser.add_argument(
        "--gavin-blocks",
        type=Path,
        default=Path(
            "../femic-afrf-gavinlake-instance/data/legacy_gavinlake/spatial/fragments.shp"
        ),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/lidar/afrf_lidar_coverage_audit.json"),
    )
    args = parser.parse_args()

    kc = gpd.read_file(args.kc_blocks).to_crs(3005)
    gavin = gpd.read_file(args.gavin_blocks).to_crs(3005)
    block_bounds = {
        "knife_creek": tuple(float(value) for value in kc.total_bounds),
        "gavin_lake": tuple(float(value) for value in gavin.total_bounds),
    }

    records: list[dict[str, Any]] = []
    for path in sorted(LIDAR_ROOT.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".las", ".laz", ".tif", ".tiff", ".lasd"}:
            record = _record(path, block_bounds)
            if record is not None:
                records.append(record)

    readable = [record for record in records if record.get("readable")]
    bounded = [record for record in readable if "intersects" in record]
    summary = {
        "source_root": str(LIDAR_ROOT),
        "block_bounds_3005": block_bounds,
        "files": len(records),
        "readable": len(readable),
        "laspy_readable": sum(1 for record in records if record.get("laspy_readable")),
        "fusion_readable": sum(1 for record in records if record.get("fusion_readable")),
        "unreadable": len(records) - len(readable),
        "knife_creek": {
            "files_intersecting": sum(
                1 for record in bounded if record["intersects"]["knife_creek"] > 0.0
            ),
            "overlap_ha": sum(record["intersects"]["knife_creek"] for record in bounded),
        },
        "gavin_lake": {
            "files_intersecting": sum(
                1 for record in bounded if record["intersects"]["gavin_lake"] > 0.0
            ),
            "overlap_ha": sum(record["intersects"]["gavin_lake"] for record in bounded),
        },
        "legacy_fusion_files": [
            record["path"] for record in records if record.get("format") == "FUSION LIDARBIN index"
        ],
        "caveats": [
            "Overlap area is counted per file and can double-count overlapping tiles.",
            "The 2013 LAS files carry no CRS; they are assumed to be EPSG:26910 UTM 10N.",
            "FUSION LIDARBIN is valid data; it is readable with FUSION/LDV or "
            "LDA2LAS, not with laspy or a standard LAS reader.",
        ],
    }
    gavin_2009 = Path("../femic-afrf-gavinlake-instance/data/lidar/gavin_2009/summary.json")
    if gavin_2009.exists():
        payload = json.loads(gavin_2009.read_text())
        summary["gavin_lake"]["fusion_lidarbin_tiles"] = payload.get("tiles")
        summary["gavin_lake"]["fusion_lidarbin_trees"] = payload.get("trees")
        summary["gavin_lake"]["fusion_lidarbin_coverage"] = "full block"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"summary": summary, "records": records}, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
