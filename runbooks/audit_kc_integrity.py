#!/usr/bin/env python3
"""Audit KC ws4 transition and curve integrity.

This verifies structural integrity and source-curve consistency. It does not
claim that the curves are calibrated KC growth.

Usage::

    python runbooks/audit_kc_integrity.py \
      --dataset ws4/dataset_kc_v1 \
      --recipe data/kc_ws4_recipe/forestmodel.xml \
      --h-dir data/patchworks_knifecreek/tracks/H \
      --out ws4/evidence/kc_v1/integrity_audit.json
"""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd


def _recipe_curve_ids(recipe: Path) -> dict[str, int]:
    """Return curve name -> compiled id, matching the compiler's recipe order."""
    root = ET.parse(recipe).getroot()
    return {
        str(curve.get("id")): index for index, curve in enumerate(root.findall("./curve"), start=1)
    }


def _close(left: np.ndarray, right: np.ndarray) -> bool:
    """Compare two curve point arrays with a small serialization tolerance."""
    return left.shape == right.shape and bool(np.allclose(left, right, rtol=1e-5, atol=1e-7))


def main() -> None:
    """Write a machine-readable integrity audit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--h-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    curves = pd.read_parquet(args.dataset / "curves.parquet")
    features = pd.read_parquet(args.dataset / "features.parquet")
    products = pd.read_parquet(args.dataset / "products.parquet")
    treatments = pd.read_parquet(args.dataset / "treatments.parquet")
    tracks = pd.read_parquet(args.dataset / "tracks.parquet")
    strata = pd.read_parquet(args.dataset / "strata.parquet")
    h_curves = pd.read_csv(args.h_dir / "curves.csv")
    h_features = pd.read_csv(args.h_dir / "features.csv")
    h_products = pd.read_csv(args.h_dir / "products.csv")

    issues: list[str] = []
    curve_ids = set(curves["curve_id"].astype(int))
    track_ids = set(tracks["track_id"].astype(int))

    for curve_id, group in curves.groupby("curve_id", sort=True):
        values = group.sort_values("x")["x"].to_numpy(dtype=float)
        if not np.isfinite(values).all():
            issues.append(f"curve {curve_id} has a non-finite x")
        if len(values) > 1 and not np.all(np.diff(values) > 0):
            issues.append(f"curve {curve_id} x values are not strictly increasing")
        if group["y"].isna().any():
            issues.append(f"curve {curve_id} has a missing y")

    for name, frame in (("features", features), ("products", products)):
        missing = sorted(set(frame["curve_id"].astype(int)) - curve_ids)
        if missing:
            issues.append(f"{name} reference missing curves: {missing}")

    if not set(features["track_id"].astype(int)).issubset(track_ids):
        issues.append("a feature references an unknown track")
    if not set(products["track_id"].astype(int)).issubset(track_ids):
        issues.append("a product references an unknown track")
    if not set(treatments["track_id"].astype(int)).issubset(track_ids):
        issues.append("a treatment references an unknown source track")
    if not set(treatments["new_track"].astype(int)).issubset(track_ids):
        issues.append("a treatment references an unknown target track")
    if not set(strata["track_id"].astype(int)).issubset(track_ids):
        issues.append("a stratum references an unknown track")

    for row in treatments.itertuples(index=False):
        if int(row.end) < int(row.begin):
            issues.append(f"treatment {row.treatment} has end < begin")
        if str(row.treatment).upper() in {"CC", "CLEARCUT", "CLEAR_CUT"}:
            issues.append(f"clearcut treatment present: {row.treatment}")

    h_counts = h_curves.groupby("CURVE").size()
    compiled_counts = curves.groupby("curve_id").size()
    recipe_ids = _recipe_curve_ids(args.recipe)
    curve_checked = 0
    for source_id, group in h_curves.groupby("CURVE", sort=True):
        name = f"kc_{int(source_id)}"
        compiled_id = recipe_ids.get(name)
        if compiled_id is None:
            issues.append(f"source curve {source_id} is absent from the recipe")
            continue
        source_points = group.sort_values("X")[["X", "Y"]].to_numpy(dtype=float)
        target = (
            curves[curves["curve_id"] == compiled_id]
            .sort_values("x")[["x", "y"]]
            .to_numpy(dtype=float)
        )
        if not _close(source_points, target):
            issues.append(f"source curve {source_id} differs from compiled curve {compiled_id}")
        else:
            curve_checked += 1

    source_labels = set(h_features["LABEL"].astype(str))
    compiled_labels = set(features["label"].astype(str))
    if not source_labels.issubset(compiled_labels):
        issues.append(
            f"source feature labels missing from compile: {sorted(source_labels - compiled_labels)}"
        )
    source_products = set(h_products["LABEL"].astype(str))
    compiled_products = set(products["label"].astype(str))
    if not source_products.issubset(compiled_products):
        issues.append(
            "source product labels missing from compile: "
            f"{sorted(source_products - compiled_products)}"
        )

    result = {
        "dataset": str(args.dataset),
        "recipe": str(args.recipe),
        "source_matrix": str(args.h_dir),
        "curves": {
            "compiled_ids": len(curve_ids),
            "compiled_points": len(curves),
            "source_ids": int(h_curves["CURVE"].nunique()),
            "source_points": len(h_curves),
            "checked_against_source": curve_checked,
            "source_counts_match": bool(
                h_counts.shape[0] == 0
                or compiled_counts.reindex(
                    [recipe_ids[f"kc_{int(value)}"] for value in h_counts.index]
                )
                .to_numpy()
                .tolist()
                == h_counts.to_numpy().tolist()
            ),
        },
        "treatments": {
            "rows": len(treatments),
            "labels": sorted(treatments["treatment"].astype(str).unique()),
            "clearcut": bool(
                set(treatments["treatment"].astype(str).str.upper())
                & {"CC", "CLEARCUT", "CLEAR_CUT"}
            ),
        },
        "strata": {
            "rows": len(strata),
            "zero_cycle_tracks": int((strata["cycle"] <= 0).sum()),
            "note": "cycle is compiler metadata and is not used by the annual simulator",
        },
        "features": len(features),
        "products": len(products),
        "issues": issues,
        "ok": not issues,
        "limits": [
            "Source curves are the KC H-matrix structural curves, not a fresh FVS-BC validation.",
            "Feature curves cover 100 years; product curves cover 30 years.",
            "No calibrated-growth or legal-compliance conclusion is drawn.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
