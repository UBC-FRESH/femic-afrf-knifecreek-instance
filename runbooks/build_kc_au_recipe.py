#!/usr/bin/env python3
"""Compile the AU-aware KC ForestModelXML recipe.

The model has one natural and one managed state per AU. A selection treatment
moves natural to managed; the managed state can re-enter itself. This is a
two-state AU model, not a full BA/QMD state graph yet.

Usage::

    python runbooks/build_kc_au_recipe.py \
      --au-table data/kc_au/kc_au_table.csv \
      --assignment data/kc_au/kc_au_assignment.csv \
      --fragments data/patchworks_knifecreek/fragments.csv \
      --no-cut data/psp/kc_au_200y/kc_au_yield_200y.csv \
      --selection data/psp/kc_au_200y/kc_au_selection_200y.csv \
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
TREATMENT = "GWM_MODERATE"
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
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    au = pd.read_csv(args.au_table)
    assignment = pd.read_csv(args.assignment)[["POLYGON_ID", "au_id"]].rename(
        columns={"POLYGON_ID": "POLY_ID"}
    )
    fragments = pd.read_csv(args.fragments)
    no_cut = pd.read_csv(args.no_cut)
    selection = pd.read_csv(args.selection)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    fragments = fragments.merge(assignment, on="POLY_ID", how="left")
    if fragments["au_id"].isna().any():
        raise ValueError("one or more fragments have no AU")
    fragments["SILV"] = "natural"
    fragments["AU"] = fragments["au_id"]
    fragments["IFM"] = "managed"
    fragments["ORIGIN"] = "natural"
    fragments["RETENTION"] = 0.0
    fragments["TSA"] = "KC"
    fragments["FRAGMENT_ID"] = fragments["BLOCK"]
    fragments.to_csv(args.out_dir / "fragments.csv", index=False)

    root = ET.Element("ForestModel", horizon="200", year="2026", match="multi")
    ET.SubElement(root, "curve", id="unity").append(ET.Element("point", x="0", y="1"))
    area_curve = ET.SubElement(root, "curve", id="kc_area")
    ET.SubElement(area_curve, "point", x="0", y="1")
    ET.SubElement(area_curve, "point", x="200", y="1")

    ET.SubElement(root, "define", field="AU", column="AU")
    ET.SubElement(root, "define", field="SILV", column="SILV")
    ET.SubElement(root, "define", field="IFM", column="IFM")
    ET.SubElement(root, "define", field="ORIGIN", column="ORIGIN")
    ET.SubElement(root, "define", field="RETENTION", column="Number(column('RETENTION'))")
    ET.SubElement(root, "define", field="treatment")
    ET.SubElement(root, "input", block="BLOCK", area="AREA_HA", age="F_AGE")
    ET.SubElement(root, "output", messages="messages.csv")

    curve_index = 0

    def next_id(prefix: str) -> str:
        nonlocal curve_index
        curve_index += 1
        return f"{prefix}_{curve_index}"

    for row in au.itertuples(index=False):
        au_id = str(row.au_id)
        natural = no_cut[no_cut["au_id"] == au_id].sort_values("year")
        managed = selection[selection["au_id"] == au_id].sort_values("year")
        if natural.empty or managed.empty:
            raise ValueError(f"missing curves for {au_id}")
        managed = managed[managed["year"] >= ENTRY_YEAR].copy()
        managed["year"] = managed["year"] - ENTRY_YEAR
        feature_ids: dict[str, str] = {}
        for label, column in FEATURE_COLUMNS.items():
            curve_id = next_id("natural")
            _add_curve(root, curve_id, list(zip(natural["year"], natural[column], strict=True)))
            feature_ids[f"natural:{label}"] = curve_id
        for label, column in FEATURE_COLUMNS.items():
            curve_id = next_id("managed")
            _add_curve(root, curve_id, list(zip(managed["year"], managed[column], strict=True)))
            feature_ids[f"managed:{label}"] = curve_id
        cut_curve = next_id("cut")
        cut_row = managed[managed["year"] == 0]
        cut_value = float(cut_row["cut_m3_ha"].iloc[0]) if not cut_row.empty else 0.0
        _add_curve(root, cut_curve, [(0, cut_value)])

        for silv in ("natural", "managed"):
            select = ET.SubElement(
                root,
                "select",
                statement=f"AU eq '{au_id}' and SILV eq '{silv}'",
            )
            features = ET.SubElement(select, "features")
            for label in FEATURE_COLUMNS:
                _attribute(features, label, feature_ids[f"{silv}:{label}"])
            _attribute(features, "feature.area.managed.total", "kc_area")
            track = ET.SubElement(select, "track")
            treatment = ET.SubElement(
                track,
                "treatment",
                label=TREATMENT,
                minage=str(ENTRY_YEAR),
                maxage="200",
            )
            transition = ET.SubElement(treatment, "transition")
            ET.SubElement(transition, "assign", field="SILV", value="'managed'")

        product = ET.SubElement(
            root,
            "select",
            statement=f"AU eq '{au_id}' and treatment eq '{TREATMENT}'",
        )
        products = ET.SubElement(product, "products")
        _attribute(products, "product.yield.managed.total", cut_curve)

    ET.indent(root, space="  ")
    ET.ElementTree(root).write(
        args.out_dir / "forestmodel.xml", encoding="utf-8", xml_declaration=True
    )
    manifest = {
        "recipe": "kc-au-two-state-v1",
        "aus": len(au),
        "tracks": len(au) * 2,
        "selection_entry_year": ENTRY_YEAR,
        "treatment": TREATMENT,
        "caveats": [
            "Two states per AU: natural and managed.",
            "Managed is re-enterable but not a BA/QMD state graph.",
            "No calibration or legal-compliance claim.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
