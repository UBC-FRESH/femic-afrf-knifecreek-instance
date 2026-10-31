#!/usr/bin/env python3
"""Extract the AFRF road, landing, and harvest-system audit tables from MWP #3.

The 2007 AFRF Management and Working Plan #3 is public, but its road and
harvest-system material is spread across text, tables, and schematic maps. This
runbook transcribes the reviewable tables, renders the two Appendix 11 access
maps, and records the source hashes and page references.

The output is an audit surface. It is not a legal access layer and it does not
create road, mill, or log-price data that the plan does not contain.

Usage::

    python runbooks/build_mwp3_roads_audit.py \
      --pdf reference/AFRF-management-working-plan-3-2007.pdf \
      --out-dir data/roads
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import pymupdf

EXPECTED_SHA256 = "9bfd8b8f0449f45fb97fcf529236640ace09b73ba74f77001f677eee7307ff6a"
EXPECTED_PAGES = 168

TABLE37 = [
    # section, measure, unit, gavin_lake, knife_creek, total
    ("Net area", "net_area", "ha", 4922, 3117, 8040),
    ("Existing roads", "length", "km", 112.2, 86.2, 198.4),
    ("Existing roads", "right_of_way_area", "ha", 168.3, 129.3, 297.6),
    ("Existing roads", "density", "km/km2", 2.28, 2.76, 2.47),
    ("Existing roads", "area_share", "%", 3.4, 4.1, 3.7),
    ("Total chance planned roads", "length", "km", 136.1, 77.2, 213.3),
    ("Total chance planned roads", "right_of_way_area", "ha", 204.1, 115.9, 320.0),
    ("Total chance planned roads", "density", "km/km2", 2.77, 2.48, 2.65),
    ("Total chance planned roads", "area_share", "%", 4.1, 3.7, 4.0),
    ("Planned change in road density", "length", "km", 23.9, -9.0, 14.9),
    ("Planned change in road density", "right_of_way_area", "ha", 35.8, -13.4, 22.4),
    ("Planned change in road density", "density", "km/km2", 0.49, -0.28, 0.18),
    ("Planned change in road density", "area_share", "%", 0.7, -0.4, 0.3),
]

TABLE38 = [
    # surface_width, design_speed, sight, radius, fav_sustained, fav_short, adv_sustained, adv_short, switchbacks
    ("4", 20, 40, 15, 16, 18, 9, 12, 8),
    ("5-6", 30, 65, 35, 12, 14, 8, 10, 8),
    ("", 40, 95, 65, 12, 14, 8, 10, 8),
]

TABLE39 = [
    ("Net area", "net_area", "ha", 4922, 3117, 8040),
    ("Existing landings", "area", "ha", 24.1, 34.2, 58.3),
    ("Existing landings", "area_share", "%", 0.5, 1.1, 0.7),
]

HARVEST_SYSTEMS = [
    (
        "shortwood",
        "shortwood harvester/forwarder",
        "thinning; ground-based",
        "ground-based",
        "particularly well suited for thinning",
    ),
    (
        "feller-buncher/grapple skidder/processor",
        "feller-buncher, grapple skidder, processor",
        "clearcut; shortwood or long-log",
        "ground-based",
        "best suited to clearcutting",
    ),
    (
        "hand-falling/cable skidder/hand bucking",
        "hand falling, cable skidder, hand bucking",
        "large piece size, high value, salvage",
        "ground-based or cable",
        "best suited to large piece size, high value, or salvage",
    ),
    (
        "cable",
        "cable harvest system",
        "substantial area above 30% slope at Gavin Lake",
        "cable",
        "anticipated on Gavin Lake blocks with substantial area above 30% slope",
    ),
    (
        "inaccessible",
        "inaccessible",
        "areas above 60% slope",
        "inaccessible",
        "generally considered inaccessible above 60% slope",
    ),
]

ACCESS_ASSUMPTIONS = [
    ("maximum sustained favourable grade", "12", "%", "8.2.1", 109, 117),
    ("maximum sustained adverse grade", "8", "%", "8.2.1", 109, 117),
    ("maximum skid distance", "400", "m", "8.2.1", 109, 117),
    ("circular routes", "not allowed", "", "8.2.1", 109, 117),
    ("annual road construction program", "0.5-3", "km/year", "8.2.1", 110, 118),
    ("planned new-road build period", "15", "years", "8.2.1", 110, 118),
    (
        "annual cost of one percentage point of productive land in roads",
        "75000",
        "CAD/year",
        "8.2.1",
        109,
        117,
    ),
    ("salvage share of average annual harvest, 2001-2005", "18", "%", "8.1.3", 108, 116),
    ("partial-cutting share of Research Forest", "70", "%", "8.2.1", 110, 118),
    ("maximum landing area", "0.25", "ha", "8.2.2", 112, 120),
    ("landing service area", "30", "ha", "8.2.2", 112, 120),
    ("target skid-trail density", "10", "% of productive area", "8.2.3", 112, 120),
]


def _sha256(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_table37(out_dir: Path) -> None:
    """Write Table 37 in tidy form."""
    rows = [
        {
            "section": section,
            "measure": measure,
            "unit": unit,
            "gavin_lake": gavin,
            "knife_creek": knife,
            "total": total,
            "table": "37",
            "page": 110,
            "pdf_page": 118,
            "source": "AFRF Management and Working Plan #3, as of 2006",
        }
        for section, measure, unit, gavin, knife, total in TABLE37
    ]
    pd.DataFrame(rows).to_csv(out_dir / "mwp3_table37_roads.csv", index=False)


def _write_table38(out_dir: Path) -> None:
    """Write Table 38 in tidy form."""
    rows = []
    for index, values in enumerate(TABLE38):
        (
            surface_width,
            design_speed,
            sight,
            radius,
            fav_sustained,
            fav_short,
            adv_sustained,
            adv_short,
            switchbacks,
        ) = values
        rows.append(
            {
                "row": index + 1,
                "surface_width_m": surface_width,
                "design_speed_kmh": design_speed,
                "min_sight_distance_m": sight,
                "min_curve_radius_m": radius,
                "favorable_sustained_pct": fav_sustained,
                "favorable_short_pitch_pct": fav_short,
                "adverse_sustained_pct": adv_sustained,
                "adverse_short_pitch_pct": adv_short,
                "switchbacks_pct": switchbacks,
                "table": "38",
                "page": 110,
                "pdf_page": 118,
                "source": "AFRF Management and Working Plan #3, adapted from BC Ministry of Forests 2002",
            }
        )
    pd.DataFrame(rows).to_csv(out_dir / "mwp3_table38_specs.csv", index=False)


def _write_table39(out_dir: Path) -> None:
    """Write Table 39 in tidy form."""
    rows = [
        {
            "section": section,
            "measure": measure,
            "unit": unit,
            "gavin_lake": gavin,
            "knife_creek": knife,
            "total": total,
            "table": "39",
            "page": 112,
            "pdf_page": 120,
            "source": "AFRF Management and Working Plan #3, as of 2006",
        }
        for section, measure, unit, gavin, knife, total in TABLE39
    ]
    pd.DataFrame(rows).to_csv(out_dir / "mwp3_table39_landings.csv", index=False)


def _write_harvest_systems(out_dir: Path) -> None:
    """Write the harvest-system transect from section 8.1.1."""
    rows = [
        {
            "system_id": system_id,
            "system_name": system_name,
            "use_case": use_case,
            "access_class": access_class,
            "note": note,
            "section": "8.1.1",
            "page": 107,
            "pdf_page": 115,
            "source": "AFRF Management and Working Plan #3",
        }
        for system_id, system_name, use_case, access_class, note in HARVEST_SYSTEMS
    ]
    pd.DataFrame(rows).to_csv(out_dir / "mwp3_harvest_systems.csv", index=False)


def _write_access_assumptions(out_dir: Path) -> None:
    """Write the access and operational assumptions."""
    rows = [
        {
            "assumption": assumption,
            "value": value,
            "unit": unit,
            "section": section,
            "page": page,
            "pdf_page": pdf_page,
            "source": "AFRF Management and Working Plan #3",
        }
        for assumption, value, unit, section, page, pdf_page in ACCESS_ASSUMPTIONS
    ]
    pd.DataFrame(rows).to_csv(out_dir / "mwp3_access_assumptions.csv", index=False)


def _write_gap_register(out_dir: Path) -> None:
    """Write the source gaps that block a delivered-wood model."""
    rows = [
        {
            "gap_id": "G01",
            "category": "road geometry",
            "item": "AFRF road centerlines",
            "status": "missing",
            "evidence": "AFRF.zip AFRF/roads/ is empty; 02_build_roads.bsh references Roads_PW_v2.shp",
            "consequence": "No route network can be built from the legacy archive",
            "request": "Roads_PW_v2.shp or current equivalent",
        },
        {
            "gap_id": "G02",
            "category": "road geometry",
            "item": "Existing and planned road classification",
            "status": "partial",
            "evidence": "MWP #3 Table 37 and Appendix 11 give lengths and classes, but the maps are schematic",
            "consequence": "Length can be reconciled, but segment-level class and status cannot be assigned",
            "request": "AFRF road inventory with class, surface, status, and right-of-way width",
        },
        {
            "gap_id": "G03",
            "category": "road cost",
            "item": "Build, maintenance, haul, landing, and deactivation rates",
            "status": "missing",
            "evidence": "MWP #3 gives only the $75,000/year per 1% productive-land proxy and Table 38 specifications",
            "consequence": "Route cost accounts cannot use AFRF rates",
            "request": "AFRF road cost workbook or recent contract records",
        },
        {
            "gap_id": "G04",
            "category": "route model",
            "item": "Legacy route tables",
            "status": "missing",
            "evidence": "AFRF_H.pin has useRoutes = false; AFRF/roads/ is empty",
            "consequence": "No block-to-network linkage or destination table",
            "request": "vertices, segments, destinations, and linkages, or the inputs to rebuild them",
        },
        {
            "gap_id": "G05",
            "category": "mills",
            "item": "Mill register",
            "status": "missing",
            "evidence": "MWP #3 names interior sawmills and a log broker, but no mill list or capacities",
            "consequence": "Destinations and eligibility cannot be assigned",
            "request": "Mill name, location, operator, capacity, status, accepted species and sorts",
        },
        {
            "gap_id": "G06",
            "category": "mills",
            "item": "Accepted log sorts and mill demand",
            "status": "missing",
            "evidence": "No sort specifications or delivery constraints in the archive or OneDrive payload",
            "consequence": "Product eligibility and delivery constraints cannot be modelled",
            "request": "Mill sort specifications, minimum volumes, and current demand",
        },
        {
            "gap_id": "G07",
            "category": "log prices",
            "item": "Interior species-by-grade price list",
            "status": "missing",
            "evidence": "FEMIC ships coastal 2025 matrices; MWP #3 gives only a 1988-2005 value/cost trend",
            "consequence": "Value products would use a coastal or historical price basis",
            "request": "Dated interior log price list or AFRF sales/scaling records",
        },
        {
            "gap_id": "G08",
            "category": "log grades",
            "item": "AFRF grade distribution and scaling rules",
            "status": "missing",
            "evidence": "MWP #3 mentions grade 3 sawlogs and high-grade logs, but no grade rules",
            "consequence": "Grade volumes cannot be calibrated to AFRF sales",
            "request": "Scaling records, grade distributions, and sort specifications",
        },
        {
            "gap_id": "G09",
            "category": "harvest systems",
            "item": "Block-level system and prescription records",
            "status": "partial",
            "evidence": "MWP #3 gives system classes and slope thresholds; actual block records are absent",
            "consequence": "System classes can be inferred only from slope and access",
            "request": "Harvest-system records, prescriptions, and operational constraints",
        },
        {
            "gap_id": "G10",
            "category": "access",
            "item": "Gate, bridge, culvert, and legal-access status",
            "status": "missing",
            "evidence": "KC route-config note records these as absent",
            "consequence": "Modelled access is not legal or operational access",
            "request": "Access status layer and current approved plan or order",
        },
        {
            "gap_id": "G11",
            "category": "road geometry",
            "item": "Knife Creek public road completeness",
            "status": "partial",
            "evidence": "Public layer has 44 sections over 59.6 km; MWP #3 records 86.2 km existing",
            "consequence": "The public layer cannot be treated as the full AFRF network",
            "request": "AFRF road inventory or field-verified centerlines",
        },
        {
            "gap_id": "G12",
            "category": "road geometry",
            "item": "Gavin Lake road layer",
            "status": "missing",
            "evidence": "The Gavin Lake instance has no road layer",
            "consequence": "No Gavin route network",
            "request": "Gavin Lake road inventory or the legacy Roads_PW_v2.shp",
        },
        {
            "gap_id": "G13",
            "category": "reuse",
            "item": "TSA23 mill and cost values",
            "status": "not transferable",
            "evidence": "TSA23 route fixture has three mills and C5-class costs; no AFRF provenance",
            "consequence": "TSA23 numbers cannot be used as AFRF values",
            "request": "AFRF-specific mills, costs, and eligibility",
        },
        {
            "gap_id": "G14",
            "category": "log grades",
            "item": "TSA23 compiled log-grade products",
            "status": "not demonstrated",
            "evidence": "compiled_ft_econ, compiled_ft_econ_bc, and compiled_sf_risk contain no Logs_Grade labels",
            "consequence": "The TSA23 configuration is a template, not a proven compiled result",
            "request": "A compiled AFRF log-grade proof with an interior matrix",
        },
    ]
    pd.DataFrame(rows).to_csv(out_dir / "gap_register.csv", index=False)


def main() -> None:
    """Run the extraction and write the audit artifacts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    actual_sha256 = _sha256(args.pdf)
    if actual_sha256 != EXPECTED_SHA256:
        raise SystemExit(
            f"unexpected MWP #3 SHA-256: {actual_sha256}; expected {EXPECTED_SHA256}"
        )

    doc = pymupdf.open(args.pdf)
    if len(doc) != EXPECTED_PAGES:
        raise SystemExit(f"unexpected MWP #3 page count: {len(doc)}; expected {EXPECTED_PAGES}")

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    context_dir = out_dir / "context"
    context_dir.mkdir(parents=True, exist_ok=True)

    _write_table37(out_dir)
    _write_table38(out_dir)
    _write_table39(out_dir)
    _write_harvest_systems(out_dir)
    _write_access_assumptions(out_dir)
    _write_gap_register(out_dir)

    # PDF pages 165 and 166 carry the Gavin Lake and Knife Creek access plans.
    for page_number, name in ((165, "mwp3_gavin_access.jpg"), (166, "mwp3_knife_creek_access.jpg")):
        page = doc[page_number - 1]
        pix = page.get_pixmap(dpi=150)
        pix.save(context_dir / name, jpg_quality=85)

    text_pages = {
        "sections_8_1_8_2": [115, 116, 117, 118, 119, 120],
        "appendix_11": [165, 166],
    }
    text_path = out_dir / "mwp3_relevant_text.txt"
    chunks: list[str] = []
    for label, pages in text_pages.items():
        chunks.append(f"===== {label} =====")
        for page_number in pages:
            chunks.append(f"--- PDF page {page_number} ---")
            chunks.append(doc[page_number - 1].get_text())
    text_path.write_text("\n".join(chunks))

    manifest = {
        "source": "AFRF Management and Working Plan #3",
        "path": str(args.pdf),
        "sha256": actual_sha256,
        "pages": len(doc),
        "effective_period": "2007-01-01 to 2012-12-31",
        "publisher": "UBC Alex Fraser Research Forest",
        "licence": "public UBC AFRF planning document; UBC copyright, not OGL",
        "used_sections": {
            "8.1": "timber harvest systems, block harvesting, salvage, marking",
            "8.2": "access, roads, landings, skid trails",
            "Table 37": "road length and area, page 110",
            "Table 38": "road construction specifications, page 110",
            "Table 39": "landings, page 112",
            "Appendix 11": "Gavin Lake and Knife Creek access plans, pages 153-154",
        },
        "caveats": [
            "Appendix 11 maps are schematic: scale bar and north arrow, no coordinate grid.",
            "The plan does not contain mill capacities, accepted sorts, or a road unit-cost schedule.",
            "The plan is not a legal access determination.",
        ],
        "derived_tables": sorted(
            path.name for path in out_dir.glob("mwp3_*.csv")
        ),
        "context_images": sorted(path.name for path in context_dir.glob("*.*")),
    }
    (out_dir / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"source_manifest={out_dir / 'source_manifest.json'}")
    print(f"context_images={len(manifest['context_images'])} tables={len(manifest['derived_tables'])}")


if __name__ == "__main__":
    main()
