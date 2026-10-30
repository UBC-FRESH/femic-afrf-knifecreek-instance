#!/usr/bin/env python3
"""Map the FAIB space-for-time curves into the KC Patchworks H feature layer.

The product curves stay on the existing treatment runs. The feature curves are
replaced by nearest-neighbour regional space-for-time curves, which extend the
feature horizon to 50 years.

Usage::

    python runbooks/integrate_psp_space_for_time.py \
      --h-dir data/patchworks_knifecreek/tracks/H \
      --panel-dir data/psp \
      --out-dir data/patchworks_knifecreek/tracks/H
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

BA_MID = {
    "BA_LT20": 15.0,
    "BA20_25": 22.5,
    "BA25_30": 27.5,
    "BA30_35": 32.5,
    "BA35_40": 37.5,
    "BA40_PLUS": 45.0,
}
QMD_MID = {
    "QMD_LT20": 17.5,
    "QMD20_25": 22.5,
    "QMD25_30": 27.5,
    "QMD30_35": 32.5,
    "QMD35_PLUS": 37.5,
}
FEATURE_MAP = {
    "feature.habitat.basal_area": "ba_m2_ha",
    "feature.habitat.qmd": "qmd_cm",
    "feature.habitat.tph": "tph",
    "feature.habitat.canopy_ccf": "canopy_ccf",
    "feature.yield.managed.total": "volume_m3_ha",
}


def _track_state(name: str) -> tuple[float, float]:
    """Parse BA and QMD midpoints from a track name."""
    ba_match = re.search(r"__(BA[A-Z0-9_]+?)__", name)
    qmd_match = re.search(r"__(QMD[A-Z0-9_]+?)__", name)
    if not ba_match or not qmd_match:
        raise ValueError(f"cannot parse state from {name}")
    ba_key = ba_match.group(1)
    qmd_key = qmd_match.group(1)
    if ba_key not in BA_MID or qmd_key not in QMD_MID:
        raise ValueError(f"unknown bin in {name}: {ba_key}, {qmd_key}")
    return BA_MID[ba_key], QMD_MID[qmd_key]


def main() -> None:
    """Write the mapped feature curves and updated H layer."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h-dir", type=Path, required=True)
    parser.add_argument("--panel-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    curves = pd.read_csv(args.panel_dir / "idf_cariboo_space_for_time_curves.csv")
    panel = pd.read_csv(args.panel_dir / "idf_cariboo_space_for_time_plots.csv")
    tracks = pd.read_csv(args.h_dir / "tracknames.csv")
    old_curves = pd.read_csv(args.h_dir / "curves.csv")
    products = pd.read_csv(args.h_dir / "products.csv")

    panel["state_id"] = "FAIB-" + panel["site_id"].astype(str)
    panel = panel.set_index("state_id")
    state_ids = list(panel.index)
    panel_mid = panel[["ba", "qmd"]].to_numpy(float)
    scale = np.array([max(panel["ba"].std(), 1.0), max(panel["qmd"].std(), 1.0)])
    state_names = sorted(set(tracks["STRATA"].astype(str)))
    state_to_panel = {}
    for name in state_names:
        track_mid = np.array(_track_state(name))
        distance = np.linalg.norm((panel_mid - track_mid[None, :]) / scale, axis=1)
        state_index = int(np.argmin(distance))
        state_to_panel[name] = (state_ids[state_index], float(distance[state_index]))
    mapping = []
    for row in tracks.itertuples(index=False):
        name = str(row.STRATA)
        track_ba, track_qmd = _track_state(name)
        state_id, distance_value = state_to_panel[name]
        state_pos = state_ids.index(state_id)
        mapping.append(
            {
                "TRACK": int(row.TRACK),
                "state_id": state_id,
                "distance": distance_value,
                "track_ba": track_ba,
                "track_qmd": track_qmd,
                "panel_ba": float(panel_mid[state_pos, 0]),
                "panel_qmd": float(panel_mid[state_pos, 1]),
            }
        )
    mapping_frame = pd.DataFrame(mapping)
    mapping_frame.to_csv(args.h_dir / "space_for_time_mapping.csv", index=False)

    next_curve = int(old_curves["CURVE"].max()) + 1
    new_curves = []
    new_features = []
    for row in mapping_frame.itertuples(index=False):
        subset = curves[curves["state_id"] == row.state_id].sort_values("year")
        if subset.empty:
            raise ValueError(f"no curves for {row.state_id}")
        for label, column in FEATURE_MAP.items():
            curve_id = next_curve
            next_curve += 1
            for point in subset.itertuples(index=False):
                new_curves.append(
                    {"CURVE": curve_id, "X": int(point.year), "Y": float(getattr(point, column))}
                )
            new_features.append(
                {"TRACK": int(row.TRACK), "LABEL": label, "METHOD": "", "CURVE": curve_id}
            )
    product_curve_ids = set(products["CURVE"].astype(int))
    kept_curves = old_curves[old_curves["CURVE"].astype(int).isin(product_curve_ids)].copy()
    all_curves = pd.concat([kept_curves, pd.DataFrame(new_curves)], ignore_index=True)
    all_curves = all_curves.sort_values(["CURVE", "X"])
    features = pd.DataFrame(new_features)

    account_labels = [*list(FEATURE_MAP), "product.yield.managed.total"]
    accounts = pd.DataFrame(
        {
            "GROUP": "_MANAGED_",
            "ATTRIBUTE": account_labels,
            "ACCOUNT": account_labels,
            "SUM": 1,
        }
    )
    accounts.to_csv(args.h_dir / "accounts.csv", index=False)
    accounts.to_csv(args.h_dir / "protoaccounts.csv", index=False)
    features.to_csv(args.h_dir / "features.csv", index=False)
    all_curves.to_csv(args.h_dir / "curves.csv", index=False)
    manifest_path = args.h_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    manifest.update(
        {
            "status": "matrix-scaffold-space-for-time-features",
            "feature_horizon_years": int(curves["year"].max()),
            "product_horizon_years": 30,
            "curves": int(all_curves["CURVE"].nunique()),
            "curve_points": len(all_curves),
            "features": len(features),
            "feature_curves": int(features["CURVE"].nunique()),
            "feature_rows": len(features),
            "product_curves": len(product_curve_ids),
            "accounts": len(accounts),
            "space_for_time_mapping": "space_for_time_mapping.csv",
            "caveats": [
                "Feature curves are regional FAIB IDF space-for-time FVS-BC runs.",
                "Product curves remain the existing 30-year GWM treatment runs.",
                "Feature and product horizons differ (100 vs 30 years).",
                "Space-for-time is not a growth chronology and not a KC CFI.",
                "No large-tree-BA feature is claimed from this panel.",
            ],
        }
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"tracks={len(tracks)} features={len(features)} curves={len(all_curves)}")


if __name__ == "__main__":
    main()
