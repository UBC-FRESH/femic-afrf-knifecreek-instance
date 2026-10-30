#!/usr/bin/env python3
"""Build the first Patchworks-compatible KC `tracks/H` matrix.

This is the matrix scaffold from the validated spatial structural dataset. It
preserves the existing 30-year curves and marks the 300-year extension as a
limit; it does not fabricate longer curves.

Usage::

    python runbooks/build_kc_patchworks_h.py \
      --dataset ws4/dataset_kc_spatial_v3 \
      --fragments data/patchworks_knifecreek/fragments.csv \
      --out-dir data/patchworks_knifecreek/tracks/H
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

AREA_HA = 0.05


def _write(frame: pd.DataFrame, path: Path, columns: list[str]) -> None:
    """Write a matrix table with a deterministic column order."""
    frame.reindex(columns=columns).to_csv(path, index=False)


def main() -> None:
    """Write the H matrix tables and a manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--fragments", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    dataset = args.dataset
    blocks = pd.read_parquet(dataset / "blocks.parquet")
    tracks = pd.read_parquet(dataset / "tracks.parquet")
    strata = pd.read_parquet(dataset / "strata.parquet")
    treatments = pd.read_parquet(dataset / "treatments.parquet")
    curves = pd.read_parquet(dataset / "curves.parquet")
    features = pd.read_parquet(dataset / "features.parquet")
    products = pd.read_parquet(dataset / "products.parquet")
    groups = pd.read_parquet(dataset / "groups.parquet")
    fragments = pd.read_csv(args.fragments)
    if len(blocks) != len(fragments):
        raise ValueError("blocks and fragments are not one-to-one")
    if set(blocks.block_id) != set(fragments.BLOCK):
        raise ValueError("block ids do not match fragments")

    h_blocks = pd.DataFrame(
        {
            "BLOCK": blocks["block_id"],
            "TYPE": "managed",
            "TRACK": blocks["track_id"],
            "OFFSET": blocks["offset"],
            "AREA": blocks["area_ha"],
        }
    )
    tracknames = pd.DataFrame({"TRACK": tracks["track_id"], "STRATA": tracks["name"]})
    h_strata = pd.DataFrame(
        {
            "TRACK": strata["track_id"],
            "OFFSET": strata["offset"],
            "NEXTAGE": strata["next_age"],
            "CYCLE": strata["cycle"],
            "au": 0,
            "auf": 0,
        }
    )
    h_treatments = pd.DataFrame(
        {
            "TRACK": treatments["track_id"],
            "BEGIN": treatments["begin"],
            "END": treatments["end"],
            "TREATMENT": treatments["treatment"],
            "MANUAL": "false",
            "NEWTRACK": treatments["new_track"],
            "ADJUST": "A",
            "OFFSET": treatments["offset"],
            "RETAIN": treatments["retain"],
            "CURVE": "",
            "CYCLE": 0,
            "ELIGIBILITY": "",
        }
    )
    h_curves = curves.rename(columns={"curve_id": "CURVE", "x": "X", "y": "Y"})
    h_features = pd.DataFrame(
        {
            "TRACK": features["track_id"],
            "LABEL": features["label"],
            "METHOD": "",
            "CURVE": features["curve_id"],
        }
    )
    h_products = pd.DataFrame(
        {
            "TRACK": products["track_id"],
            "TREATMENT": products["treatment"],
            "LABEL": products["label"],
            "FUTURE": 0,
            "ADJUST": "R",
            "METHOD": "",
            "CURVE": products["curve_id"],
        }
    )
    accounts = pd.DataFrame(columns=["GROUP", "ATTRIBUTE", "ACCOUNT", "SUM"])
    h_groups = pd.DataFrame({"BLOCK": groups["block_id"], "GROUP": groups["group"]})
    messages = pd.DataFrame(columns=["MESSAGE"])

    _write(
        h_blocks,
        args.out_dir / "blocks.csv",
        ["BLOCK", "TYPE", "TRACK", "OFFSET", "AREA"],
    )
    _write(tracknames, args.out_dir / "tracknames.csv", ["TRACK", "STRATA"])
    _write(
        h_strata,
        args.out_dir / "strata.csv",
        ["TRACK", "OFFSET", "NEXTAGE", "CYCLE", "au", "auf"],
    )
    _write(
        h_treatments,
        args.out_dir / "treatments.csv",
        [
            "TRACK",
            "BEGIN",
            "END",
            "TREATMENT",
            "MANUAL",
            "NEWTRACK",
            "ADJUST",
            "OFFSET",
            "RETAIN",
            "CURVE",
            "CYCLE",
            "ELIGIBILITY",
        ],
    )
    _write(h_curves, args.out_dir / "curves.csv", ["CURVE", "X", "Y"])
    _write(h_features, args.out_dir / "features.csv", ["TRACK", "LABEL", "METHOD", "CURVE"])
    _write(
        h_products,
        args.out_dir / "products.csv",
        ["TRACK", "TREATMENT", "LABEL", "FUTURE", "ADJUST", "METHOD", "CURVE"],
    )
    _write(accounts, args.out_dir / "accounts.csv", ["GROUP", "ATTRIBUTE", "ACCOUNT", "SUM"])
    _write(accounts, args.out_dir / "protoaccounts.csv", ["GROUP", "ATTRIBUTE", "ACCOUNT", "SUM"])
    _write(h_groups, args.out_dir / "groups.csv", ["BLOCK", "GROUP"])
    _write(messages, args.out_dir / "messages.csv", ["MESSAGE"])
    manifest = {
        "matrix": "kc-patchworks-H-scaffold-v1",
        "blocks": len(h_blocks),
        "tracks": len(tracknames),
        "treatments": len(h_treatments),
        "curves": int(h_curves["CURVE"].nunique()),
        "curve_points": len(h_curves),
        "features": len(h_features),
        "products": len(h_products),
        "horizon_years": int(h_curves["X"].max()),
        "period_years": 10,
        "status": "matrix-scaffold-30-year-curves",
        "caveats": [
            "Curves currently cover years 0-30 only; the 300-year extension is not generated.",
            "accounts.csv and protoaccounts.csv are empty; product/feature account wiring is P3.4.",
            "No clearcut treatment exists.",
            "No ForestModelXML is claimed.",
            "The source is dataset_kc_spatial_v3, which is a structural PSP-derived library.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
