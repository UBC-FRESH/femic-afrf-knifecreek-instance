#!/usr/bin/env python3
"""Assign the Knife Creek VRI polygons to mule-deer HMZ areas.

The output is a polygon-level area crosswalk, not a treatment decision. It lets
later block/AU construction carry the HMZ class and the legal harvest-opportunity
code without re-running the overlay.

Usage::

    python runbooks/assign_hmz.py \
      --vri data/inventory/vri_2025_kc.gpkg \
      --hmz data/habitat/mule_deer_hmz_kc.gpkg \
      --out-dir data/habitat
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd


def main() -> None:
    """Write the VRI-HMZ area crosswalk."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vri", type=Path, required=True)
    parser.add_argument("--hmz", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    vri = gpd.read_file(args.vri).to_crs(3005)
    hmz = gpd.read_file(args.hmz).to_crs(3005)
    overlay = gpd.overlay(
        vri[["POLYGON_ID", "POLYGON_AREA", "geometry"]],
        hmz[["HMZ", "TIMBER_HARVEST_OPP_CODE", "geometry"]],
        how="intersection",
    )
    overlay["area_ha"] = overlay.geometry.area / 10000.0
    pivot = (
        overlay.pivot_table(
            index="POLYGON_ID",
            columns="HMZ",
            values="area_ha",
            aggfunc="sum",
            fill_value=0.0,
        )
        .add_prefix("hmz_")
        .reset_index()
    )
    codes = (
        overlay.sort_values("area_ha", ascending=False)
        .drop_duplicates("POLYGON_ID")[["POLYGON_ID", "HMZ", "TIMBER_HARVEST_OPP_CODE"]]
        .rename(columns={"HMZ": "dominant_hmz", "TIMBER_HARVEST_OPP_CODE": "dominant_code"})
    )
    total = (
        overlay.groupby("POLYGON_ID", as_index=False)["area_ha"]
        .sum()
        .rename(columns={"area_ha": "overlay_area_ha"})
    )
    crosswalk = total.merge(pivot, on="POLYGON_ID", how="left").merge(
        codes, on="POLYGON_ID", how="left"
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    crosswalk.to_csv(args.out_dir / "kc_vri_hmz_overlay.csv", index=False)
    summary = (
        overlay.groupby(["HMZ", "TIMBER_HARVEST_OPP_CODE"], as_index=False)["area_ha"]
        .sum()
        .sort_values("HMZ")
    )
    summary.to_csv(args.out_dir / "kc_vri_hmz_summary.csv", index=False)
    metadata = {
        "vri": str(args.vri),
        "hmz": str(args.hmz),
        "crs": "EPSG:3005",
        "polygons": int(crosswalk["POLYGON_ID"].nunique()),
        "overlay_area_ha": float(overlay["area_ha"].sum()),
        "caveats": [
            "HMZ is a spatial legal constraint; the crosswalk is not a treatment decision.",
            "Dominant HMZ is the largest area share, not a legal interpretation.",
            "Verify the current approved order before a compliance claim.",
        ],
    }
    (args.out_dir / "kc_vri_hmz_overlay.metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )
    print(summary.to_string(index=False))
    print(f"polygons={crosswalk['POLYGON_ID'].nunique()} area_ha={overlay['area_ha'].sum():.2f}")


if __name__ == "__main__":
    main()
