#!/usr/bin/env python3
"""Measure straight-line distance from each split block to the public road layer.

This is an access-context check, not a route linkage. It shows which blocks are
near the public tenure-road layer and which are beyond a 400 m skid distance.
The public layer is incomplete against the 2007 plan, so the result is a gap
indicator, not an AFRF access model.

Usage::

    python runbooks/measure_kc_public_access.py \
      --blocks data/patchworks_knifecreek/spatial_split/fragments.shp \
      --roads data/patchworks_knifecreek/spatial/roads.gpkg \
      --out-dir data/roads
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd


def main() -> None:
    """Write the nearest-public-road table and metadata."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--blocks",
        type=Path,
        default=Path("data/patchworks_knifecreek/spatial_split/fragments.shp"),
    )
    parser.add_argument(
        "--roads",
        type=Path,
        default=Path("data/patchworks_knifecreek/spatial/roads.gpkg"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("data/roads"))
    args = parser.parse_args()

    blocks = gpd.read_file(args.blocks).to_crs(3005)
    roads = gpd.read_file(args.roads).to_crs(3005)
    points = blocks[["BLOCK", "AREA_HA", "geometry"]].copy()
    points["geometry"] = points.representative_point()
    near = gpd.sjoin_nearest(
        points,
        roads[["ROAD_ID", "SECTION_ID", "ROAD_NAME", "LENGTH_M", "geometry"]],
        how="left",
        distance_col="distance_m",
    )
    near = near.rename(
        columns={
            "BLOCK": "block_id",
            "AREA_HA": "block_area_ha",
            "ROAD_ID": "nearest_road_id",
            "SECTION_ID": "nearest_section_id",
            "ROAD_NAME": "nearest_road_name",
            "LENGTH_M": "nearest_section_length_m",
        }
    )
    near = (
        near[
            [
                "block_id",
                "block_area_ha",
                "nearest_road_id",
                "nearest_section_id",
                "nearest_road_name",
                "nearest_section_length_m",
                "distance_m",
            ]
        ]
        .sort_values(["block_id", "distance_m"])
        .drop_duplicates("block_id")
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    near.to_csv(args.out_dir / "kc_public_access_nearest.csv", index=False)

    metadata = {
        "source": "BC Forest Tenure Road Section Lines (public layer)",
        "blocks": len(near),
        "roads": len(roads),
        "method": (
            "block representative point to nearest road section; straight-line "
            "distance, not skid or route distance"
        ),
        "within_100m": int((near["distance_m"] <= 100).sum()),
        "within_400m": int((near["distance_m"] <= 400).sum()),
        "beyond_400m": int((near["distance_m"] > 400).sum()),
        "max_distance_m": float(near["distance_m"].max()),
        "caveats": [
            "Public tenure-road layer is incomplete against MWP #3 Table 37 "
            "(44 sections, 59.6 km vs 86.2 km existing).",
            "Nearest-road distance is not an access route, skid distance, or legal "
            "access determination.",
            "Do not use this table as a route linkage.",
        ],
    }
    (args.out_dir / "kc_public_access_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )
    print(
        f"blocks={len(near)} within_400m={metadata['within_400m']} "
        f"beyond_400m={metadata['beyond_400m']}"
    )


if __name__ == "__main__":
    main()
