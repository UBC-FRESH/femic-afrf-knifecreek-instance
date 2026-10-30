#!/usr/bin/env python3
"""Compile the AU-aware KC ForestModelXML recipe.

State: AU x HMZ x natural/managed. Treatment eligibility follows the KC HMZ
matrix:

- M and A: GWM_LOW or GWM_MODERATE;
- L: GWM_LOW only;
- U: no treatment.

The managed state can re-enter itself. This is still a two-state AU model, not a
full BA/QMD state graph.

Usage::

    python runbooks/build_kc_au_recipe.py \
      --au-table data/kc_au/kc_au_table.csv \
      --assignment data/kc_au/kc_au_assignment.csv \
      --fragments data/patchworks_knifecreek/fragments.csv \
      --no-cut data/psp/kc_au_200y/kc_au_yield_200y.csv \
      --selection-low data/psp/kc_au_200y/kc_au_selection_low_200y.csv \
      --selection-moderate data/psp/kc_au_200y/kc_au_selection_moderate_200y.csv \
      --out-dir data/kc_ws4_recipe_au
"""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

FEATURE_COLUMNS = {
    "feature.habitat.basal_area": "ba_m2_ha",
    "feature.habitat.qmd": "qmd_cm",
    "feature.habitat.tph": "tph",
    "feature.yield.managed.total": "volume_m3_ha",
    "feature.habitat.canopy_ccf": "canopy_ccf",
}
REGIMES = ("GWM_LOW", "GWM_MODERATE")
ALLOWED_BY_HMZ = {
    "M": REGIMES,
    "A": REGIMES,
    "L": ("GWM_LOW",),
    "U": (),
}
ENTRY_YEAR = 30


def _add_curve(root: ET.Element, curve_id: str, points: list[tuple[int, float]]) -> None:
    """Append a curve with sorted points."""
    element = ET.SubElement(root, "curve", id=curve_id)
    for x, y in sorted(points):
        ET.SubElement(element, "point", x=str(int(x)), y=f"{float(y):.6f}")


def _attribute(parent: ET.Element, label: str, curve_id: str) -> None:
    """Append one attribute."""
    attribute = ET.SubElement(parent, "attribute", label=label)
    ET.SubElement(attribute, "curve", idref=curve_id)


