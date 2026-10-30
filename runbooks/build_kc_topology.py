#!/usr/bin/env python3
"""Build KC block topology from the Patchworks fragments shapefile.

Outputs both the Patchworks pair table and the ws4 topology table. Distance is
the shortest polygon-to-polygon distance; LENGTH is the shared boundary length.
Pairs farther than the search distance are omitted.

Usage::

    python runbooks/build_kc_topology.py \
      --fragments data/patchworks_knifecreek/spatial/fragments.shp \
      --out-dir data/patchworks_knifecreek/spatial \
      --ws4-out ws4/topology.csv \
      --search-distance 100
"""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd


def main() -> None:
    """Write the pair tables."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fragments", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--ws4-out", type=Path, required=True)
    parser.add_argument("--search-distance", type=float, default=100.0)
    args = parser.parse_args()
    blocks = gpd.read_file(args.fragments).to_crs(3005)
    rows = []
    for left in range(len(blocks)):
        a = blocks.iloc[left]
        for right in range(left + 1, len(blocks)):
            b = blocks.iloc[right]
            distance = float(a.geometry.distance(b.geometry))
            if distance > args.search_distance:
                continue
            shared = float(a.geometry.intersection(b.geometry).length)
            rows.append(
                {
                    "BLOCK1": int(a["BLOCK"]),
                    "BLOCK2": int(b["BLOCK"]),
                    "DISTANCE": round(distance, 3),
                    "LENGTH": round(shared, 3),
                }
            )
    frame = pd.DataFrame(rows).sort_values(["BLOCK1", "BLOCK2"])
    # WS4 requires every block to appear in the topology.  A block with no
    # neighbour inside the search distance gets its nearest-neighbour pair at
    # the actual distance; that keeps it in the inventory without pretending a
    # patch adjacency exists inside the patch search distance.
    present = set(frame["BLOCK1"]) | set(frame["BLOCK2"]) if not frame.empty else set()
    missing = [int(block) for block in blocks["BLOCK"] if int(block) not in present]
    extra = []
    for block in missing:
        left = blocks.loc[blocks["BLOCK"] == block].iloc[0]
        distances = [
            (float(left.geometry.distance(right.geometry)), int(right["BLOCK"]))
            for _, right in blocks.iterrows()
            if int(right["BLOCK"]) != block
        ]
        distance, neighbour = min(distances)
        extra.append(
            {
                "BLOCK1": min(block, neighbour),
                "BLOCK2": max(block, neighbour),
                "DISTANCE": round(distance, 3),
                "LENGTH": 0.0,
            }
        )
    if extra:
        frame = pd.concat([frame, pd.DataFrame(extra)], ignore_index=True)
        frame = frame.drop_duplicates(["BLOCK1", "BLOCK2"]).sort_values(["BLOCK1", "BLOCK2"])
    args.out_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.out_dir / "topo_fragments.csv", index=False)
    ws4 = frame.rename(
        columns={"BLOCK1": "src_block", "BLOCK2": "dst_block", "DISTANCE": "distance_m"}
    )[["src_block", "dst_block", "distance_m"]]
    args.ws4_out.parent.mkdir(parents=True, exist_ok=True)
    ws4.to_csv(args.ws4_out, index=False)
    all_blocks = present | {row["BLOCK1"] for row in extra} | {row["BLOCK2"] for row in extra}
    print(
        f"pairs={len(frame)} touching={int((frame.DISTANCE == 0).sum())} "
        f"nearest_neighbour_fill={len(extra)} blocks={len(all_blocks)}"
    )


if __name__ == "__main__":
    main()
