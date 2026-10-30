#!/usr/bin/env python3
"""Build the Patchworks-compatible Knife Creek fragments layer.

The layer is clipped from VRI 2025 to SUP S15382 and keyed to the existing
`dataset_kc_spatial_v3` block order. Only the spatial fragment layer is built
here; tracks/H, roads, topology, accounts and ForestModelXML are later P3 tasks.

Usage::

    python runbooks/build_kc_patchworks_fragments.py \
      --vri data/inventory/vri_2025_kc.gpkg \
      --sup data/boundaries/knife_creek_sup_S15382.gpkg \
      --dataset ws4/dataset_kc_spatial_v3 \
      --out-dir data/patchworks_knifecreek
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

EPSG = 3005


def main() -> None:
    """Build fragments.shp, fragments.csv and the fragment manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vri", type=Path, required=True)
    parser.add_argument("--sup", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    vri = gpd.read_file(args.vri).to_crs(EPSG)
    sup = gpd.read_file(args.sup).to_crs(EPSG)
    features = pd.read_csv(args.dataset / "block_features.csv")
    blocks = pd.read_parquet(args.dataset / "blocks.parquet")
    fragments = pd.read_parquet(args.dataset / "fragments.parquet")
    if len(features) != len(blocks) or len(blocks) != len(fragments):
        raise ValueError("block_features, blocks and fragments are not one-to-one")

    clipped = gpd.overlay(vri, sup[["geometry"]], how="intersection")
    clipped["area_ha"] = clipped.geometry.area / 10000.0
    clipped = clipped[
        (clipped["area_ha"] >= 0.1)
        & (clipped["BASAL_AREA"].fillna(0) > 0)
        & (clipped["VRI_LIVE_STEMS_PER_HA"].fillna(0) > 0)
    ].copy()
    if len(clipped) != len(features):
        raise ValueError(f"clipped VRI has {len(clipped)} rows, expected {len(features)}")

    geometry = clipped[
        ["POLYGON_ID", "BEC_ZONE_CODE", "BEC_SUBZONE", "BEC_VARIANT", "geometry"]
    ].drop_duplicates("POLYGON_ID")
    frame = features.merge(geometry, on="POLYGON_ID", how="left")
    if frame.geometry.isna().any():
        raise ValueError("missing geometry for one or more block_features rows")

    frame["block_id"] = range(1, len(frame) + 1)
    if not (frame["block_id"].to_numpy() == blocks["block_id"].to_numpy()).all():
        raise ValueError("block order does not match dataset blocks")
    if not (frame["block_id"].to_numpy() == fragments["block_id"].to_numpy()).all():
        raise ValueError("block order does not match dataset fragments")
    frame["TRACK"] = blocks["track_id"].to_numpy()
    frame["AREA_HA"] = blocks["area_ha"].to_numpy()
    frame["F_AGE"] = fragments["age"].to_numpy()
    frame["RES_KEY"] = frame["block_id"]
    frame["BLOCK"] = frame["block_id"]
    frame["POLY_ID"] = frame["POLYGON_ID"]
    frame["CONTCLAS"] = "C"
    frame["BEC"] = (
        frame["BEC_ZONE_CODE"].astype(str)
        + frame["BEC_SUBZONE"].astype(str)
        + frame["BEC_VARIANT"].fillna("").astype(str)
    )
    frame["HMZ"] = frame["hmz_group"].astype(str)
    frame["CLUMP"] = frame["clump_class"].astype(str)
    frame["RESERVE"] = frame["reserve_class"].astype(str)
    frame["AREA_HA"] = frame["AREA_HA"].astype(float)
    frame["F_AGE"] = frame["F_AGE"].astype(int)

    output = frame[
        [
            "RES_KEY",
            "BLOCK",
            "TRACK",
            "AREA_HA",
            "F_AGE",
            "BEC",
            "CONTCLAS",
            "HMZ",
            "CLUMP",
            "RESERVE",
            "POLY_ID",
            "geometry",
        ]
    ].rename(
        columns={
            "RES_KEY": "RES_KEY",
            "BLOCK": "BLOCK",
            "TRACK": "TRACK",
            "AREA_HA": "AREA_HA",
            "F_AGE": "F_AGE",
            "BEC": "BEC",
            "CONTCLAS": "CONTCLAS",
            "HMZ": "HMZ",
            "CLUMP": "CLUMP",
            "RESERVE": "RESERVE",
            "POLY_ID": "POLY_ID",
        }
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "spatial").mkdir(parents=True, exist_ok=True)
    output = gpd.GeoDataFrame(output, geometry="geometry", crs=EPSG)
    output.to_file(args.out_dir / "spatial" / "fragments.shp", driver="ESRI Shapefile")
    frame[
        [
            "BLOCK",
            "TRACK",
            "AREA_HA",
            "F_AGE",
            "RES_KEY",
            "POLY_ID",
            "BEC",
            "CONTCLAS",
            "HMZ",
            "CLUMP",
            "RESERVE",
        ]
    ].to_csv(args.out_dir / "fragments.csv", index=False)
    manifest = {
        "layer": "kc-patchworks-fragments-v1",
        "blocks": len(frame),
        "area_ha": float(frame["AREA_HA"].sum()),
        "crs": "EPSG:3005",
        "source": {
            "vri": str(args.vri),
            "sup": str(args.sup),
            "dataset": str(args.dataset),
        },
        "keys": {
            "RES_KEY": "stable block key",
            "BLOCK": "ws4/Patchworks block id",
            "TRACK": "initial ws4 state track",
        },
        "attributes": [
            "AREA_HA",
            "F_AGE",
            "BEC",
            "CONTCLAS",
            "HMZ",
            "CLUMP",
            "RESERVE",
            "POLY_ID",
        ],
        "caveats": [
            "The block order is inherited from dataset_kc_spatial_v3.",
            "F_AGE is VRI projected age, not a measured stand age.",
            "No absolute PSP plot centres or treatment polygons are included.",
            "tracks/H, topology, roads, accounts and ForestModelXML are later P3 tasks.",
        ],
    }
    (args.out_dir / "fragments_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"fragments={len(frame)} area_ha={frame['AREA_HA'].sum():.2f}")


if __name__ == "__main__":
    main()
