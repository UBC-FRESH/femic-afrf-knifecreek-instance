#!/usr/bin/env python3
"""Compile the KC BA/QMD residual state graph into a ws4 recipe.

Usage::

    python runbooks/build_kc_au_graph_recipe.py \
      --au-table data/kc_au/kc_au_table.csv \
      --assignment data/kc_au/kc_au_assignment.csv \
      --fragments data/patchworks_knifecreek/fragments.csv \
      --no-cut data/psp/kc_au_200y/kc_au_yield_200y.csv \
      --graph-low data/kc_au_state_graph/low \
      --graph-moderate data/kc_au_state_graph/moderate \
      --out-dir data/kc_ws4_recipe_au_graph
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
ENTRY_YEAR = 30


def _add_curve(root: ET.Element, curve_id: str, points: list[tuple[int, float]]) -> None:
    """Append a curve."""
    element = ET.SubElement(root, "curve", id=curve_id)
    for x, y in sorted(points):
        ET.SubElement(element, "point", x=str(int(x)), y=f"{float(y):.6f}")


def _attribute(parent: ET.Element, label: str, curve_id: str) -> None:
    """Append an attribute."""
    attribute = ET.SubElement(parent, "attribute", label=label)
    ET.SubElement(attribute, "curve", idref=curve_id)


def _state_name(regime: str, state_id: str) -> str:
    """Return a recipe state name."""
    prefix = "LOW" if regime == "GWM_LOW" else "MOD"
    return f"{prefix}_{state_id}"


def main() -> None:
    """Write the graph recipe and fragments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--au-table", type=Path, required=True)
    parser.add_argument("--assignment", type=Path, required=True)
    parser.add_argument("--fragments", type=Path, required=True)
    parser.add_argument("--no-cut", type=Path, required=True)
    parser.add_argument("--graph-low", type=Path, required=True)
    parser.add_argument("--graph-moderate", type=Path, required=True)
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
    graphs = {
        "GWM_LOW": (
            pd.read_csv(args.graph_low / "state_nodes.csv"),
            pd.read_csv(args.graph_low / "state_curves.csv"),
            pd.read_csv(args.graph_low / "state_edges.csv"),
        ),
        "GWM_MODERATE": (
            pd.read_csv(args.graph_moderate / "state_nodes.csv"),
            pd.read_csv(args.graph_moderate / "state_curves.csv"),
            pd.read_csv(args.graph_moderate / "state_edges.csv"),
        ),
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
        natural_features = {}
        for label, column in FEATURE_COLUMNS.items():
            curve_id = next_id("natural")
            _add_curve(root, curve_id, list(zip(natural["year"], natural[column], strict=True)))
            natural_features[label] = curve_id

        state_features: dict[str, dict[str, str]] = {}
        state_products: dict[str, str] = {}
        state_edges_by_regime: dict[str, dict[str, str]] = {}
        first_target: dict[str, str] = {}
        for regime, (nodes, curves, edges) in graphs.items():
            nodes = nodes[nodes["au_id"] == au_id]
            if nodes.empty:
                raise ValueError(f"missing {regime} graph nodes for {au_id}")
            curves = curves[curves["au_id"] == au_id]
            edges = edges[edges["au_id"] == au_id]
            for node in nodes.itertuples(index=False):
                state = _state_name(regime, str(node.state_id))
                points = curves[curves["state_id"] == node.state_id].sort_values("year")
                state_features[state] = {}
                for label, column in FEATURE_COLUMNS.items():
                    curve_id = next_id(state.lower())
                    _add_curve(
                        root,
                        curve_id,
                        list(zip(points["year"], points[column], strict=True)),
                    )
                    state_features[state][label] = curve_id
                cut_curve = next_id(f"cut_{state.lower()}")
                _add_curve(root, cut_curve, [(0, float(node.cut_mean))])
                state_products[state] = cut_curve
            state_edges_by_regime[regime] = {
                _state_name(regime, str(row.state_id)): _state_name(regime, str(row.next_state))
                for row in edges.itertuples(index=False)
            }
            stage_one = nodes[nodes["stages"].astype(str).str.split(",").apply(lambda v: "1" in v)]
            if stage_one.empty:
                stage_one = nodes
            pick = stage_one.sort_values("plots", ascending=False).iloc[0]
            first_target[regime] = _state_name(regime, str(pick.state_id))

        for hmz in hmz_values:
            allowed = ALLOWED_BY_HMZ.get(hmz, ())
            natural_select = ET.SubElement(
                root,
                "select",
                statement=f"AU eq '{au_id}' and HMZ eq '{hmz}' and SILV eq 'natural'",
            )
            features = ET.SubElement(natural_select, "features")
            for label in FEATURE_COLUMNS:
                _attribute(features, label, natural_features[label])
            _attribute(features, "feature.area.managed.total", "kc_area")
            track = ET.SubElement(natural_select, "track")
            for regime in allowed:
                target = first_target[regime]
                treatment = ET.SubElement(
                    track, "treatment", label=regime, minage=str(ENTRY_YEAR), maxage="200"
                )
                transition = ET.SubElement(treatment, "transition")
                ET.SubElement(transition, "assign", field="SILV", value=f"'{target}'")
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
                    state_products[target],
                )
            for regime in allowed:
                for state in state_features:
                    if not state.startswith("LOW_" if regime == "GWM_LOW" else "MOD_"):
                        continue
                    managed_select = ET.SubElement(
                        root,
                        "select",
                        statement=f"AU eq '{au_id}' and HMZ eq '{hmz}' and SILV eq '{state}'",
                    )
                    managed_features = ET.SubElement(managed_select, "features")
                    for label in FEATURE_COLUMNS:
                        _attribute(managed_features, label, state_features[state][label])
                    _attribute(managed_features, "feature.area.managed.total", "kc_area")
                    target = state_edges_by_regime[regime].get(state)
                    if target is None:
                        continue
                    managed_track = ET.SubElement(managed_select, "track")
                    treatment = ET.SubElement(
                        managed_track,
                        "treatment",
                        label=regime,
                        minage=str(ENTRY_YEAR),
                        maxage="200",
                    )
                    transition = ET.SubElement(treatment, "transition")
                    ET.SubElement(transition, "assign", field="SILV", value=f"'{target}'")
                    product = ET.SubElement(
                        root,
                        "select",
                        statement=(
                            f"AU eq '{au_id}' and HMZ eq '{hmz}' and "
                            f"SILV eq '{state}' and treatment eq '{regime}'"
                        ),
                    )
                    _attribute(
                        ET.SubElement(product, "products"),
                        "product.yield.managed.total",
                        state_products[target],
                    )

    ET.indent(root, space="  ")
    ET.ElementTree(root).write(
        args.out_dir / "forestmodel.xml", encoding="utf-8", xml_declaration=True
    )
    manifest = {
        "recipe": "kc-au-ba-qmd-graph-v1",
        "aus": len(au),
        "hmz_values": hmz_values,
        "treatments": list(REGIMES),
        "caveats": [
            "States are BA/QMD bins from FVS residual states.",
            "Transitions use the majority next state per source state.",
            "No calibration or legal-compliance claim.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
