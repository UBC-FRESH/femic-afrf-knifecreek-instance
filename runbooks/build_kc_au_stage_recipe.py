#!/usr/bin/env python3
"""Compile the KC AU/HMZ multi-entry stage recipe.

States are natural plus six post-entry stages per AU, HMZ and regime. The stage
graph follows the six FVS entries at years 30, 60, 90, 120, 150 and 180.

Usage::

    python runbooks/build_kc_au_stage_recipe.py \
      --au-table data/kc_au/kc_au_table.csv \
      --assignment data/kc_au/kc_au_assignment.csv \
      --fragments data/patchworks_knifecreek/fragments.csv \
      --no-cut data/psp/kc_au_200y/kc_au_yield_200y.csv \
      --multi-low data/psp/kc_au_200y/kc_au_multientry_low_200y.csv \
      --multi-moderate data/psp/kc_au_200y/kc_au_multientry_moderate_200y.csv \
      --out-dir data/kc_ws4_recipe_au_stages
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
ALLOWED_BY_HMZ = {"M": REGIMES, "A": REGIMES, "L": ("GWM_LOW",), "U": ()}
STAGES = tuple(range(1, 7))
ENTRY_YEAR = 30


def _add_curve(root: ET.Element, curve_id: str, points: list[tuple[int, float]]) -> None:
    """Append one curve."""
    element = ET.SubElement(root, "curve", id=curve_id)
    for x, y in sorted(points):
        ET.SubElement(element, "point", x=str(int(x)), y=f"{float(y):.6f}")


def _attribute(parent: ET.Element, label: str, curve_id: str) -> None:
    """Append one attribute."""
    attribute = ET.SubElement(parent, "attribute", label=label)
    ET.SubElement(attribute, "curve", idref=curve_id)


def _state(regime: str, stage: int) -> str:
    """Return the managed state name for a regime and entry stage."""
    return f"M{stage}_{regime.lower().removeprefix('gwm_')}"


def main() -> None:
    """Write the staged recipe and fragments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--au-table", type=Path, required=True)
    parser.add_argument("--assignment", type=Path, required=True)
    parser.add_argument("--fragments", type=Path, required=True)
    parser.add_argument("--no-cut", type=Path, required=True)
    parser.add_argument("--multi-low", type=Path, required=True)
    parser.add_argument("--multi-moderate", type=Path, required=True)
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
    multi = {
        "GWM_LOW": pd.read_csv(args.multi_low),
        "GWM_MODERATE": pd.read_csv(args.multi_moderate),
    }
    root = ET.Element("ForestModel", horizon="200", year="2026", match="multi")
    ET.SubElement(root, "curve", id="unity").append(ET.Element("point", x="0", y="1"))
    area = ET.SubElement(root, "curve", id="kc_area")
    ET.SubElement(area, "point", x="0", y="1")
    ET.SubElement(area, "point", x="200", y="1")
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
    for au_row in au.itertuples(index=False):
        au_id = str(au_row.au_id)
        natural = no_cut[no_cut["au_id"] == au_id].sort_values("year")
        if natural.empty:
            raise ValueError(f"missing no-cut curves for {au_id}")
        features: dict[str, dict[str, str]] = {"natural": {}}
        products: dict[str, str] = {}
        for label, column in FEATURE_COLUMNS.items():
            curve_id = next_id("natural")
            _add_curve(root, curve_id, list(zip(natural["year"], natural[column], strict=True)))
            features["natural"][label] = curve_id
        for regime in REGIMES:
            data = multi[regime][multi[regime]["au_id"] == au_id]
            if data.empty:
                raise ValueError(f"missing {regime} multi-entry curves for {au_id}")
            for stage in STAGES:
                state = _state(regime, stage)
                stage_data = data[data["stage"] == stage].sort_values("year")
                if stage_data.empty:
                    raise ValueError(f"missing {regime} stage {stage} for {au_id}")
                features[state] = {}
                for label, column in FEATURE_COLUMNS.items():
                    curve_id = next_id(state.lower())
                    _add_curve(
                        root,
                        curve_id,
                        list(zip(stage_data["year"], stage_data[column], strict=True)),
                    )
                    features[state][label] = curve_id
                cut_curve = next_id(f"cut_{state.lower()}")
                entry = stage_data[stage_data["year"] == 0]
                cut = float(entry["cut_m3_ha"].iloc[0]) if not entry.empty else 0.0
                _add_curve(root, cut_curve, [(0, cut)])
                products[state] = cut_curve

        for hmz in hmz_values:
            allowed = ALLOWED_BY_HMZ.get(hmz, ())
            natural_select = ET.SubElement(
                root,
                "select",
                statement=f"AU eq '{au_id}' and HMZ eq '{hmz}' and SILV eq 'natural'",
            )
            natural_features = ET.SubElement(natural_select, "features")
            for label in FEATURE_COLUMNS:
                _attribute(natural_features, label, features["natural"][label])
            _attribute(natural_features, "feature.area.managed.total", "kc_area")
            natural_track = ET.SubElement(natural_select, "track")
            for regime in allowed:
                treatment = ET.SubElement(
                    natural_track,
                    "treatment",
                    label=regime,
                    minage=str(ENTRY_YEAR),
                    maxage="200",
                )
                transition = ET.SubElement(treatment, "transition")
                ET.SubElement(
                    transition,
                    "assign",
                    field="SILV",
                    value=f"'{_state(regime, 1)}'",
                )
                product = ET.SubElement(
                    root,
                    "select",
                    statement=(
                        f"AU eq '{au_id}' and HMZ eq '{hmz}' and "
                        f"SILV eq 'natural' and treatment eq '{regime}'"
                    ),
                )
                _attribute(
                    ET.SubElement(product, "products"),
                    "product.yield.managed.total",
                    products[_state(regime, 1)],
                )
            for regime in allowed:
                for stage in STAGES:
                    state = _state(regime, stage)
                    managed_select = ET.SubElement(
                        root,
                        "select",
                        statement=(f"AU eq '{au_id}' and HMZ eq '{hmz}' and SILV eq '{state}'"),
                    )
                    managed_features = ET.SubElement(managed_select, "features")
                    for label in FEATURE_COLUMNS:
                        _attribute(managed_features, label, features[state][label])
                    _attribute(managed_features, "feature.area.managed.total", "kc_area")
                    if stage < STAGES[-1]:
                        managed_track = ET.SubElement(managed_select, "track")
                        treatment = ET.SubElement(
                            managed_track,
                            "treatment",
                            label=regime,
                            minage=str(ENTRY_YEAR),
                            maxage="200",
                        )
                        transition = ET.SubElement(treatment, "transition")
                        ET.SubElement(
                            transition,
                            "assign",
                            field="SILV",
                            value=f"'{_state(regime, stage + 1)}'",
                        )
                        product = ET.SubElement(
                            root,
                            "select",
                            statement=(
                                f"AU eq '{au_id}' and HMZ eq '{hmz}' and "
                                f"SILV eq '{state}' and treatment eq '{regime}'"
                            ),
                        )
                        product_attributes = ET.SubElement(product, "products")
                        _attribute(
                            product_attributes,
                            "product.yield.managed.total",
                            products[_state(regime, stage + 1)],
                        )

    ET.indent(root, space="  ")
    ET.ElementTree(root).write(
        args.out_dir / "forestmodel.xml", encoding="utf-8", xml_declaration=True
    )
    manifest = {
        "recipe": "kc-au-hmz-multientry-v1",
        "aus": len(au),
        "hmz_values": hmz_values,
        "stages": list(STAGES),
        "entry_years": [30, 60, 90, 120, 150, 180],
        "treatments": list(REGIMES),
        "caveats": [
            "Stage states are entry-sequence states, not a BA/QMD continuum.",
            "Residual x=0 uses the FVS post-treatment accounting.",
            "HMZ M/A both regimes, L low only, U none.",
            "No calibration or legal-compliance claim.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
