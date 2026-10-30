#!/usr/bin/env python3
"""Extract BA/QMD residual state nodes and edges from KC multi-entry FVS cases.

The source is the per-plot state/curve table produced by
``build_kc_au_multientry_200y.py``. States are BA/QMD bins; edges are the
majority next state for the same plot at the next entry.

Usage::

    python runbooks/build_kc_au_state_graph.py \
      --states data/psp/kc_au_200y/kc_au_multientry_moderate_plot_states.csv \
      --regime GWM_MODERATE \
      --out-dir data/kc_au_state_graph
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

BA_BINS = [0.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 1000.0]
QMD_BINS = [0.0, 20.0, 25.0, 30.0, 35.0, 40.0, 1000.0]


def _bin_label(value: float, bins: list[float], prefix: str) -> str:
    """Return a stable label for a numeric bin."""
    for lower, upper in zip(bins[:-1], bins[1:], strict=True):
        if lower <= value < upper:
            return f"{prefix}{int(lower)}_{int(upper) if upper < 1000 else 'PLUS'}"
    return f"{prefix}{int(bins[-2])}_PLUS"


def _state_id(row: pd.Series) -> str:
    """Return a BA/QMD state id for a residual row."""
    ba = _bin_label(float(row["ba_m2_ha"]), BA_BINS, "BA")
    qmd = _bin_label(float(row["qmd_cm"]), QMD_BINS, "QMD")
    return f"{ba}_{qmd}"


def main() -> None:
    """Write state nodes, curves and edges."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--states", type=Path, required=True)
    parser.add_argument("--regime", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    frame = pd.read_csv(args.states)
    frame = frame[frame["regime"] == args.regime].copy()
    frame["state_id"] = frame.apply(_state_id, axis=1)
    entry = frame[frame["year"] == 0].copy()
    entry["next_state"] = None
    for (au_id, plot), group in entry.groupby(["au_id", "CLSTR_ID"]):
        group = group.sort_values("stage")
        for index, row in group.iterrows():
            later = group[group["stage"] > row["stage"]]
            if not later.empty:
                entry.loc[index, "next_state"] = later.iloc[0]["state_id"]

    nodes = (
        entry.groupby(["au_id", "state_id"])
        .agg(
            stages=("stage", lambda values: ",".join(str(v) for v in sorted(set(values)))),
            plots=("CLSTR_ID", "nunique"),
            ba_mean=("ba_m2_ha", "mean"),
            qmd_mean=("qmd_cm", "mean"),
            tph_mean=("tph", "mean"),
            volume_mean=("volume_m3_ha", "mean"),
            canopy_mean=("canopy_ccf", "mean"),
            cut_mean=("cut_m3_ha", "mean"),
        )
        .reset_index()
    )
    curves = (
        frame.groupby(["au_id", "state_id", "year"], as_index=False)
        .agg(
            ba_m2_ha=("ba_m2_ha", "mean"),
            tph=("tph", "mean"),
            qmd_cm=("qmd_cm", "mean"),
            volume_m3_ha=("volume_m3_ha", "mean"),
            canopy_ccf=("canopy_ccf", "mean"),
            cut_m3_ha=("cut_m3_ha", "mean"),
        )
    )
    edge_counts = (
        entry.dropna(subset=["next_state"])
        .groupby(["au_id", "state_id", "next_state"])
        .size()
        .reset_index(name="count")
        .sort_values(["au_id", "state_id", "count"], ascending=[True, True, False])
    )
    edges = edge_counts.drop_duplicates(["au_id", "state_id"], keep="first")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    nodes.to_csv(args.out_dir / "state_nodes.csv", index=False)
    curves.to_csv(args.out_dir / "state_curves.csv", index=False)
    edges.to_csv(args.out_dir / "state_edges.csv", index=False)
    manifest = {
        "regime": args.regime,
        "states": int(nodes["state_id"].nunique()),
        "nodes": len(nodes),
        "edges": len(edges),
        "curve_rows": len(curves),
        "ba_bins": BA_BINS,
        "qmd_bins": QMD_BINS,
        "caveats": [
            "State ids are BA/QMD bins from residual FVS states.",
            "Edges use the majority next state for each source state.",
            "No calibration or legal-compliance claim.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
