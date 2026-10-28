#!/usr/bin/env python3
"""Canonicalize the GWM 2007 state-transition library v1.

The v1 state IDs are per stand/regime/entry. This runbook maps them to shared
BA/QMD/large-tree/reserve classes, aggregates duplicate transitions and curves,
and identifies terminal states. It does not claim graph closure by cycles; a
terminal state is an explicit no-outgoing state.

Usage::

    python runbooks/canonicalize_state_library.py \
      --library ws4/state_library_v1 \
      --out-dir ws4/state_library_v1/canonical
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd


def _ba_class(value: float) -> str:
    if not np.isfinite(value):
        return "BA_NA"
    if value < 20:
        return "BA_LT20"
    if value < 25:
        return "BA20_25"
    if value < 30:
        return "BA25_30"
    if value < 35:
        return "BA30_35"
    if value < 40:
        return "BA35_40"
    return "BA40_PLUS"


def _qmd_class(value: float) -> str:
    if not np.isfinite(value):
        return "QMD_NA"
    if value < 20:
        return "QMD_LT20"
    if value < 25:
        return "QMD20_25"
    if value < 30:
        return "QMD25_30"
    if value < 35:
        return "QMD30_35"
    return "QMD35_PLUS"


def _large_class(value: float) -> str:
    if not np.isfinite(value):
        return "LT_NA"
    if value < 6:
        return "LT_LT6"
    if value < 11:
        return "LT6_11"
    if value < 16:
        return "LT11_16"
    return "LT16_PLUS"


def _reserve_class(value: float) -> str:
    if not np.isfinite(value):
        return "RES_NA"
    if value < 0.5:
        return "RES_LT0_5"
    if value < 2.0:
        return "RES0_5_2"
    return "RES2_PLUS"


def _state_key(row: pd.Series) -> str:
    return "__".join(
        (
            "GWM2007",
            _ba_class(row.get("ba_m2_ha", np.nan)),
            _qmd_class(row.get("qmd_cm", np.nan)),
            _large_class(row.get("large_ba_m2_ha", np.nan)),
            _reserve_class(row.get("reserve_above_d_m2_ha", np.nan)),
        )
    )


def _cycles(nodes: list[str], edges: list[tuple[str, str]]) -> list[list[str]]:
    """Return simple cycles found by DFS."""
    graph: dict[str, list[str]] = {node: [] for node in nodes}
    for source, target in edges:
        graph.setdefault(source, []).append(target)
    found: list[list[str]] = []
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def walk(node: str) -> None:
        if node in visiting:
            index = stack.index(node)
            found.append([*stack[index:], node])
            return
        if node in visited:
            return
        visiting.add(node)
        stack.append(node)
        for nxt in graph.get(node, []):
            walk(nxt)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in nodes:
        walk(node)
    return found


def main() -> None:
    """Write canonical states, transitions, curves and graph."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    states = pd.read_csv(args.library / "states.csv")
    transitions = pd.read_csv(args.library / "transitions.csv")
    curves = pd.read_csv(args.library / "curves.csv")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    states["canonical_state"] = states.apply(_state_key, axis=1)
    state_map = dict(zip(states["state_id"], states["canonical_state"], strict=True))
    transitions["from_canonical"] = transitions["from_state"].map(state_map)
    transitions["to_canonical"] = transitions["to_state"].map(state_map)
    if transitions[["from_canonical", "to_canonical"]].isna().any().any():
        raise ValueError("a transition state did not map to a canonical state")

    grouped_rows = []
    curve_rows = []
    for (from_state, regime), group in transitions.groupby(["from_canonical", "regime"], sort=True):
        target = Counter(group["to_canonical"]).most_common(1)[0][0]
        selected = group[group["to_canonical"] == target]
        source_ids = set(selected["transition_id"])
        numeric = selected.select_dtypes(include=[np.number]).mean()
        row = {
            "transition_id": f"CANON__{from_state}__{regime}",
            "from_state": from_state,
            "to_state": target,
            "regime": regime,
            "basis": "GWM_2007",
            "n_sources": len(selected),
            "stand_structure_pass_fraction": float(selected["stand_structure_pass"].mean()),
            "legal_compliance": False,
        }
        for name in (
            "post_ba_m2_ha",
            "post_large_ba_m2_ha",
            "post_reserve_above_d_m2_ha",
            "post_q_factor",
            "post_max_dbh_cm",
            "clump_removed_large_ba_m2_ha",
            "fvs_cut_m3_ha",
        ):
            row[name] = float(numeric[name])
        grouped_rows.append(row)
        subset = curves[curves["transition_id"].isin(source_ids)]
        if subset.empty:
            continue
        mean_curve = subset.groupby("year", as_index=False)[
            ["ba_m2_ha", "qmd_cm", "tph", "volume_m3_ha", "canopy_ccf"]
        ].mean()
        for attribute, column in (
            ("ba", "ba_m2_ha"),
            ("qmd", "qmd_cm"),
            ("tph", "tph"),
            ("volume", "volume_m3_ha"),
            ("canopy_ccf", "canopy_ccf"),
        ):
            curve_id = f"{row['transition_id']}__{attribute}"
            for point in mean_curve.itertuples(index=False):
                curve_rows.append(
                    {
                        "curve_id": curve_id,
                        "transition_id": row["transition_id"],
                        "attribute": attribute,
                        "x": int(point.year),
                        "y": float(getattr(point, column)),
                    }
                )

    canonical_transitions = pd.DataFrame(grouped_rows)
    canonical_curves = pd.DataFrame(curve_rows)
    outgoing = set(canonical_transitions["from_state"])
    nodes = sorted(
        set(canonical_transitions["from_state"]) | set(canonical_transitions["to_state"])
    )
    terminal = sorted(set(nodes) - outgoing)
    edges = list(
        zip(
            canonical_transitions["from_state"],
            canonical_transitions["to_state"],
            strict=True,
        )
    )
    cycles = _cycles(nodes, edges)
    canonical_states = pd.DataFrame(
        {
            "state_id": nodes,
            "terminal": [node in terminal for node in nodes],
            "n_incoming": [
                int((canonical_transitions["to_state"] == node).sum()) for node in nodes
            ],
            "n_outgoing": [
                int((canonical_transitions["from_state"] == node).sum()) for node in nodes
            ],
        }
    )
    canonical_states.to_csv(args.out_dir / "states.csv", index=False)
    canonical_transitions.to_csv(args.out_dir / "transitions.csv", index=False)
    canonical_curves.to_csv(args.out_dir / "curves.csv", index=False)
    graph = {
        "nodes": [
            {"state_id": row.state_id, "terminal": bool(row.terminal)}
            for row in canonical_states.itertuples(index=False)
        ],
        "edges": [
            {
                "from": row.from_state,
                "to": row.to_state,
                "regime": row.regime,
                "n_sources": int(row.n_sources),
            }
            for row in canonical_transitions.itertuples(index=False)
        ],
        "terminal_states": terminal,
        "cycles": cycles,
    }
    (args.out_dir / "graph.json").write_text(json.dumps(graph, indent=2) + "\n")
    manifest = {
        "library": "knife-creek-state-transition-v1-canonical",
        "basis": "GWM_2007",
        "status": "canonical-terminal-graph",
        "counts": {
            "states": len(canonical_states),
            "transitions": len(canonical_transitions),
            "curves": len(canonical_curves),
            "terminal_states": len(terminal),
            "cycles": len(cycles),
        },
        "classes": {
            "ba": ["BA_LT20", "BA20_25", "BA25_30", "BA30_35", "BA35_40", "BA40_PLUS"],
            "qmd": ["QMD_LT20", "QMD20_25", "QMD25_30", "QMD30_35", "QMD35_PLUS"],
            "large_ba": ["LT_NA", "LT_LT6", "LT6_11", "LT11_16", "LT16_PLUS"],
            "reserve": ["RES_NA", "RES_LT0_5", "RES0_5_2", "RES2_PLUS"],
        },
        "caveats": [
            "Canonical classes are structural bins, not calibrated states.",
            "Duplicate from-state/regime transitions use the modal target state.",
            "Terminal states are explicit no-outgoing states; cycles are not forced.",
            "The clump rule is still a DBH-ranked proxy, not spatial.",
            "No legal-compliance claim.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"states={len(canonical_states)} transitions={len(canonical_transitions)} "
        f"curves={len(canonical_curves)} terminal={len(terminal)} cycles={len(cycles)}"
    )


if __name__ == "__main__":
    main()
