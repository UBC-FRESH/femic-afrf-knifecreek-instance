#!/usr/bin/env python3
"""Compile a synthetic ws4 dataset from the canonical GWM 2007 graph.

The dataset is a structural validation fixture, not a KC operating dataset:
each initial canonical state is one synthetic 1 ha block. It exercises the ws4
tables and validator without pretending that the PSP-derived states are KC
inventory.

Usage::

    PYTHONPATH=/path/to/ws4 python runbooks/compile_ws4_dataset.py \
      --canonical ws4/state_library_v1/canonical \
      --out-dir ws4/dataset_v1_synthetic
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
from ws4.model.api import Model
from ws4.model.schema import validate_dataset


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    """Write and validate the synthetic ws4 dataset."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    states = pd.read_csv(args.canonical / "states.csv")
    transitions = pd.read_csv(args.canonical / "transitions.csv")
    canonical_curves = pd.read_csv(args.canonical / "curves.csv")

    initial = states[(states["n_incoming"] == 0) & states["state_id"].str.contains("LT_NA")].copy()
    if initial.empty:
        initial = states[states["n_incoming"] == 0].head(8).copy()
    track_ids = {state: index for index, state in enumerate(states["state_id"], start=1)}
    initial_ids = [track_ids[state] for state in initial["state_id"]]

    tracks = pd.DataFrame({"track_id": list(track_ids.values()), "name": list(track_ids.keys())})
    blocks = pd.DataFrame(
        {
            "block_id": range(1, len(initial_ids) + 1),
            "track_id": initial_ids,
            "offset": 0,
            "area_ha": 1.0,
        }
    )
    fragments = pd.DataFrame(
        {
            "fragment_id": range(1, len(initial_ids) + 1),
            "block_id": range(1, len(initial_ids) + 1),
            "area_ha": 1.0,
            "age": 0,
            "track_id": initial_ids,
        }
    )
    strata = pd.DataFrame(
        {
            "track_id": tracks["track_id"],
            "offset": 0,
            "next_age": 30,
            "cycle": 30,
        }
    )
    treatments = pd.DataFrame(
        {
            "track_id": transitions["from_state"].map(track_ids),
            "begin": 30,
            "end": 300,
            "treatment": transitions["regime"],
            "new_track": transitions["to_state"].map(track_ids),
            "offset": 0,
            "retain": 0,
        }
    )

    curve_rows: list[dict[str, object]] = []
    curve_ids: dict[tuple[str, str], int] = {}
    next_curve = 1
    for row in canonical_curves.itertuples(index=False):
        key = (str(row.transition_id), str(row.attribute))
        if key not in curve_ids:
            curve_ids[key] = next_curve
            next_curve += 1
        curve_rows.append({"curve_id": curve_ids[key], "x": float(row.x), "y": float(row.y)})
    curves = pd.DataFrame(curve_rows)

    feature_rows: list[dict[str, object]] = []
    product_rows: list[dict[str, object]] = []
    for row in transitions.itertuples(index=False):
        track_id = int(track_ids[row.from_state])
        for attribute, label in (
            ("ba", "feature.habitat.basal_area"),
            ("qmd", "feature.habitat.qmd"),
            ("canopy_ccf", "feature.habitat.canopy_ccf"),
        ):
            curve_id = curve_ids.get((str(row.transition_id), attribute))
            if curve_id is not None:
                feature_rows.append({"track_id": track_id, "label": label, "curve_id": curve_id})
        curve_id = next_curve
        next_curve += 1
        curves = pd.concat(
            [
                curves,
                pd.DataFrame(
                    {
                        "curve_id": [curve_id, curve_id],
                        "x": [0.0, 30.0],
                        "y": [row.post_large_ba_m2_ha, row.post_large_ba_m2_ha],
                    }
                ),
            ],
            ignore_index=True,
        )
        feature_rows.append(
            {
                "track_id": track_id,
                "label": "feature.habitat.large_tree_ba",
                "curve_id": curve_id,
            }
        )
        product_curve = next_curve
        next_curve += 1
        curves = pd.concat(
            [
                curves,
                pd.DataFrame(
                    {
                        "curve_id": [product_curve],
                        "x": [0.0],
                        "y": [row.fvs_cut_m3_ha],
                    }
                ),
            ],
            ignore_index=True,
        )
        product_rows.append(
            {
                "track_id": track_id,
                "treatment": row.regime,
                "label": "product.yield.managed.total",
                "curve_id": product_curve,
            }
        )
    features = pd.DataFrame(feature_rows)
    products = pd.DataFrame(product_rows)
    groups = pd.DataFrame(columns=["block_id", "group"])
    accounts = pd.DataFrame(columns=["group", "attribute", "account", "sum"])
    protoaccounts = accounts.copy()
    messages = pd.DataFrame(columns=["severity", "message"])

    model = Model(
        {
            "fragments": fragments,
            "blocks": blocks,
            "tracks": tracks,
            "strata": strata,
            "treatments": treatments,
            "curves": curves,
            "features": features,
            "products": products,
            "groups": groups,
            "accounts": accounts,
            "protoaccounts": protoaccounts,
            "messages": messages,
        }
    )
    model.write(args.out_dir)
    manifest_path = args.out_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["sources"] = [
        {
            "path": str(args.canonical),
            "states_sha256": _hash(args.canonical / "states.csv"),
            "transitions_sha256": _hash(args.canonical / "transitions.csv"),
            "curves_sha256": _hash(args.canonical / "curves.csv"),
        }
    ]
    manifest["metadata"] = {
        "instance": "knife-creek",
        "basis": "GWM_2007",
        "status": "synthetic-structural-validation",
        "caveats": [
            "Synthetic 1 ha blocks, not KC inventory or operating area.",
            "Canonical states are structural bins, not calibrated KC states.",
            "The clump rule is a DBH-ranked proxy, not spatial.",
            "No UWR/HMZ spatial constraint.",
            "Not a legal-compliance product.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    problems = validate_dataset(args.out_dir)
    if problems:
        for problem in problems:
            print(f"{problem.code}: {problem.where}: {problem.message}")
        raise SystemExit(1)
    print(
        f"dataset={args.out_dir} fragments={len(fragments)} tracks={len(tracks)} "
        f"treatments={len(treatments)} curves={len(curves)}"
    )


if __name__ == "__main__":
    main()
