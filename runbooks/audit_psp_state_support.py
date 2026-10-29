#!/usr/bin/env python3
"""Audit whether the observed PSP transitions support a state library.

The audit maps each transition to the existing ws4 BA/QMD/large-tree bins and
to a species-mix class. It reports support counts; it does not invent an
acceptance threshold or fill unsupported states.

Usage::

    python runbooks/audit_psp_state_support.py \
      --transitions data/psp/kc_afrf_psp_transitions.csv \
      --species data/psp/kc_afrf_psp_transitions_species.csv \
      --out-dir data/psp
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

BA_BINS = [-np.inf, 20, 25, 30, 35, 40, np.inf]
BA_LABELS = ["BA_LT20", "BA20_25", "BA25_30", "BA30_35", "BA35_40", "BA40_PLUS"]
QMD_BINS = [-np.inf, 20, 25, 30, 35, np.inf]
QMD_LABELS = ["QMD_LT20", "QMD20_25", "QMD25_30", "QMD30_35", "QMD35_PLUS"]
LT_BINS = [-np.inf, 6, 11, 16, np.inf]
LT_LABELS = ["LT_LT6", "LT6_11", "LT11_16", "LT16_PLUS"]


def _bin(series: pd.Series, bins: list[float], labels: list[str]) -> pd.Series:
    """Right-open categorical binning with explicit labels."""
    return pd.cut(series, bins=bins, labels=labels, right=False).astype(str)


def _state_frame(transitions: pd.DataFrame, species: pd.DataFrame) -> pd.DataFrame:
    """Annotate transitions with canonical and species-aware state IDs."""
    frame = transitions.copy()
    frame["ba_start_bin"] = _bin(frame["ba_start_m2_ha"], BA_BINS, BA_LABELS)
    frame["ba_end_bin"] = _bin(frame["ba_end_m2_ha"], BA_BINS, BA_LABELS)
    frame["qmd_start_bin"] = _bin(frame["qmd_start_cm"], QMD_BINS, QMD_LABELS)
    frame["qmd_end_bin"] = _bin(frame["qmd_end_cm"], QMD_BINS, QMD_LABELS)
    frame["lt_start_bin"] = _bin(frame["large_ba_start_m2_ha"], LT_BINS, LT_LABELS)
    frame["lt_end_bin"] = _bin(frame["large_ba_end_m2_ha"], LT_BINS, LT_LABELS)

    # Species mix from the start and end species-group BA.
    species_total = species.groupby(["plot", "interval_id"], as_index=False).agg(
        ba_start=("ba_start_m2_ha", "sum"), ba_end=("ba_end_m2_ha", "sum")
    )
    fd = species[species["species_group"] == "FD"][
        ["plot", "interval_id", "ba_start_m2_ha", "ba_end_m2_ha"]
    ].rename(columns={"ba_start_m2_ha": "fd_start", "ba_end_m2_ha": "fd_end"})
    mix = species_total.merge(fd, on=["plot", "interval_id"], how="left").fillna(0.0)
    mix["fd_start_share"] = np.where(mix["ba_start"] > 0, mix["fd_start"] / mix["ba_start"], 0.0)
    mix["fd_end_share"] = np.where(mix["ba_end"] > 0, mix["fd_end"] / mix["ba_end"], 0.0)

    def mix_class(share: float) -> str:
        if share >= 0.75:
            return "FD_DOM"
        if share >= 0.40:
            return "MIXED"
        return "OTHER"

    mix["start_mix"] = mix["fd_start_share"].map(mix_class)
    mix["end_mix"] = mix["fd_end_share"].map(mix_class)
    frame = frame.merge(
        mix[
            [
                "plot",
                "interval_id",
                "fd_start_share",
                "fd_end_share",
                "start_mix",
                "end_mix",
            ]
        ],
        on=["plot", "interval_id"],
        how="left",
    )
    frame["start_state_canonical"] = (
        frame["ba_start_bin"] + "__" + frame["qmd_start_bin"] + "__" + frame["lt_start_bin"]
    )
    frame["end_state_canonical"] = (
        frame["ba_end_bin"] + "__" + frame["qmd_end_bin"] + "__" + frame["lt_end_bin"]
    )
    frame["start_state_species"] = frame["start_state_canonical"] + "__" + frame["start_mix"]
    frame["end_state_species"] = frame["end_state_canonical"] + "__" + frame["end_mix"]
    return frame


def _summary(frame: pd.DataFrame, start_col: str, end_col: str, label: str) -> dict:
    """Support summary for one state definition."""
    grouped = (
        frame.groupby([start_col, end_col], as_index=False)
        .agg(
            n_transitions=("plot", "size"),
            n_plots=("plot", "nunique"),
            n_blocks=("block", "nunique"),
            n_subset_cd=("subset_cd", "sum"),
            intervals=("interval_id", lambda values: "|".join(sorted(set(values)))),
        )
        .sort_values(["n_transitions", "n_plots"], ascending=False)
    )
    grouped = grouped.rename(columns={start_col: "start_state", end_col: "end_state"})
    grouped["state_definition"] = label
    grouped["repeated"] = grouped["n_transitions"] > 1
    return {
        "definition": label,
        "n_transitions": len(frame),
        "n_start_states": frame[start_col].nunique(),
        "n_end_states": frame[end_col].nunique(),
        "n_pairs": len(grouped),
        "n_repeated_pairs": int(grouped["repeated"].sum()),
        "n_one_off_pairs": int((~grouped["repeated"]).sum()),
        "n_pairs_multi_plot": int((grouped["n_plots"] >= 2).sum()),
        "max_pair_support": int(grouped["n_transitions"].max()),
        "median_pair_support": float(grouped["n_transitions"].median()),
        "summary": grouped,
    }


def main() -> None:
    """Write the state-support tables and metadata."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transitions", type=Path, required=True)
    parser.add_argument("--species", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    transitions = pd.read_csv(args.transitions)
    species = pd.read_csv(args.species)
    frame = _state_frame(transitions, species)
    frame.to_csv(args.out_dir / "kc_afrf_psp_state_support.csv", index=False)

    canonical = _summary(frame, "start_state_canonical", "end_state_canonical", "canonical")
    with_species = _summary(frame, "start_state_species", "end_state_species", "species_mix")
    summaries = pd.concat(
        [canonical.pop("summary"), with_species.pop("summary")], ignore_index=True
    )
    summaries.to_csv(args.out_dir / "kc_afrf_psp_state_support_summary.csv", index=False)
    metadata = {
        "source": "observed KC PSP transitions, support audit",
        "n_transitions": len(frame),
        "definitions": {
            "ba_bins": BA_LABELS,
            "qmd_bins": QMD_LABELS,
            "large_tree_ba_bins": LT_LABELS,
            "species_mix": {
                "FD_DOM": "FD BA share >= 0.75",
                "MIXED": "FD BA share 0.40-0.75",
                "OTHER": "FD BA share < 0.40",
            },
        },
        "canonical": canonical,
        "species_mix": with_species,
        "notes": [
            "Support counts are descriptive; no acceptance threshold is applied.",
            "One-off pairs are retained, not deleted.",
            "The canonical bins follow the existing ws4 BA/QMD/large-tree classes.",
            "No age or site index is assigned.",
            "No reserve-above-D class is available: reserve is a treatment "
            "decision, not an observed PSP attribute.",
        ],
        "files": [
            "kc_afrf_psp_state_support.csv",
            "kc_afrf_psp_state_support_summary.csv",
        ],
    }
    (args.out_dir / "kc_afrf_psp_state_support_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )
    print(
        f"transitions={len(frame)} "
        f"canonical pairs={canonical['n_pairs']} "
        f"species pairs={with_species['n_pairs']}"
    )
    print("canonical", {k: canonical[k] for k in canonical if k != "summary"})
    print("species", {k: with_species[k] for k in with_species if k != "summary"})


if __name__ == "__main__":
    main()
