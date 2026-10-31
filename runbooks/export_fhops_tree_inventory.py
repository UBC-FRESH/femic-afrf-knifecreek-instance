#!/usr/bin/env python3
"""Export one block's LiDAR canopy trees to the FHOPS tree-inventory contract.

The FHOPS contract requires tree_id, block_id, x_m, y_m, species_code, dbh_cm,
height_m, status, and confidence. LiDAR supplies position, height, crown radius,
and a height-allometry DBH estimate; it does not supply species or measured DBH.

Usage::

    python runbooks/export_fhops_tree_inventory.py \
      --trees data/lidar/kc_2024/trees.parquet \
      --blocks data/patchworks_knifecreek/spatial_split/fragments.shp \
      --block-id 78 \
      --block-prefix KC \
      --out-dir data/lidar/kc_2024/fhops/kc_0078
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import geopandas as gpd
import pandas as pd

CRS = "EPSG:3005"


def _sha256(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    """Write the FHOPS CSV and metadata sidecar for one block."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--blocks", type=Path, required=True)
    parser.add_argument("--block-id", type=int, required=True)
    parser.add_argument("--block-column", default="BLOCK")
    parser.add_argument("--block-prefix", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--confidence", type=float, default=0.66)
    parser.add_argument("--trees-crs", default="EPSG:6653")
    args = parser.parse_args()

    if args.trees.suffix.lower() == ".parquet":
        frame = pd.read_parquet(args.trees)
        trees = gpd.GeoDataFrame(
            frame,
            geometry=gpd.points_from_xy(frame["x"], frame["y"]),
            crs=args.trees_crs,
        ).to_crs(CRS)
    else:
        trees = gpd.read_file(args.trees).to_crs(CRS)
    blocks = gpd.read_file(args.blocks).to_crs(CRS)
    block = blocks[blocks[args.block_column].astype(int) == args.block_id]
    if block.empty:
        raise SystemExit(f"block {args.block_id} not found")
    clipped = gpd.clip(trees, block[["geometry"]])
    if clipped.empty:
        raise SystemExit(f"no trees in block {args.block_id}")

    block_id = f"{args.block_prefix}_{args.block_id:04d}"
    frame = pd.DataFrame(
        {
            "tree_id": [f"{block_id}_{index:06d}" for index in range(1, len(clipped) + 1)],
            "block_id": block_id,
            "x_m": clipped.geometry.x.round(3),
            "y_m": clipped.geometry.y.round(3),
            "elevation_m": "",
            "species_code": (
                clipped["species"].fillna("UNK") if "species" in clipped.columns else "UNK"
            ),
            "dbh_cm": clipped["dbh_cm_est"].round(2),
            "height_m": clipped["height_m"].round(2),
            "crown_radius_m": (
                clipped["crown_radius_m"].round(2) if "crown_radius_m" in clipped.columns else ""
            ),
            "status": "live",
            "confidence": args.confidence,
            "source_id": "lidar-canopy-inventory",
            "source_tile_id": (clipped["tile"].fillna("") if "tile" in clipped.columns else ""),
            "merchantable_height_m": "",
            "defect": "",
            "grade_hint": "",
        }
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.out_dir / "inventory.csv"
    frame.to_csv(csv_path, index=False)
    metadata = {
        "schema_version": "fhops.tree.inventory.v1",
        "inventory_id": f"{block_id}-lidar-canopy",
        "generated_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_id": "lidar-canopy-inventory",
        "producer": "FEMIC/WS4 LiDAR pipeline",
        "method": (
            "1 m CHM local maxima; DBH height allometry; species unknown; canopy-only inventory"
        ),
        "crs": CRS,
        "units": {
            "x_y": "m",
            "elevation": "m",
            "dbh": "cm",
            "height": "m",
            "crown_radius": "m",
        },
        "review_status": "not_reviewed",
        "reviewed_by": None,
        "block_ids": [block_id],
        "caveats": [
            "Canopy tree inventory, not a CFI.",
            "Species is UNK and DBH is height allometry.",
            "Crown maxima can split crowns.",
        ],
        "tree_count": len(frame),
        "inventory_sha256": _sha256(csv_path),
    }
    (args.out_dir / "inventory.meta.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"block={block_id} trees={len(frame)} out={csv_path}")


if __name__ == "__main__":
    main()
