#!/usr/bin/env python3
"""Build the KC ForestModelXML recipe and matrix-builder fragments.

The ws4 compiler consumes a ForestModelXML recipe plus a fragment inventory
(``ws4 build --xml ... --fragments ...``).  This runbook turns the validated KC
H-matrix tables into that recipe.  It preserves the H-matrix state dimensions,
treatment windows and target tracks, and every feature/product curve reference.

The recipe is deliberately generated from the current source matrix rather than
hand-written, so a curve or treatment change can be recompiled deterministically.

Usage::

    python runbooks/build_kc_forestmodel_xml.py \
      --h-dir data/patchworks_knifecreek/tracks/H \
      --fragments data/patchworks_knifecreek/fragments.csv \
      --out-dir data/kc_ws4_recipe
"""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

STATE_FIELDS = ("GWM", "BA", "QMD", "LT", "RES", "HMZ")
EXPECTED_TRACK_PARTS = len(STATE_FIELDS)


def _state_from_name(name: str) -> dict[str, str]:
    """Split a KC track name into its six state dimensions."""
    parts = name.split("__")
    if len(parts) != EXPECTED_TRACK_PARTS:
        raise ValueError(f"unexpected track name: {name!r}")
    return dict(zip(STATE_FIELDS, parts, strict=True))


def _add_curve(root: ET.Element, curve_id: str, points: pd.DataFrame) -> None:
    """Append a curve element with its points in x order."""
    element = ET.SubElement(root, "curve", id=curve_id)
    for row in points.sort_values("X").itertuples(index=False):
        ET.SubElement(element, "point", x=f"{row.X:g}", y=f"{row.Y:g}")


def _statement(state: dict[str, str], treatment: str | None = None) -> str:
    """Build a ForestModelXML select statement for a KC state."""
    terms = ["AU eq 1", "IFM eq 'managed'"]
    terms.extend(f"{field} eq '{state[field]}'" for field in STATE_FIELDS)
    if treatment is not None:
        terms.append(f"treatment eq '{treatment}'")
    return " and ".join(terms)


def _attrs(parent: ET.Element, rows: pd.DataFrame, curve_prefix: str) -> None:
    """Append feature/product attributes from a table of labels and curve ids."""
    for row in rows.itertuples(index=False):
        attribute = ET.SubElement(parent, "attribute", label=str(row.LABEL))
        ET.SubElement(attribute, "curve", idref=f"{curve_prefix}{int(row.CURVE)}")


