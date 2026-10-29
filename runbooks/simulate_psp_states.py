#!/usr/bin/env python3
"""Simulate observed KC PSP transitions with the tree-level models.

This is a state-reconstruction test, not a forecast of ingrowth. It applies
leave-one-block-out growth and survival models to each observed transition.
Two outputs are compared:

- ``cohort``: start trees only, no ingrowth;
- ``conditional``: start trees plus the recruits actually observed in that
  interval.

The conditional result uses observed ingrowth; it is therefore a check of the
growth/survival engine, not a test of the ingrowth model.

Usage::

    python runbooks/simulate_psp_states.py \
      --trees data/private/afrf_kc_psp/trees_long.csv \
      --transitions data/psp/kc_afrf_psp_transitions.csv \
      --out-dir ws4/kc_psp_simulation
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

import fit_psp_tree_models as tm

BLOCKS = ("B", "C", "D")
AREA_HA = 0.05


def _recruits(trees: pd.DataFrame) -> pd.DataFrame:
    """First measured DBH for every tree, used only for conditional ingrowth."""
    alive = trees[
        (trees["position"] == "I")
        & trees["plot"].notna()
        & trees["tree"].notna()
        & trees["dbh_cm"].notna()
    ].copy()
    return (
        alive.sort_values("year")
        .drop_duplicates(["plot", "tree"])[["plot", "tree", "year", "dbh_cm", "species"]]
        .rename(columns={"year": "first_year", "dbh_cm": "first_dbh_cm"})
    )


def _simulate_fold(
    trees: pd.DataFrame,
    transitions: pd.DataFrame,
    pairs: pd.DataFrame,
    heldout: str,
) -> pd.DataFrame:
    """Fit on the other blocks and simulate the held-out transitions."""
    train = pairs[pairs["block"] != heldout].copy()
    dg_model = tm._fit_dg(train)
    survival_model = tm._fit_survival(train)
    recruits = _recruits(trees)
    rows = []
    held = transitions[transitions["block"] == heldout].copy()
    for transition in held.itertuples(index=False):
        group = pairs[
            (pairs["plot"] == transition.plot) & (pairs["year"] == transition.start_year)
        ].copy()
        if group.empty:
            continue
        pred_dg = tm._predict_dg(dg_model, group)
        pred_surv = tm._predict_survival(survival_model, group)
        dbh_end = group["dbh_cm"].to_numpy() + pred_dg * transition.years
        pred_surv = np.clip(pred_surv, 0, 1)
        cohort_tph = float(pred_surv.sum() * 20.0)
        cohort_ba = float(np.sum(pred_surv * 0.00007854 * dbh_end**2 * 20.0))
        rec = recruits[
            (recruits["plot"] == transition.plot)
            & (recruits["first_year"] > transition.start_year)
            & (recruits["first_year"] <= transition.end_year)
        ]
        rec_tph = float(len(rec) * 20.0)
        rec_ba = float((0.00007854 * rec["first_dbh_cm"] ** 2 * 20.0).sum())
        full_tph = cohort_tph + rec_tph
        full_ba = cohort_ba + rec_ba
        rows.append(
            {
                "heldout_block": heldout,
                "interval_id": transition.interval_id,
                "plot": int(transition.plot),
                "block": heldout,
                "treatment": transition.treatment,
                "start_year": int(transition.start_year),
                "end_year": int(transition.end_year),
                "obs_tph": float(transition.tph_end),
                "obs_ba_m2_ha": float(transition.ba_end_m2_ha),
                "obs_qmd_cm": float(transition.qmd_end_cm),
                "cohort_tph": cohort_tph,
                "cohort_ba_m2_ha": cohort_ba,
                "cohort_qmd_cm": (
                    np.sqrt(cohort_ba / (cohort_tph * 0.00007854)) if cohort_tph > 0 else np.nan
                ),
                "conditional_tph": full_tph,
                "conditional_ba_m2_ha": full_ba,
                "conditional_qmd_cm": (
                    np.sqrt(full_ba / (full_tph * 0.00007854)) if full_tph > 0 else np.nan
                ),
                "observed_ingrowth_n": int(transition.ingrowth_n),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    """Run the reconstruction and write summary tables."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--transitions", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    trees = pd.read_csv(args.trees)
    transitions = pd.read_csv(args.transitions)
    pairs = tm._pairs(trees)
    frames = [_simulate_fold(trees, transitions, pairs, block) for block in BLOCKS]
    frame = pd.concat(frames, ignore_index=True)
    frame.to_csv(args.out_dir / "simulation_validation.csv", index=False)
    for mode in ("cohort", "conditional"):
        frame[f"{mode}_ba_bias"] = frame[f"{mode}_ba_m2_ha"] - frame["obs_ba_m2_ha"]
        frame[f"{mode}_tph_bias"] = frame[f"{mode}_tph"] - frame["obs_tph"]
        frame[f"{mode}_qmd_bias"] = frame[f"{mode}_qmd_cm"] - frame["obs_qmd_cm"]
    summary = (
        frame.groupby(["heldout_block", "interval_id"])
        .agg(
            n=("plot", "size"),
            obs_ba=("obs_ba_m2_ha", "mean"),
            cohort_ba=("cohort_ba_m2_ha", "mean"),
            conditional_ba=("conditional_ba_m2_ha", "mean"),
            cohort_ba_bias=("cohort_ba_bias", "mean"),
            conditional_ba_bias=("conditional_ba_bias", "mean"),
            cohort_ba_mae=("cohort_ba_bias", lambda x: float(np.abs(x).mean())),
            conditional_ba_mae=("conditional_ba_bias", lambda x: float(np.abs(x).mean())),
            obs_tph=("obs_tph", "mean"),
            cohort_tph=("cohort_tph", "mean"),
            conditional_tph=("conditional_tph", "mean"),
            cohort_tph_bias=("cohort_tph_bias", "mean"),
            conditional_tph_bias=("conditional_tph_bias", "mean"),
            obs_qmd=("obs_qmd_cm", "mean"),
            cohort_qmd=("cohort_qmd_cm", "mean"),
            conditional_qmd=("conditional_qmd_cm", "mean"),
            cohort_qmd_bias=("cohort_qmd_bias", "mean"),
            conditional_qmd_bias=("conditional_qmd_bias", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(args.out_dir / "simulation_summary.csv", index=False)
    overall = {}
    for mode in ("cohort", "conditional"):
        overall[mode] = {
            "ba_bias": float(frame[f"{mode}_ba_bias"].mean()),
            "ba_mae": float(frame[f"{mode}_ba_bias"].abs().mean()),
            "tph_bias": float(frame[f"{mode}_tph_bias"].mean()),
            "tph_mae": float(frame[f"{mode}_tph_bias"].abs().mean()),
            "qmd_bias": float(frame[f"{mode}_qmd_bias"].mean()),
            "qmd_mae": float(frame[f"{mode}_qmd_bias"].abs().mean()),
        }
    manifest = {
        "simulation": "afrf-kc-psp-state-reconstruction-v1",
        "transitions": len(frame),
        "folds": list(BLOCKS),
        "overall": overall,
        "caveats": [
            "Conditional mode uses observed ingrowth counts and recruit DBH; it is not a forecast.",
            "Cohort mode excludes ingrowth and tests growth/survival only.",
            "Models are fit leave-one-block-out.",
            "No age or site index is assigned.",
            "DBH presence is the working live-tree indicator.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(overall, indent=2))
    columns = [
        "cohort_ba_bias",
        "cohort_ba_mae",
        "conditional_ba_bias",
        "conditional_ba_mae",
        "cohort_tph_bias",
        "conditional_tph_bias",
        "cohort_qmd_bias",
        "conditional_qmd_bias",
    ]
    print(summary.groupby("heldout_block")[columns].mean().to_string())


if __name__ == "__main__":
    main()
