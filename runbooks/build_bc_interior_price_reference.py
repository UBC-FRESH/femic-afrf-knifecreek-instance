#!/usr/bin/env python3
"""Build the interior log-market and interior-grade reference tables.

The BC Interior Log Market Report gives average prices by species group and
log sort. It is not a mill-specific accepted-sort list and it is not a
grade-by-grade price matrix. This runbook transcribes the published 3-month
report (June-August 2026) and the five interior grade codes, and records the
source hashes and caveats.

Usage::

    python runbooks/build_bc_interior_price_reference.py \
      --out-dir data/log_prices \
      --report-pdf /path/to/3mi_aug_26.pdf \
      --grading-pdf /path/to/scale_ch9.pdf
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

REPORT_SHA256 = "e10b2d4bf3bbce6f247a34045bdc27fa0de0d6a9ff3d7bbe90d65c3e2a50f495"
GRADING_SHA256 = "0c9149c09c66092bf4f51feab09f1e72c8876c2c552fece9873a1cd5ef39441a"
REPORT_URL = (
    "https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/"
    "forestry/timber-pricing/interior-timber-pricing/"
    "interior-log-market-reports/3mi_aug_26.pdf"
)
GRADING_URL = (
    "https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/"
    "forestry/timber-pricing/harvest-billing/timber-scaling/scale_ch9.pdf"
)

# 3-month report, June 1, 2026 to August 31, 2026. Blank cells are no reported
# transactions, not zero price.
PRICES = [
    ("SPF", "Sawlog", 1_227_626, 114.34),
    ("SPF", "Peelers", 34_798, 140.90),
    ("SPF", "Pulpwood", 116_689, 52.91),
    ("Df-Larch", "Sawlog", 371_069, 124.41),
    ("Df-Larch", "Peelers", 65_860, 141.84),
    ("Df-Larch", "Pulpwood", 21_760, 60.76),
    ("Hem-Bal", "Sawlog", 113_957, 107.82),
    ("Hem-Bal", "Pulpwood", 7_063, 51.77),
    ("Cedar", "Sawlog", 81_294, 197.32),
    ("Other", "Other", 42_262, 72.72),
    ("Total/Avg", "Sawlog", 1_793_946, 119.77),
    ("Total/Avg", "Peelers", 100_658, 141.51),
    ("Total/Avg", "Pulpwood", 145_511, 54.03),
    ("Total/Avg", "Other", 42_262, 72.72),
]

GRADES = [
    ("Z", "Firmwood reject", "Reject grade for firmwood."),
    (
        "6",
        "Undersized",
        (
            "Undersized log; minimum 15 cm for lodgepole pine and 20 cm for "
            "other species at 15 cm from the butt."
        ),
    ),
    ("1", "Premium sawlog", "Premium sawlog grade."),
    ("2", "Sawlog", "Sawlog grade."),
    ("4", "Lumber reject", "Lumber reject grade."),
]


def _sha256(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    """Write the reference tables and metadata."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--report-pdf", type=Path)
    parser.add_argument("--grading-pdf", type=Path)
    args = parser.parse_args()

    if args.report_pdf and _sha256(args.report_pdf) != REPORT_SHA256:
        raise SystemExit("unexpected interior log-market report SHA-256")
    if args.grading_pdf and _sha256(args.grading_pdf) != GRADING_SHA256:
        raise SystemExit("unexpected interior grading SHA-256")

    args.out_dir.mkdir(parents=True, exist_ok=True)

    price_rows = [
        {
            "species_group": species,
            "row_type": "total_average" if species == "Total/Avg" else "species_group",
            "include_in_species_total": species != "Total/Avg",
            "sort": sort,
            "volume_m3": volume,
            "price_cad_m3": price,
            "price_basis": "reported average purchase price",
            "report_period": "2026-06-01/2026-08-31",
            "report_type": "3-month rolling",
            "source": "BC Interior Log Market Report",
            "source_url": REPORT_URL,
            "source_sha256": REPORT_SHA256,
            "caveat": (
                "Average reported price; individual transactions vary by quality, "
                "distance, and market."
            ),
        }
        for species, sort, volume, price in PRICES
    ]
    pd.DataFrame(price_rows).to_csv(
        args.out_dir / "bc_interior_log_market_2026-08.csv", index=False
    )

    grade_rows = [
        {
            "grade_code": code,
            "grade_name": name,
            "description": description,
            "source": "BC Timber Scaling Manual, Chapter 9, Interior Grading",
            "source_url": GRADING_URL,
            "source_sha256": GRADING_SHA256,
            "page": 2,
        }
        for code, name, description in GRADES
    ]
    pd.DataFrame(grade_rows).to_csv(args.out_dir / "bc_interior_grade_codes.csv", index=False)

    metadata = {
        "price_source": "BC Interior Log Market Report",
        "price_url": REPORT_URL,
        "price_sha256": REPORT_SHA256,
        "price_period": "2026-06-01/2026-08-31",
        "price_compiled": "2026-09-24",
        "price_units": "CAD/m3",
        "grade_source": "BC Timber Scaling Manual, Chapter 9, Interior Grading",
        "grade_url": GRADING_URL,
        "grade_sha256": GRADING_SHA256,
        "grade_codes": ["Z", "6", "1", "2", "4"],
        "caveats": [
            (
                "The log-market report is a species-group and sort average, not a "
                "mill-specific accepted-sort list."
            ),
            "Interior grades are Z/6/1/2/4, not the coastal D/F/H/I/J/U/X/Y grade family.",
            "The report is a regional market reference, not an AFRF sales record.",
            (
                "Do not apply the average price to an AFRF grade volume without a "
                "documented species and grade crosswalk."
            ),
        ],
    }
    (args.out_dir / "log_prices_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"prices={len(price_rows)} grades={len(grade_rows)}")


if __name__ == "__main__":
    main()
