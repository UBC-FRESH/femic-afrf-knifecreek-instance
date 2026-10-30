#!/usr/bin/env python3
"""Integrate the 200-year KC PSP FVS curves into the H source matrix.

Each H track state is assigned to the nearest KC PSP plot by initial BA and QMD.
The plot's 200-year no-cut FVS curve then supplies the track's feature curves.
Product curves remain the source matrix's point estimates.

Usage::

    python runbooks/integrate_kc_psp_200y.py \
      --h-dir data/patchworks_knifecreek/tracks/H \
      --curves data/psp/kc_afrf_psp_fvs_200y_curves.csv \
      --out-dir data/patchworks_knifecreek/tracks/H_200y
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

BA_CENTRES = {
    "BA_LT20": 17.5,
    "BA20_25": 22.5,
    "BA25_30": 27.5,
    "BA30_35": 32.5,
    "BA35_40": 37.5,
    "BA40_PLUS": 42.5,
}
QMD_CENTRES = {
    "QMD_LT20": 17.5,
    "QMD20_25": 22.5,
    "QMD25_30": 27.5,
    "QMD30_35": 32.5,
    "QMD35_PLUS": 37.5,
}
LABELS = {
    "feature.habitat.basal_area": "ba_m2_ha",
    "feature.habitat.qmd": "qmd_cm",
    "feature.habitat.tph": "tph",
    "feature.yield.managed.total": "volume_m3_ha",
    "feature.habitat.canopy_ccf": "canopy_ccf",
}


def _state_value(name: str, centres: dict[str, float]) -> float:
    """Return the centre value named in a track state."""
    for key, value in centres.items():
        if f"__{key}__" in name:
            return value
    return float("nan")


def main() -> None:
    """Write H_200y with 200-year feature curves."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h-dir", type=Path, required=True)
    parser.add_argument("--curves", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    tracks = pd.read_csv(args.h_dir / "tracknames.csv")
    source_curves = pd.read_csv(args.h_dir / "curves.csv")
    products = pd.read_csv(args.h_dir / "products.csv")
    plot_curves = pd.read_csv(args.curves)
    initial = (
        plot_curves[plot_curves["year"] == 0]
        .sort_values("plot")
        .drop_duplicates("plot")
        .reset_index(drop=True)
    )
    if initial.empty:
        raise ValueError("the curve table has no year-0 rows")

    # Map each track to the nearest plot initial state in BA/QMD space.
    map_rows = []
    for row in tracks.itertuples(index=False):
        ba = _state_value(str(row.STRATA), BA_CENTRES)
        qmd = _state_value(str(row.STRATA), QMD_CENTRES)
        if not np.isfinite(ba) or not np.isfinite(qmd):
            ba = float(initial["ba_m2_ha"].median())
            qmd = float(initial["qmd_cm"].median())
        distance = ((initial["ba_m2_ha"] - ba) / 5.0) ** 2 + ((initial["qmd_cm"] - qmd) / 5.0) ** 2
        plot = int(initial.loc[distance.idxmin(), "plot"])
        map_rows.append({"TRACK": int(row.TRACK), "plot": plot, "track_ba": ba, "track_qmd": qmd})
    mapping = pd.DataFrame(map_rows)

    # Copy the source matrix, then replace only the feature curves.
    if args.out_dir.exists():
        shutil.rmtree(args.out_dir)
    shutil.copytree(args.h_dir, args.out_dir)
    for name in ("manifest.json", "features.csv", "curves.csv"):
        path = args.out_dir / name
        if path.exists():
            path.unlink()

    feature_rows = []
    curve_rows = []
    next_curve = 1
    area_curve = next_curve
    next_curve += 1
    curve_rows.append({"CURVE": area_curve, "X": 0, "Y": 1.0})
    for track in tracks["TRACK"].astype(int):
        plot_id = int(mapping.loc[mapping["TRACK"] == track, "plot"].iloc[0])
        plot = plot_curves[plot_curves["plot"] == plot_id].sort_values("year")
        for label, column in LABELS.items():
            curve_id = next_curve
            next_curve += 1
            for point in plot.itertuples(index=False):
                curve_rows.append(
                    {"CURVE": curve_id, "X": int(point.year), "Y": float(getattr(point, column))}
                )
            feature_rows.append({"TRACK": track, "LABEL": label, "METHOD": "", "CURVE": curve_id})
        feature_rows.append(
            {
                "TRACK": track,
                "LABEL": "feature.area.managed.total",
                "METHOD": "",
                "CURVE": area_curve,
            }
        )

    # Preserve the product curves from the source matrix.
    product_curve_map: dict[int, int] = {}
    for source_id in products["CURVE"].dropna().astype(int).unique():
        target_id = next_curve
        next_curve += 1
        product_curve_map[int(source_id)] = target_id
        points = source_curves[source_curves["CURVE"] == source_id]
        for point in points.itertuples(index=False):
            curve_rows.append({"CURVE": target_id, "X": float(point.X), "Y": float(point.Y)})
    products = products.copy()
    products["CURVE"] = products["CURVE"].astype(int).map(product_curve_map)

    pd.DataFrame(feature_rows, columns=["TRACK", "LABEL", "METHOD", "CURVE"]).to_csv(
        args.out_dir / "features.csv", index=False
    )
    pd.DataFrame(curve_rows, columns=["CURVE", "X", "Y"]).to_csv(
        args.out_dir / "curves.csv", index=False
    )
    products.to_csv(args.out_dir / "products.csv", index=False)

    manifest = {
        "matrix": "kc-h-200y-psp-curves-v1",
        "source_h": str(args.h_dir),
        "source_curves": str(args.curves),
        "tracks": len(tracks),
        "plots": len(initial),
        "feature_rows": len(feature_rows),
        "product_rows": len(products),
        "curve_ids": int(max([row["CURVE"] for row in curve_rows])),
        "horizon_years": int(plot_curves["year"].max()),
        "mapping": mapping.to_dict(orient="records"),
        "caveats": [
            "Track-to-plot assignment is nearest initial BA/QMD, not a spatial join.",
            "No-cut FVS-BC curves with tree age 60 and site index 60 placeholders.",
            "Product curves remain the source H point estimates.",
            "No KC calibration or legal-compliance claim.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    summary = {
        key: manifest[key]
        for key in ("tracks", "plots", "feature_rows", "product_rows", "horizon_years")
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
