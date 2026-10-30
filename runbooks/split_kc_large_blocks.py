#!/usr/bin/env python3
"""Split large KC blocks into smaller sub-blocks for harvest-flow granularity.

The source fragments are VRI polygons.  A 210 ha polygon treated in one entry
creates a one-block harvest spike even when the annual volume is fine.  This
splits polygons above a maximum area into a compact grid of sub-polygons,
preserving track, age, AU/HMZ and stand attributes.

Usage::

    python runbooks/split_kc_large_blocks.py \
      --fragments data/patchworks_knifecreek/spatial/fragments.shp \
      --out-dir data/patchworks_knifecreek/spatial_split \
      --max-ha 40 \
      --schedule-in ws4/runtime/kc_au_stages/selection_gwm_legal.csv \
      --schedule-out ws4/runtime/kc_au_stages_split/selection_gwm_legal.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import box
from shapely.geometry.base import BaseGeometry


def _split_geometry(geometry: BaseGeometry, max_ha: float, depth: int = 0) -> list[BaseGeometry]:
    """Recursively bisect a polygon until every part is at most max_ha."""
    if geometry.area / 10000.0 <= max_ha or depth >= 8:
        return [geometry]
    minx, miny, maxx, maxy = geometry.bounds
    if (maxx - minx) >= (maxy - miny):
        midpoint = (minx + maxx) / 2.0
        left = box(minx, miny, midpoint, maxy)
        right = box(midpoint, miny, maxx, maxy)
    else:
        midpoint = (miny + maxy) / 2.0
        left = box(minx, miny, maxx, midpoint)
        right = box(minx, midpoint, maxx, maxy)
    parts = []
    for cell in (left, right):
        part = geometry.intersection(cell)
        if part.is_empty or part.area <= 0:
            continue
        parts.extend(_split_geometry(part, max_ha, depth + 1))
    return parts or [geometry]


def main() -> None:
    """Write split fragments and an initial schedule mapped to children."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fragments", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--max-ha", type=float, default=40.0)
    parser.add_argument("--schedule-in", type=Path)
    parser.add_argument("--schedule-out", type=Path)
    args = parser.parse_args()
    source = gpd.read_file(args.fragments).to_crs(3005)
    source["AREA_HA"] = source.geometry.area / 10000.0
    max_block = int(source["BLOCK"].max())
    rows = []
    parent_lookup: dict[int, list[int]] = {}
    next_block = max_block + 1
    for record in source.itertuples(index=False):
        parts = _split_geometry(record.geometry, args.max_ha)
        parent = int(record.BLOCK)
        children = []
        for geometry in parts:
            if len(parts) == 1:
                block = parent
            else:
                block = next_block
                next_block += 1
            children.append(block)
            data = record._asdict()
            data.pop("geometry")
            data["BLOCK"] = block
            data["PARENT_BLOCK"] = parent
            data["AREA_HA"] = geometry.area / 10000.0
            data["geometry"] = geometry
            rows.append(data)
        parent_lookup[parent] = children
    split = gpd.GeoDataFrame(rows, crs=source.crs).sort_values("BLOCK")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    split.to_file(args.out_dir / "fragments.shp", driver="ESRI Shapefile")
    split.drop(columns="geometry").to_csv(args.out_dir / "fragments.csv", index=False)
    manifest = {
        "source_fragments": str(args.fragments),
        "max_ha": args.max_ha,
        "source_blocks": len(source),
        "split_blocks": len(split),
        "source_area_ha": float(source["AREA_HA"].sum()),
        "split_area_ha": float(split["AREA_HA"].sum()),
        "split_parents": {
            str(parent): children for parent, children in parent_lookup.items() if len(children) > 1
        },
    }
    (args.out_dir / "split_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if args.schedule_in and args.schedule_out:
        schedule = pd.read_csv(args.schedule_in)
        schedule_rows = []
        for row in schedule.itertuples(index=False):
            for child in parent_lookup.get(int(row.block_id), []):
                schedule_rows.append(
                    {
                        "block_id": int(child),
                        "treatment": row.treatment,
                        "offset": int(row.offset),
                    }
                )
        args.schedule_out.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(schedule_rows).drop_duplicates().to_csv(args.schedule_out, index=False)
        manifest["schedule_in"] = str(args.schedule_in)
        manifest["schedule_out"] = str(args.schedule_out)
        manifest["schedule_rows"] = len(schedule_rows)
        (args.out_dir / "split_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"blocks {len(source)} -> {len(split)}  "
        f"area {manifest['source_area_ha']:.3f} -> {manifest['split_area_ha']:.3f} ha"
    )


if __name__ == "__main__":
    main()
