#!/usr/bin/env python3
"""Compile a spatial KC structural ws4 dataset with HMZ-restricted tracks.

Blocks are clipped VRI polygons. Each block is assigned to the nearest initial
canonical GWM state and to an HMZ group. Track copies enforce the HMZ matrix:

- M (HMZ 1/3/4): Low or Moderate only;
- L (HMZ 2): Low only;
- A (HMZ 5): all classes;
- U (outside HMZ): no treatments.

The result is a structural spatial dataset, not a KC operating model. Tree
lists are still PSP-derived and the clump rule is a DBH-ranked proxy.

Usage::

    PYTHONPATH=/path/to/ws4 python runbooks/compile_kc_spatial_dataset.py \
      --canonical ws4/state_library_v1/canonical \
      --vri data/inventory/vri_2025_kc.gpkg \
      --sup data/boundaries/knife_creek_sup_S15382.gpkg \
      --hmz-crosswalk data/habitat/kc_vri_hmz_overlay.csv \
      --out-dir ws4/dataset_kc_spatial_v1
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from ws4.model.api import Model
from ws4.model.schema import validate_dataset

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
HMZ_REGIMES = {
    "M": ("GWM_LOW", "GWM_MODERATE"),
    "L": ("GWM_LOW",),
    "A": ("GWM_HIGH", "GWM_MODERATE", "GWM_LOW"),
    "U": (),
}


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _class_value(state: str, names: dict[str, float]) -> float:
    for name, value in names.items():
        if f"__{name}__" in state:
            return value
    return float("nan")


def _nearest_initial(ba: float, qmd: float, initial: pd.DataFrame) -> str:
    best = initial.iloc[0]["state_id"]
    best_score = float("inf")
    for row in initial.itertuples(index=False):
        score = ((_class_value(row.state_id, BA_CENTRES) - ba) / 5.0) ** 2
        score += ((_class_value(row.state_id, QMD_CENTRES) - qmd) / 5.0) ** 2
        if score < best_score:
            best = row.state_id
            best_score = score
    return str(best)


def main() -> None:
    """Write and validate the spatial structural dataset."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--vri", type=Path, required=True)
    parser.add_argument("--sup", type=Path, required=True)
    parser.add_argument("--hmz-crosswalk", type=Path, required=True)
    parser.add_argument("--lidar-block-summary", type=Path)
    parser.add_argument("--lidar-reserve-summary", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    states = pd.read_csv(args.canonical / "states.csv")
    transitions = pd.read_csv(args.canonical / "transitions.csv")
    canonical_curves = pd.read_csv(args.canonical / "curves.csv")
    crosswalk = pd.read_csv(args.hmz_crosswalk)
    initial = states[(states["n_incoming"] == 0) & states["state_id"].str.contains("LT_NA")].copy()
    if initial.empty:
        raise ValueError("no initial canonical states")

    # One track copy per canonical state and HMZ group.
    track_ids: dict[tuple[str, str], int] = {}
    track_rows = []
    next_track = 1
    for state in states["state_id"]:
        for group in HMZ_REGIMES:
            track_ids[(state, group)] = next_track
            track_rows.append({"track_id": next_track, "name": f"{state}__HMZ_{group}"})
            next_track += 1
    tracks = pd.DataFrame(track_rows)

    # Shared canonical curves; features and products point at copies.
    curve_rows = []
    curve_ids: dict[tuple[str, str], int] = {}
    next_curve = 1
    for row in canonical_curves.itertuples(index=False):
        key = (str(row.transition_id), str(row.attribute))
        if key not in curve_ids:
            curve_ids[key] = next_curve
            next_curve += 1
        curve_rows.append({"curve_id": curve_ids[key], "x": float(row.x), "y": float(row.y)})
    curves = pd.DataFrame(curve_rows)

    treatment_rows = []
    feature_rows = []
    product_rows = []
    for row in transitions.itertuples(index=False):
        for group, allowed in HMZ_REGIMES.items():
            if row.regime not in allowed:
                continue
            from_id = track_ids[(row.from_state, group)]
            to_id = track_ids[(row.to_state, group)]
            treatment_rows.append(
                {
                    "track_id": from_id,
                    "begin": 30,
                    "end": 300,
                    "treatment": row.regime,
                    "new_track": to_id,
                    "offset": 0,
                    "retain": 0,
                }
            )
            for attribute, label in (
                ("ba", "feature.habitat.basal_area"),
                ("qmd", "feature.habitat.qmd"),
                ("canopy_ccf", "feature.habitat.canopy_ccf"),
            ):
                curve_id = curve_ids.get((str(row.transition_id), attribute))
                if curve_id is not None:
                    feature_rows.append({"track_id": from_id, "label": label, "curve_id": curve_id})
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
                    "track_id": from_id,
                    "treatment": row.regime,
                    "label": "product.yield.managed.total",
                    "curve_id": product_curve,
                }
            )
    treatments = pd.DataFrame(treatment_rows)
    features = pd.DataFrame(feature_rows)
    products = pd.DataFrame(product_rows)

    # Spatial blocks from clipped VRI.
    vri = gpd.read_file(args.vri).to_crs(3005)
    sup = gpd.read_file(args.sup).to_crs(3005)
    blocks_gdf = gpd.overlay(vri, sup[["geometry"]], how="intersection")
    blocks_gdf["area_ha"] = blocks_gdf.geometry.area / 10000.0
    blocks_gdf = blocks_gdf[
        (blocks_gdf["area_ha"] >= 0.1)
        & (blocks_gdf["BASAL_AREA"].fillna(0) > 0)
        & (blocks_gdf["VRI_LIVE_STEMS_PER_HA"].fillna(0) > 0)
    ].copy()
    blocks_gdf["qmd_cm"] = np.sqrt(
        blocks_gdf["BASAL_AREA"] / (0.00007854 * blocks_gdf["VRI_LIVE_STEMS_PER_HA"])
    )
    blocks_gdf = blocks_gdf.merge(
        crosswalk[["POLYGON_ID", "dominant_hmz", "dominant_code"]],
        on="POLYGON_ID",
        how="left",
    )
    blocks_gdf["hmz_group"] = blocks_gdf["dominant_code"].fillna("U")
    blocks_gdf["initial_state"] = blocks_gdf.apply(
        lambda row: _nearest_initial(row.BASAL_AREA, row.qmd_cm, initial),
        axis=1,
    )
    blocks_gdf["track_id"] = [
        track_ids[(state, group)]
        for state, group in zip(blocks_gdf["initial_state"], blocks_gdf["hmz_group"], strict=True)
    ]
    lidar = None
    if args.lidar_block_summary:
        lidar = pd.read_csv(args.lidar_block_summary)
        blocks_gdf = blocks_gdf.merge(
            lidar[
                [
                    "POLYGON_ID",
                    "large_clumps_per_ha",
                    "large_clumps_4_10",
                    "large_tph_ge20",
                ]
            ],
            on="POLYGON_ID",
            how="left",
        )
        blocks_gdf["clump_class"] = pd.cut(
            blocks_gdf["large_clumps_per_ha"],
            bins=[-0.01, 10.0, 20.0, 30.0, 1e9],
            labels=["CLUMP_LT10", "CLUMP10_20", "CLUMP20_30", "CLUMP30_PLUS"],
        ).astype(str)
        blocks_gdf["clump_class"] = blocks_gdf["clump_class"].fillna("CLUMP_NA")
    else:
        blocks_gdf["clump_class"] = "CLUMP_NA"
    reserve = None
    if args.lidar_reserve_summary:
        reserve = pd.read_csv(args.lidar_reserve_summary)
        blocks_gdf = blocks_gdf.merge(
            reserve[
                [
                    "POLYGON_ID",
                    "reserve_tph",
                    "harvest_tph",
                    "reserve_ba_est_m2_ha",
                    "clumps",
                ]
            ],
            on="POLYGON_ID",
            how="left",
        )
        blocks_gdf["reserve_class"] = pd.cut(
            blocks_gdf["reserve_tph"],
            bins=[-0.01, 20.0, 30.0, 1e9],
            labels=["RESERVE_LT20", "RESERVE20_30", "RESERVE30_PLUS"],
        ).astype(str)
        blocks_gdf["reserve_class"] = blocks_gdf["reserve_class"].fillna("RESERVE_NA")
    else:
        blocks_gdf["reserve_class"] = "RESERVE_NA"
    blocks_gdf = blocks_gdf.reset_index(drop=True)
    blocks = pd.DataFrame(
        {
            "block_id": range(1, len(blocks_gdf) + 1),
            "track_id": blocks_gdf["track_id"],
            "offset": 0,
            "area_ha": blocks_gdf["area_ha"],
        }
    )
    fragments = pd.DataFrame(
        {
            "fragment_id": range(1, len(blocks_gdf) + 1),
            "block_id": range(1, len(blocks_gdf) + 1),
            "area_ha": blocks_gdf["area_ha"],
            "age": blocks_gdf["PROJ_AGE_1"].fillna(0).astype(int),
            "track_id": blocks_gdf["track_id"],
        }
    )
    groups = pd.DataFrame(
        {
            "block_id": range(1, len(blocks_gdf) + 1),
            "group": "hmz_"
            + blocks_gdf["hmz_group"].astype(str)
            + "__"
            + blocks_gdf["clump_class"].astype(str)
            + "__"
            + blocks_gdf["reserve_class"].astype(str),
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
    accounts = pd.DataFrame(columns=["group", "attribute", "account", "sum"])
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
            "protoaccounts": accounts.copy(),
            "messages": pd.DataFrame(columns=["severity", "message"]),
        }
    )
    model.write(args.out_dir)
    manifest_path = args.out_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["sources"] = [
        {
            "path": str(args.canonical),
            "transitions_sha256": _hash(args.canonical / "transitions.csv"),
        },
        {"path": str(args.vri), "sha256": _hash(args.vri)},
        {"path": str(args.hmz_crosswalk), "sha256": _hash(args.hmz_crosswalk)},
    ]
    manifest["metadata"] = {
        "instance": "knife-creek",
        "basis": "GWM_2007",
        "status": "spatial-structural-fixture",
        "blocks": len(blocks),
        "area_ha": float(blocks["area_ha"].sum()),
        "hmz_groups": blocks_gdf["hmz_group"].value_counts().to_dict(),
        "clump_classes": blocks_gdf["clump_class"].value_counts().to_dict(),
        "reserve_classes": blocks_gdf["reserve_class"].value_counts().to_dict(),
        "caveats": [
            "Blocks are clipped VRI polygons, but tree lists are PSP-derived, not KC CFI.",
            "Initial canonical state is nearest BA/QMD class, not a measured state assignment.",
            (
                "Block groups use observed LiDAR clump and reserve classes; "
                "the FVS treatment reserve is still a DBH-ranked proxy."
            ),
            "HMZ track offers enforce the matrix; they are not a legal-compliance determination.",
            "No current approved-order verification.",
        ],
    }
    if lidar is not None:
        columns = [
            "POLYGON_ID",
            "hmz_group",
            "dominant_code",
            "clump_class",
            "reserve_class",
            "large_clumps_per_ha",
            "large_clumps_4_10",
            "large_tph_ge20",
        ]
        if reserve is not None:
            columns += ["reserve_tph", "harvest_tph", "reserve_ba_est_m2_ha", "clumps"]
        blocks_gdf[columns].to_csv(args.out_dir / "block_features.csv", index=False)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    problems = validate_dataset(args.out_dir)
    if problems:
        for problem in problems:
            print(f"{problem.code}: {problem.where}: {problem.message}")
        raise SystemExit(1)
    print(
        f"dataset={args.out_dir} blocks={len(blocks)} area_ha={blocks['area_ha'].sum():.1f} "
        f"tracks={len(tracks)} treatments={len(treatments)}"
    )


if __name__ == "__main__":
    main()
