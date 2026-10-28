#!/usr/bin/env python3
"""Fetch and clip the Cariboo mule-deer habitat-management-zone layer.

Source: BC Map Hub / DataBC, "Habitat Management Zones Within Mule Deer Winter
Range - Cariboo Region", layer 8 of
bcgw_pub_reg_land_and_natural_resource. Licence: Open Government Licence - BC.

The derived layer is clipped to the Knife Creek SUP S15382. It is a public
spatial layer for the legal order's HMZ matrix; it is not a substitute for the
current approved order or a legal-compliance opinion.

Usage::

    python runbooks/fetch_mdwr_hmz.py \
      --out-dir data/habitat
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

import geopandas as gpd
import requests

SERVICE = (
    "https://maps.gov.bc.ca/arcgis/rest/services/whse/"
    "bcgw_pub_reg_land_and_natural_resource/MapServer/8/query"
)
SUP = Path("data/boundaries/knife_creek_sup_S15382.gpkg")
FIELDS = (
    "MULE_DEER_HAB_MG_ZN_CAR_ID",
    "HABITAT_MGMT_ZONE",
    "TIMBER_HARVEST_OPP_CODE",
    "TIMBER_HARVEST_OPP_DESC",
    "UWR_INFO_URL",
    "FEATURE_AREA_SQM",
    "FEATURE_LENGTH_M",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    """Fetch, clip and write the HMZ layer and area summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path("data/habitat"))
    args = parser.parse_args()
    sup = gpd.read_file(SUP).to_crs(3005)
    xmin, ymin, xmax, ymax = sup.total_bounds
    params = {
        "where": "1=1",
        "geometry": f"{xmin},{ymin},{xmax},{ymax}",
        "geometryType": "esriGeometryEnvelope",
        "inSR": "3005",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": "3005",
        "f": "geojson",
    }
    response = requests.get(SERVICE, params=params, timeout=120)
    response.raise_for_status()
    raw = gpd.GeoDataFrame.from_features(response.json()["features"])
    raw = raw.set_crs(3005, allow_override=True)
    raw = raw[raw["HABITAT_MGMT_ZONE"].astype(str).str.startswith("dwl_50_")].copy()
    clipped = gpd.overlay(raw, sup[["geometry"]], how="intersection")
    clipped["area_ha"] = clipped.geometry.area / 10000.0
    clipped["HMZ"] = clipped["HABITAT_MGMT_ZONE"].str.extract(r"dwl_50_(\d+)").astype(int)
    clipped = clipped[
        [
            "HMZ",
            "HABITAT_MGMT_ZONE",
            "TIMBER_HARVEST_OPP_CODE",
            "TIMBER_HARVEST_OPP_DESC",
            "UWR_INFO_URL",
            "area_ha",
            "geometry",
        ]
    ].sort_values("HMZ")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / "mule_deer_hmz_kc.gpkg"
    clipped.to_file(out, driver="GPKG")
    summary = (
        clipped.groupby(["HMZ", "HABITAT_MGMT_ZONE", "TIMBER_HARVEST_OPP_CODE"], as_index=False)[
            "area_ha"
        ]
        .sum()
        .sort_values("HMZ")
    )
    summary.to_csv(args.out_dir / "mule_deer_hmz_kc.csv", index=False)
    metadata = {
        "source": "BC Map Hub / DataBC",
        "item": "Mule Deer Winter Range Habitat Management Zones - Cariboo Region",
        "arcgis_item": "96151b4539c4437897e3ec3324037db2",
        "query_url": SERVICE,
        "licence": "Open Government Licence - British Columbia",
        "retrieved": date.today().isoformat(),
        "clip": "SUP S15382, EPSG:3005",
        "unit_filter": "HABITAT_MGMT_ZONE starts with dwl_50_",
        "features": len(clipped),
        "area_ha": float(clipped["area_ha"].sum()),
        "sha256": _sha(out),
        "caveats": [
            "Public spatial layer; verify the current approved order before a compliance claim.",
            "HMZ is a spatial constraint; a stand-level run alone is not compliance.",
            "The layer does not replace the legal UWR boundary or stand-structure map.",
        ],
    }
    (args.out_dir / "mule_deer_hmz_kc.metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )
    print(summary.to_string(index=False))
    print(f"features={len(clipped)} area_ha={clipped['area_ha'].sum():.2f}")


if __name__ == "__main__":
    main()
