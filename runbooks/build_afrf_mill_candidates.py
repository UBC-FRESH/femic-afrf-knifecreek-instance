#!/usr/bin/env python3
"""Build a candidate AFRF mill register from the BC major-processing-facilities layer.

The BC layer gives mill location, product class, status, and estimated annual
capacity. It does not give accepted log sorts or log demand. This runbook keeps
those limits explicit: it derives a *candidate sort* from the mill product class
and marks every sort as unconfirmed.

Usage::

    python runbooks/build_afrf_mill_candidates.py \
      --out-dir data/mills \
      --radius-km 100
"""

from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

import geopandas as gpd
import pandas as pd

LAYER_URL = (
    "https://maps.gov.bc.ca/arcgis/rest/services/"
    "whse/bcgw_pub_whse_imagery_and_base_maps/MapServer/54"
)
SOURCE_URL = "https://www.arcgis.com/home/item.html?id=70ec7d6020f24ac1a068d5f808b3cca6"
DATE_UPDATED_MS = 1781706027000  # 2026-06-17, from the published feature layer
PRODUCT_SORT = {
    "LBR": ("sawlog", "lumber mill: sawlog"),
    "PLY": ("peeler", "plywood mill: peeler/veneer log"),
    "VNR": ("peeler", "veneer mill: peeler log"),
    "PLP": ("pulpwood", "pulp mill: pulpwood/chips"),
    "PLT": ("pulpwood", "pellet mill: pulpwood/biomass"),
    "CHP": ("pulpwood", "chip mill: pulpwood/chips"),
    "PPR": ("pulpwood", "paper mill: pulpwood"),
    "LGH": ("house_log", "log home mill: house log"),
    "PLE": ("pole", "pole mill: pole/post"),
    "PST": ("pole", "post mill: pole/post"),
    "UTI": ("pole", "utility pole mill: pole"),
    "SS": ("minor", "shake/shingle mill: minor products"),
    "LVL": ("peeler", "LVL mill: peeler/veneer log"),
    "PNL": ("peeler", "panel mill: peeler/veneer log"),
    "SID": ("peeler", "siding mill: peeler/veneer log"),
}
CAPACITY_FIELDS = (
    ("EST_AN_CAP_MLN_BOARD_FT", "million_board_feet_lumber"),
    ("EST_AN_CAP_MLN_SQ_FT", "million_sq_ft_3_8_in"),
    ("EST_AN_CAP_000_TONNES", "thousand_tonnes"),
    ("EST_AN_CAP_MLN_CUBIC_FT", "million_cubic_feet"),
    ("EST_AN_CAP_000_PCS_6_LNL_FT", "thousand_pieces_6ft"),
    ("EST_AN_CAP_000_PCS_40_LNL_FT", "thousand_pieces_40ft"),
    ("EST_AN_CAP_000_PCS_42_LNL_FT", "thousand_pieces_42ft"),
)


def _fetch_mills(path: Path) -> None:
    """Fetch the BC mill layer as GeoJSON when the local copy is absent."""
    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
        "outSR": "4326",
    }
    url = LAYER_URL + "/query?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "femic-afrf-roads/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read()
    path.write_bytes(payload)


def _capacity(row: pd.Series) -> tuple[float | None, str]:
    """Return the reported capacity and its unit."""
    for field, unit in CAPACITY_FIELDS:
        value = row.get(field)
        if value is not None and pd.notna(value) and float(value) > 0.0:
            return float(value), unit
    return None, "unknown"


