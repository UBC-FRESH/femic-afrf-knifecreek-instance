#!/usr/bin/env python3
"""Compare simulated KC PSP transitions with observed canonical states."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from audit_psp_state_support import (
    BA_BINS,
    BA_LABELS,
    LT_BINS,
    LT_LABELS,
    QMD_BINS,
    QMD_LABELS,
    _bin,
)


def _state(frame: pd.DataFrame, prefix: str) -> pd.Series:
    ba = _bin(frame[f"{prefix}_ba_m2_ha"], BA_BINS, BA_LABELS)
    qmd = _bin(frame[f"{prefix}_qmd_cm"], QMD_BINS, QMD_LABELS)
    lt = _bin(frame[f"{prefix}_large_ba_m2_ha"], LT_BINS, LT_LABELS)
    return ba + "__" + qmd + "__" + lt


def main() -> None:
    """Write simulated-versus-observed state-match tables."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--simulation", type=Path, required=True)
    parser.add_argument("--transitions", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    sim = pd.read_csv(args.simulation)
    observed = pd.read_csv(args.transitions)
    frame = sim.merge(
        observed[
            [
                "plot",
                "interval_id",
                "ba_start_m2_ha",
                "qmd_start_cm",
                "large_ba_start_m2_ha",
                "ba_end_m2_ha",
                "qmd_end_cm",
                "large_ba_end_m2_ha",
            ]
        ],
        on=["plot", "interval_id"],
        how="inner",
    )
    frame = frame.rename(
        columns={
            "ba_start_m2_ha": "start_ba_m2_ha",
            "qmd_start_cm": "start_qmd_cm",
            "large_ba_start_m2_ha": "start_large_ba_m2_ha",
            "ba_end_m2_ha": "end_ba_m2_ha",
            "qmd_end_cm": "end_qmd_cm",
            "large_ba_end_m2_ha": "end_large_ba_m2_ha",
        }
    )
    frame["start_state"] = _state(frame, "start")
    frame["observed_end_state"] = _state(frame, "end")
    frame["cohort_end_state"] = _state(frame, "cohort")
    frame["conditional_end_state"] = _state(frame, "conditional")
    for mode in ("cohort", "conditional"):
        frame[f"{mode}_match"] = frame[f"{mode}_end_state"] == frame["observed_end_state"]
    frame.to_csv(args.out_dir / "state_match.csv", index=False)
    summary = (
        frame.groupby("heldout_block")
        .agg(
            n=("plot", "size"),
            cohort_matches=("cohort_match", "sum"),
            conditional_matches=("conditional_match", "sum"),
            observed_start_states=("start_state", "nunique"),
            observed_end_states=("observed_end_state", "nunique"),
            cohort_end_states=("cohort_end_state", "nunique"),
            conditional_end_states=("conditional_end_state", "nunique"),
        )
        .reset_index()
    )
    summary["cohort_match_rate"] = summary["cohort_matches"] / summary["n"]
    summary["conditional_match_rate"] = summary["conditional_matches"] / summary["n"]
    summary.to_csv(args.out_dir / "state_match_summary.csv", index=False)
    overall = {
        "n": len(frame),
        "cohort_matches": int(frame["cohort_match"].sum()),
        "conditional_matches": int(frame["conditional_match"].sum()),
        "cohort_match_rate": float(frame["cohort_match"].mean()),
        "conditional_match_rate": float(frame["conditional_match"].mean()),
    }
    manifest = {
        "comparison": "afrf-kc-psp-simulated-state-match-v1",
        "overall": overall,
        "bins": {
            "ba": BA_LABELS,
            "qmd": QMD_LABELS,
            "large_tree_ba": LT_LABELS,
        },
        "notes": [
            "States are BA/QMD/large-tree canonical bins; reserve is not observed.",
            "Conditional mode uses observed ingrowth; it is not an ingrowth forecast.",
            "A state match is exact equality of the three bins, not a distance.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(overall, indent=2))
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