def _build_recipe(h_dir: Path) -> tuple[ET.Element, pd.DataFrame, pd.DataFrame]:
    """Return the recipe root and the track/state tables."""
    tracks = pd.read_csv(h_dir / "tracknames.csv")
    states = tracks.assign(**pd.DataFrame([_state_from_name(name) for name in tracks["STRATA"]]))
    start_by_track = {
        int(row.TRACK): _state_from_name(row.STRATA) for row in tracks.itertuples(index=False)
    }

    root = ET.Element("ForestModel", horizon="100", year="2026", match="multi")
    ET.SubElement(root, "curve", id="unity").append(ET.Element("point", x="0", y="1"))
    curves = pd.read_csv(h_dir / "curves.csv")
    for curve_id, points in curves.groupby("CURVE", sort=True):
        _add_curve(root, f"kc_{int(curve_id)}", points)

    # The source matrix carries a constant AU=1.  The six KC state dimensions
    # are the real track dimensions; IFM/ORIGIN/RETENTION remain explicit so the
    # recipe is valid ForestModelXML and the semantics stay separate.
    ET.SubElement(root, "define", field="AU", column="AU")
    for field in STATE_FIELDS:
        ET.SubElement(root, "define", field=field, column=field)
    ET.SubElement(root, "define", field="IFM", column="IFM")
    ET.SubElement(root, "define", field="ORIGIN", column="ORIGIN")
    ET.SubElement(root, "define", field="RETENTION", column="Number(column('RETENTION'))")
    ET.SubElement(root, "define", field="treatment")
    ET.SubElement(root, "input", block="BLOCK", area="AREA_HA", age="F_AGE")
    ET.SubElement(
        root,
        "output",
        messages="messages.csv",
        blocks="blocks.csv",
        features="features.csv",
        products="products.csv",
        treatments="treatments.csv",
        curves="curves.csv",
        tracknames="tracknames.csv",
    )

    features = pd.read_csv(h_dir / "features.csv")
    products = pd.read_csv(h_dir / "products.csv")
    treatments = pd.read_csv(h_dir / "treatments.csv")

    known_tracks = set(start_by_track)
    if not set(treatments["NEWTRACK"].astype(int)).issubset(known_tracks):
        missing = sorted(set(treatments["NEWTRACK"].astype(int)) - known_tracks)
        raise ValueError(f"treatments point at unknown tracks: {missing}")

    for track_id, state in start_by_track.items():
        feature_rows = features.loc[features["TRACK"] == track_id]
        track_treatments = treatments.loc[treatments["TRACK"] == track_id]
        if feature_rows.empty and track_treatments.empty:
            continue

        select = ET.SubElement(root, "select", statement=_statement(state))
        if not feature_rows.empty:
            _attrs(ET.SubElement(select, "features"), feature_rows, "kc_")

        track = ET.SubElement(select, "track")
        for row in track_treatments.itertuples(index=False):
            treatment = ET.SubElement(
                track,
                "treatment",
                label=str(row.TREATMENT),
                minage=str(int(row.BEGIN)),
                maxage=str(int(row.END)),
            )
            target = start_by_track[int(row.NEWTRACK)]
            transition = ET.SubElement(treatment, "transition")
            for field in STATE_FIELDS:
                ET.SubElement(transition, "assign", field=field, value=f"'{target[field]}'")

    for track_id, state in start_by_track.items():
        rows = products.loc[products["TRACK"] == track_id]
        for treatment, group in rows.groupby("TREATMENT", sort=True):
            select = ET.SubElement(
                root,
                "select",
                statement=_statement(state, str(treatment)),
            )
            _attrs(ET.SubElement(select, "products"), group, "kc_")

    ET.indent(root, space="  ")
    return root, tracks, states


def main() -> None:
    """Write ForestModelXML, matrix-builder fragments and a manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h-dir", type=Path, required=True)
    parser.add_argument("--fragments", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    root, tracks, states = _build_recipe(args.h_dir)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    xml_path = args.out_dir / "forestmodel.xml"
    ET.ElementTree(root).write(xml_path, encoding="utf-8", xml_declaration=True)

    fragments = pd.read_csv(args.fragments)
    state_by_track = states.set_index("TRACK")
    missing = sorted(set(fragments["TRACK"]) - set(state_by_track.index))
    if missing:
        raise ValueError(f"fragments point at unknown tracks: {missing}")

    matrix_fragments = fragments.copy()
    matrix_fragments["FRAGMENT_ID"] = matrix_fragments["BLOCK"]
    matrix_fragments["AU"] = 1
    matrix_fragments["IFM"] = "managed"
    matrix_fragments["ORIGIN"] = "natural"
    matrix_fragments["RETENTION"] = 0.0
    matrix_fragments["TSA"] = "KC"
    for field in STATE_FIELDS:
        matrix_fragments[field] = matrix_fragments["TRACK"].map(state_by_track[field].to_dict())
    matrix_fragments = matrix_fragments[
        [
            "FRAGMENT_ID",
            "BLOCK",
            "AREA_HA",
            "F_AGE",
            "AU",
            "IFM",
            "ORIGIN",
            "RETENTION",
            "TSA",
            *STATE_FIELDS,
            "TRACK",
        ]
    ]
    matrix_fragments.to_csv(args.out_dir / "fragments.csv", index=False)

    manifest = {
        "recipe": "kc-ws4-forestmodelxml-v1",
        "source_matrix": str(args.h_dir),
        "tracks": len(tracks),
        "states": len(states),
        "fragments": len(matrix_fragments),
        "state_fields": list(STATE_FIELDS),
        "horizon_years": 100,
        "caveats": [
            "Generated from the KC H-matrix source tables, not from a fresh FVS-BC run.",
            "The recipe uses AU=1 as a constant compatibility field; the six KC "
            "state dimensions carry the tracks.",
            "F_AGE is VRI projected age, not a measured stand age.",
            "No clearcut treatment is present.",
            "The recipe is a structural ws4 input, not a calibrated or legal-compliance model.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