def main() -> None:
    """Build the candidate mill table and metadata."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument(
        "--knife-creek-fragments",
        type=Path,
        default=Path("data/patchworks_knifecreek/spatial_split/fragments.shp"),
    )
    parser.add_argument(
        "--gavin-fragments",
        type=Path,
        default=Path(
            "../femic-afrf-gavinlake-instance/data/legacy_gavinlake/spatial/fragments.shp"
        ),
    )
    parser.add_argument("--radius-km", type=float, default=100.0)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    source_path = args.out_dir / "bc_mills_source.geojson"
    if not source_path.exists():
        _fetch_mills(source_path)

    mills = gpd.read_file(source_path).to_crs(3005)
    knife = gpd.read_file(args.knife_creek_fragments).to_crs(3005)
    gavin = gpd.read_file(args.gavin_fragments).to_crs(3005)
    knife_centroid = knife.geometry.union_all().centroid
    gavin_centroid = gavin.geometry.union_all().centroid

    mills["knife_creek_km"] = mills.geometry.distance(knife_centroid) / 1000.0
    mills["gavin_lake_km"] = mills.geometry.distance(gavin_centroid) / 1000.0
    mills["nearest_block_km"] = mills[["knife_creek_km", "gavin_lake_km"]].min(axis=1)
    mills["nearest_block"] = mills.apply(
        lambda row: (
            "knife_creek" if row["knife_creek_km"] <= row["gavin_lake_km"] else "gavin_lake"
        ),
        axis=1,
    )
    candidates = mills[mills["nearest_block_km"] <= args.radius_km].copy()

    rows: list[dict[str, object]] = []
    for _, row in candidates.iterrows():
        product_code = str(row.get("PRODUCT_CODE") or "")
        sort, basis = PRODUCT_SORT.get(product_code, ("unknown", "unrecognised product code"))
        capacity_value, capacity_unit = _capacity(row)
        mill_id = str(row.get("MILL_ID") or "")
        destination = f"destination.MILL_{mill_id}_{product_code}"
        rows.append(
            {
                "destination": destination,
                "mill_id": mill_id,
                "company": row.get("COMPANY_NAME"),
                "locality": row.get("LOCALITY"),
                "street_address": row.get("STREET_ADDRESS"),
                "latitude": float(row.get("LATITUDE")) if pd.notna(row.get("LATITUDE")) else None,
                "longitude": float(row.get("LONGITUDE"))
                if pd.notna(row.get("LONGITUDE"))
                else None,
                "product_code": product_code,
                "status": row.get("STATUS"),
                "candidate_sort": sort,
                "sort_basis": basis,
                "capacity_value": capacity_value,
                "capacity_unit": capacity_unit,
                "capacity_basis": "estimated annual capacity, 2023 Mill List Survey",
                "knife_creek_km": round(float(row["knife_creek_km"]), 2),
                "gavin_lake_km": round(float(row["gavin_lake_km"]), 2),
                "nearest_block": row["nearest_block"],
                "nearest_block_km": round(float(row["nearest_block_km"]), 2),
                "source": "BC Major Timber Processing Facilities",
                "source_date": datetime.fromtimestamp(DATE_UPDATED_MS / 1000, tz=UTC)
                .date()
                .isoformat(),
                "source_url": SOURCE_URL,
                "sort_confirmed": False,
            }
        )

    table = pd.DataFrame(rows).sort_values(
        ["nearest_block", "nearest_block_km", "product_code", "company"]
    )
    table.to_csv(args.out_dir / "afrf_mill_candidates.csv", index=False)

    # A minimal destination table for review. It is not a route config until the
    # sort and eligibility questions are settled.
    destinations = table[
        [
            "destination",
            "mill_id",
            "company",
            "locality",
            "product_code",
            "candidate_sort",
            "capacity_value",
            "capacity_unit",
            "status",
        ]
    ].copy()
    destinations.to_csv(args.out_dir / "candidate_destinations.csv", index=False)

    metadata = {
        "source": "BC Major Timber Processing Facilities",
        "source_url": SOURCE_URL,
        "layer_url": LAYER_URL,
        "source_date": datetime.fromtimestamp(DATE_UPDATED_MS / 1000, tz=UTC).date().isoformat(),
        "query_date": datetime.now(UTC).date().isoformat(),
        "licence": "Open Government Licence - British Columbia",
        "radius_km": args.radius_km,
        "source_features": len(mills),
        "candidate_rows": len(table),
        "candidate_mills": int(table["mill_id"].nunique()),
        "blocks": {
            "knife_creek_centroid_epsg3005": [
                float(knife_centroid.x),
                float(knife_centroid.y),
            ],
            "gavin_lake_centroid_epsg3005": [
                float(gavin_centroid.x),
                float(gavin_centroid.y),
            ],
        },
        "caveats": [
            "Capacity is the published estimated annual capacity, not current demand.",
            "Accepted log sorts are inferred from the mill product class; they are not confirmed.",
            "The table is a candidate register, not a destination or eligibility model.",
            "The source layer is a 2023 survey published in 2026; verify current status.",
        ],
    }
    (args.out_dir / "mills_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"candidates={len(table)} mills={metadata['candidate_mills']}")


if __name__ == "__main__":
    main()