def main() -> None:
    """Write the AU recipe and AU fragments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--au-table", type=Path, required=True)
    parser.add_argument("--assignment", type=Path, required=True)
    parser.add_argument("--fragments", type=Path, required=True)
    parser.add_argument("--no-cut", type=Path, required=True)
    parser.add_argument("--selection-low", type=Path, required=True)
    parser.add_argument("--selection-moderate", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    au = pd.read_csv(args.au_table)
    assignment = pd.read_csv(args.assignment)[["POLYGON_ID", "au_id"]].rename(
        columns={"POLYGON_ID": "POLY_ID"}
    )
    fragments = pd.read_csv(args.fragments).merge(assignment, on="POLY_ID", how="left")
    if fragments["au_id"].isna().any():
        raise ValueError("one or more fragments have no AU")
    fragments["AU"] = fragments["au_id"]
    fragments["SILV"] = "natural"
    fragments["IFM"] = "managed"
    fragments["ORIGIN"] = "natural"
    fragments["RETENTION"] = 0.0
    fragments["TSA"] = "KC"
    fragments["FRAGMENT_ID"] = fragments["BLOCK"]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    fragments.to_csv(args.out_dir / "fragments.csv", index=False)

    no_cut = pd.read_csv(args.no_cut)
    selections = {
        "GWM_LOW": pd.read_csv(args.selection_low),
        "GWM_MODERATE": pd.read_csv(args.selection_moderate),
    }
    root = ET.Element("ForestModel", horizon="200", year="2026", match="multi")
    ET.SubElement(root, "curve", id="unity").append(ET.Element("point", x="0", y="1"))
    area_curve = ET.SubElement(root, "curve", id="kc_area")
    ET.SubElement(area_curve, "point", x="0", y="1")
    ET.SubElement(area_curve, "point", x="200", y="1")

    for field, column in (
        ("AU", "AU"),
        ("HMZ", "HMZ"),
        ("SILV", "SILV"),
        ("IFM", "IFM"),
        ("ORIGIN", "ORIGIN"),
        ("RETENTION", "Number(column('RETENTION'))"),
    ):
        ET.SubElement(root, "define", field=field, column=column)
    ET.SubElement(root, "define", field="treatment")
    ET.SubElement(root, "input", block="BLOCK", area="AREA_HA", age="F_AGE")
    ET.SubElement(root, "output", messages="messages.csv")

    curve_index = 0

    def next_id(prefix: str) -> str:
        nonlocal curve_index
        curve_index += 1
        return f"{prefix}_{curve_index}"

    hmz_values = sorted(str(value) for value in fragments["HMZ"].dropna().unique())
    for row in au.itertuples(index=False):
        au_id = str(row.au_id)
        natural = no_cut[no_cut["au_id"] == au_id].sort_values("year")
        if natural.empty:
            raise ValueError(f"missing no-cut curves for {au_id}")
        state_for = {"GWM_LOW": "managed_low", "GWM_MODERATE": "managed_moderate"}
        feature_ids: dict[str, dict[str, str]] = {"natural": {}}
        for label, column in FEATURE_COLUMNS.items():
            curve_id = next_id("natural")
            _add_curve(root, curve_id, list(zip(natural["year"], natural[column], strict=True)))
            feature_ids["natural"][label] = curve_id

        product_ids: dict[str, str] = {}
        for regime in REGIMES:
            managed = selections[regime][selections[regime]["au_id"] == au_id].sort_values("year")
            if managed.empty:
                raise ValueError(f"missing {regime} curves for {au_id}")
            post = managed[managed["year"] >= ENTRY_YEAR].copy()
            post["year"] = post["year"] - ENTRY_YEAR
            state = state_for[regime]
            feature_ids[state] = {}
            for label, column in FEATURE_COLUMNS.items():
                curve_id = next_id(f"{state.lower()}")
                _add_curve(root, curve_id, list(zip(post["year"], post[column], strict=True)))
                feature_ids[state][label] = curve_id
            cut_curve = next_id(f"cut_{regime.lower()}")
            entry = post[post["year"] == 0]
            cut = float(entry["cut_m3_ha"].iloc[0]) if not entry.empty else 0.0
            _add_curve(root, cut_curve, [(0, cut)])
            product_ids[regime] = cut_curve

        for hmz in hmz_values:
            allowed = ALLOWED_BY_HMZ.get(hmz, ())
            natural_select = ET.SubElement(
                root,
                "select",
                statement=f"AU eq '{au_id}' and HMZ eq '{hmz}' and SILV eq 'natural'",
            )
            features = ET.SubElement(natural_select, "features")
            for label in FEATURE_COLUMNS:
                _attribute(features, label, feature_ids["natural"][label])
            _attribute(features, "feature.area.managed.total", "kc_area")
            track = ET.SubElement(natural_select, "track")
            for regime in allowed:
                treatment = ET.SubElement(
                    track,
                    "treatment",
                    label=regime,
                    minage=str(ENTRY_YEAR),
                    maxage="200",
                )
                transition = ET.SubElement(treatment, "transition")
                ET.SubElement(transition, "assign", field="SILV", value=f"'{state_for[regime]}'")
            for regime in allowed:
                state = state_for[regime]
                managed_select = ET.SubElement(
                    root,
                    "select",
                    statement=f"AU eq '{au_id}' and HMZ eq '{hmz}' and SILV eq '{state}'",
                )
                managed_features = ET.SubElement(managed_select, "features")
                for label in FEATURE_COLUMNS:
                    _attribute(managed_features, label, feature_ids[state][label])
                _attribute(managed_features, "feature.area.managed.total", "kc_area")
                managed_track = ET.SubElement(managed_select, "track")
                treatment = ET.SubElement(
                    managed_track,
                    "treatment",
                    label=regime,
                    minage=str(ENTRY_YEAR),
                    maxage="200",
                )
                transition = ET.SubElement(treatment, "transition")
                ET.SubElement(transition, "assign", field="SILV", value=f"'{state}'")
                product = ET.SubElement(
                    root,
                    "select",
                    statement=(f"AU eq '{au_id}' and HMZ eq '{hmz}' and treatment eq '{regime}'"),
                )
                products = ET.SubElement(product, "products")
                _attribute(products, "product.yield.managed.total", product_ids[regime])

    ET.indent(root, space="  ")
    ET.ElementTree(root).write(
        args.out_dir / "forestmodel.xml", encoding="utf-8", xml_declaration=True
    )
    manifest = {
        "recipe": "kc-au-hmz-two-state-v1",
        "aus": len(au),
        "hmz_values": hmz_values,
        "tracks": "AU x HMZ x natural/managed",
        "selection_entry_year": ENTRY_YEAR,
        "treatments": list(REGIMES),
        "caveats": [
            "Two states per AU/HMZ: natural and managed.",
            "Managed is re-enterable but not a BA/QMD state graph.",
            "HMZ treatment eligibility follows M/A both classes, L low only, U none.",
            "No calibration or legal-compliance claim.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
