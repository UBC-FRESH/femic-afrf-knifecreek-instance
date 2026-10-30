#!/usr/bin/env python3
"""Fetch and clip BC Forest Tenure road sections for the KC SUP.

The output is a derived road layer for mapping and route work. It is not a
legal access determination and does not replace a field-verified AFRF road
inventory.

Usage::

    python runbooks/fetch_kc_roads.py \
      --sup data/boundaries/knife_creek_sup_S15382.gpkg \
      --out-dir data/patchworks_knifecreek/spatial
"""

from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path

import geopandas as gpd

WFS = "https://openmaps.gov.bc.ca/geo/pub/wfs"
TYPE = "pub:WHSE_FOREST_TENURE.FTEN_ROAD_SECTION_LINES_SVW"


def _fetch(bounds: tuple[float, float, float, float]) -> dict:
    """Fetch road sections in a WGS84 bounding box."""
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeName": TYPE,
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
        "bbox": f"{bounds[0]},{bounds[1]},{bounds[2]},{bounds[3]},EPSG:4326",
    }
    url = WFS + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "femic-kc-roads/1.0 (research)"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read())


def main() -> None:
    """Fetch, clip and write the road layer."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sup", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    sup = gpd.read_file(args.sup).to_crs(4326)
    payload = _fetch(tuple(float(value) for value in sup.total_bounds))
    frame = gpd.GeoDataFrame.from_features(payload["features"], crs=4326).to_crs(3005)
    frame = gpd.clip(frame, sup.to_crs(3005)[["geometry"]])
    frame = frame[~frame.geometry.is_empty].copy()
    frame["ROAD_ID"] = range(1, len(frame) + 1)
    frame["LENGTH_M"] = frame.geometry.length.round(1)
    output = frame[
        [
            "ROAD_ID",
            "ROAD_SECTION_ID",
            "ROAD_SECTION_NAME",
            "FOREST_FILE_ID",
            "FILE_STATUS_CODE",
            "LIFE_CYCLE_STATUS_CODE",
            "FILE_TYPE_DESCRIPTION",
            "LENGTH_M",
            "geometry",
        ]
    ].rename(
        columns={
            "ROAD_SECTION_ID": "SECTION_ID",
            "ROAD_SECTION_NAME": "ROAD_NAME",
            "FOREST_FILE_ID": "FILE_ID",
            "FILE_STATUS_CODE": "STATUS",
            "LIFE_CYCLE_STATUS_CODE": "LIFE_CYCLE",
            "FILE_TYPE_DESCRIPTION": "FILE_TYPE",
        }
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    output.to_file(args.out_dir / "roads.gpkg", driver="GPKG")
    output.drop(columns="geometry").to_csv(args.out_dir / "roads.csv", index=False)
    metadata = {
        "source": "BC Forest Tenure Road Section Lines",
        "wfs_type": TYPE,
        "licence": "Open Government Licence - British Columbia",
        "query_bbox_wgs84": [float(value) for value in sup.total_bounds],
        "features": len(output),
        "length_m": float(output["LENGTH_M"].sum()),
        "life_cycle": output["LIFE_CYCLE"].value_counts(dropna=False).to_dict(),
        "caveats": [
            "Derived public road sections, not a field-verified AFRF access inventory.",
            "No legal access, gate, bridge or haul-cost claim.",
            "Route configuration remains a separate task.",
        ],
    }
    (args.out_dir / "roads_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"roads={len(output)} length_m={metadata['length_m']:.1f}")


if __name__ == "__main__":
    main()
