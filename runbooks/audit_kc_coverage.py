#!/usr/bin/env python3
"""Audit KC ws4 inventory, state and group coverage.

This is a structural verification. It does not verify growth calibration or
legal compliance.

Usage::

    python runbooks/audit_kc_coverage.py \
      --dataset ws4/dataset_kc_v1 \
      --recipe-fragments data/kc_ws4_recipe/fragments.csv \
      --source-fragments data/patchworks_knifecreek/fragments.csv \
      --topology ws4/topology.csv \
      --out ws4/evidence/kc_v1/coverage_audit.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> None:
    """Write a machine-readable coverage audit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--recipe-fragments", type=Path, required=True)
    parser.add_argument("--source-fragments", type=Path, required=True)
    parser.add_argument("--topology", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    fragments = pd.read_parquet(args.dataset / "fragments.parquet")
    blocks = pd.read_parquet(args.dataset / "blocks.parquet")
    tracks = pd.read_parquet(args.dataset / "tracks.parquet")
    treatments = pd.read_parquet(args.dataset / "treatments.parquet")
    groups = pd.read_parquet(args.dataset / "groups.parquet")
    recipe_fragments = pd.read_csv(args.recipe_fragments)
    source_fragments = pd.read_csv(args.source_fragments)
    topology = pd.read_csv(args.topology)
    h_tracks = pd.read_csv(Path("data/patchworks_knifecreek/tracks/H/tracknames.csv"))

    issues: list[str] = []
    block_ids = set(blocks["block_id"].astype(int))
    fragment_blocks = set(fragments["block_id"].astype(int))
    recipe_blocks = set(recipe_fragments["BLOCK"].astype(int))
    source_blocks = set(source_fragments["BLOCK"].astype(int))
    topology_blocks = set(topology["src_block"].astype(int)) | set(
        topology["dst_block"].astype(int)
    )

    for name, values in (
        ("blocks", block_ids),
        ("fragments", fragment_blocks),
        ("recipe fragments", recipe_blocks),
        ("source fragments", source_blocks),
        ("topology", topology_blocks),
    ):
        if len(values) != 160:
            issues.append(f"{name} covers {len(values)} blocks, expected 160")

    if block_ids != fragment_blocks:
        issues.append("blocks and fragments do not cover the same block ids")
    if block_ids != recipe_blocks:
        issues.append("blocks and recipe fragments do not cover the same block ids")
    if block_ids != source_blocks:
        issues.append("blocks and source fragments do not cover the same block ids")
    if block_ids != topology_blocks:
        issues.append("blocks and topology do not cover the same block ids")

    track_ids = set(tracks["track_id"].astype(int))
    if not set(fragments["track_id"].astype(int)).issubset(track_ids):
        issues.append("a fragment references an unknown track")
    if not set(blocks["track_id"].astype(int)).issubset(track_ids):
        issues.append("a block references an unknown track")
    if not set(treatments["new_track"].astype(int)).issubset(track_ids):
        issues.append("a treatment references an unknown target track")

    if recipe_fragments["AU"].isna().any():
        issues.append("one or more recipe fragments have no AU")
    if recipe_fragments["AU"].nunique() != 1:
        issues.append("the current recipe has more than one AU")

    area_fragments = float(fragments["area_ha"].sum())
    area_blocks = float(blocks["area_ha"].sum())
    area_recipe = float(recipe_fragments["AREA_HA"].sum())
    area_source = float(source_fragments["AREA_HA"].sum())
    if abs(area_fragments - area_blocks) > 1e-6:
        issues.append("fragment and block area totals differ")
    if abs(area_fragments - area_recipe) > 1e-6:
        issues.append("fragment and recipe area totals differ")
    if abs(area_fragments - area_source) > 1e-6:
        issues.append("fragment and source area totals differ")

    group_names = set(groups["group"].astype(str))
    for required in ("forest", "ifm_managed"):
        if required not in group_names:
            issues.append(f"missing group: {required}")
    group_blocks = set(groups["block_id"].astype(int))
    if group_blocks != block_ids:
        issues.append("groups do not cover the same block ids")
    group_families = {
        family: {name for name in group_names if name.startswith(f"{family}_")}
        for family in ("hmz", "clump", "reserve")
    }
    for family, names in group_families.items():
        if not names:
            issues.append(f"no {family} groups")
        counts = groups[groups["group"].isin(names)].groupby("block_id")["group"].nunique()
        if len(counts) != len(block_ids) or (counts != 1).any():
            issues.append(f"{family} membership is not exactly one group per block")

    reachable = len(tracks)
    source_tracks = int(h_tracks["TRACK"].nunique())
    result = {
        "dataset": str(args.dataset),
        "blocks": len(block_ids),
        "fragments": len(fragments),
        "recipe_blocks": len(recipe_blocks),
        "source_blocks": len(source_blocks),
        "topology_blocks": len(topology_blocks),
        "topology_pairs": len(topology),
        "tracks_reachable": reachable,
        "tracks_source": source_tracks,
        "tracks_unreachable": source_tracks - reachable,
        "treatments": len(treatments),
        "aus": [int(value) for value in recipe_fragments["AU"].unique()],
        "area_ha": {
            "fragments": round(area_fragments, 6),
            "blocks": round(area_blocks, 6),
            "recipe": round(area_recipe, 6),
            "source": round(area_source, 6),
        },
        "groups": {
            "count": len(group_names),
            "memberships": len(groups),
            "families": {name: sorted(values) for name, values in group_families.items()},
        },
        "issues": issues,
        "ok": not issues,
        "limits": [
            "The source H scaffold has 92 possible tracks; only 19 are reachable "
            "from the current inventory and treatments.",
            "Area is the net fragment area, not the gross SUP permit area.",
            "No legal-compliance or calibrated-growth conclusion is drawn.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
