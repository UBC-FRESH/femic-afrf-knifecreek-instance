#!/usr/bin/env python3
"""Leave-one-block-out cross-validation of the KC PSP FVS-BC calibration.

Each fold fits the species-group multipliers on two blocks and evaluates the
held-out block. The comparison is against the uncalibrated backtest in
``ws4/kc_psp_validation``. A calibration that only improves in-sample fit is
not useful; the held-out errors decide.

Usage::

    python runbooks/fvs_cross_validate_afrf_kc_psp.py \
      --trees data/private/afrf_kc_psp/trees_long.csv \
      --observed data/psp/kc_afrf_psp_plot_summary.csv \
      --baseline ws4/kc_psp_validation/validation.csv \
      --out-dir ws4/kc_psp_cv \
      --runtime-dir runtime/kc_psp_cv
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

import fvs_calibrate_afrf_kc_psp as cal

FOLDS = ("B", "C", "D")
TARGET_YEAR = 2013
TOLERANCE = 0.02
LOSS_TOLERANCE = 1e-4


def _fit(
    trees: pd.DataFrame,
    initial: pd.DataFrame,
    *,
    train_blocks: tuple[str, ...],
    runtime_dir: Path,
    max_iter: int,
) -> tuple[dict[str, float], dict[str, float], list[dict[str, object]], bool]:
    """Fit multipliers on the training blocks."""
    train_initial = initial[initial["block"].isin(train_blocks)].copy()
    train_trees = trees[trees["block"].isin(train_blocks)].copy()
    observed_1993 = cal._observed_groups(train_trees, 1993)
    observed_2013 = cal._observed_groups(train_trees, TARGET_YEAR)
    ba = dict.fromkeys(cal.GROUPS, 1.0)
    mort = dict.fromkeys(cal.GROUPS, 1.0)
    history: list[dict[str, object]] = []
    previous_loss = np.inf
    converged = False
    for iteration in range(1, max_iter + 1):
        _, group_frames, _ = cal._run_iteration(
            train_initial,
            ba_multipliers=ba,
            mort_multipliers=mort,
            runtime_dir=runtime_dir,
            iteration=iteration,
        )
        predicted = group_frames.groupby("group")[["ba_m2_ha", "tph"]].sum()
        loss = cal._loss(observed_2013, predicted)
        next_ba, next_mort = cal._next_parameters(
            observed_1993=observed_1993,
            observed_2013=observed_2013,
            predicted_2013=predicted,
            ba=ba,
            mort=mort,
            damping=0.6,
        )
        changes = [
            abs(next_ba[group] - ba[group]) / max(ba[group], 1e-9) for group in cal.GROUPS
        ] + [abs(next_mort[group] - mort[group]) / max(mort[group], 1e-9) for group in cal.GROUPS]
        max_change = max(changes)
        history.append(
            {
                "iteration": iteration,
                "loss": loss,
                "max_parameter_change": max_change,
                **{f"bai_{group}": ba[group] for group in cal.GROUPS},
                **{f"mort_{group}": mort[group] for group in cal.GROUPS},
            }
        )
        if max_change < TOLERANCE and abs(loss - previous_loss) < LOSS_TOLERANCE:
            converged = True
            break
        previous_loss = loss
        ba, mort = next_ba, next_mort
    return ba, mort, history, converged


def main() -> None:
    """Run three folds and write held-out comparison tables."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--observed", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--max-iter", type=int, default=20)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    trees = pd.read_csv(args.trees)
    initial = trees[
        (trees["year"] == 1993) & (trees["position"] == "I") & trees["dbh_cm"].notna()
    ].copy()
    observed = pd.read_csv(args.observed)
    baseline = pd.read_csv(args.baseline)
    fold_rows = []
    heldout_rows = []
    parameter_rows = []
    for heldout in FOLDS:
        train_blocks = tuple(block for block in FOLDS if block != heldout)
        print(f"fold heldout={heldout} train={train_blocks}", flush=True)
        ba, mort, history, converged = _fit(
            trees,
            initial,
            train_blocks=train_blocks,
            runtime_dir=args.runtime_dir / f"fold_{heldout}",
            max_iter=args.max_iter,
        )
        parameter_rows.append(
            {
                "heldout_block": heldout,
                "train_blocks": "+".join(train_blocks),
                "converged": converged,
                "iterations": len(history),
                "final_loss": history[-1]["loss"],
                **{f"bai_{group}": ba[group] for group in cal.GROUPS},
                **{f"mort_{group}": mort[group] for group in cal.GROUPS},
            }
        )
        final_pred, _, _ = cal._run_iteration(
            initial,
            ba_multipliers=ba,
            mort_multipliers=mort,
            runtime_dir=args.runtime_dir / f"fold_{heldout}" / "evaluate",
            iteration=99,
        )
        heldout_plots = observed.loc[observed["block"] == heldout, "plot"].unique()
        obs = observed[observed["plot"].isin(heldout_plots)].copy()
        pred = final_pred[final_pred["plot"].isin(heldout_plots)].copy()
        joined = obs.merge(pred, on=["plot", "year"], how="inner")
        joined["cal_ba_error"] = joined["pred_ba_m2_ha"] - joined["ba_m2_ha"]
        joined["cal_qmd_error"] = joined["pred_qmd_cm"] - joined["qmd_cm"]
        joined["cal_tph_error"] = joined["pred_tph"] - joined["tph"]
        base = baseline[baseline["plot"].isin(heldout_plots)].copy()
        joined = joined.merge(
            base[["plot", "year", "ba_error", "qmd_error", "tph_error"]],
            on=["plot", "year"],
            how="left",
            suffixes=("", "_base"),
        )
        joined["heldout_block"] = heldout
        heldout_rows.append(joined)
        target = joined[joined["year"] == TARGET_YEAR]
        fold_rows.append(
            {
                "heldout_block": heldout,
                "n_plots": int(target["plot"].nunique()),
                "converged": converged,
                "iterations": len(history),
                "baseline_ba_bias": float(target["ba_error"].mean()),
                "calibrated_ba_bias": float(target["cal_ba_error"].mean()),
                "baseline_qmd_bias": float(target["qmd_error"].mean()),
                "calibrated_qmd_bias": float(target["cal_qmd_error"].mean()),
                "baseline_tph_bias": float(target["tph_error"].mean()),
                "calibrated_tph_bias": float(target["cal_tph_error"].mean()),
                "baseline_ba_mae": float(target["ba_error"].abs().mean()),
                "calibrated_ba_mae": float(target["cal_ba_error"].abs().mean()),
            }
        )
    pd.DataFrame(parameter_rows).to_csv(args.out_dir / "fold_parameters.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(args.out_dir / "heldout_summary.csv", index=False)
    pd.concat(heldout_rows, ignore_index=True).to_csv(
        args.out_dir / "heldout_validation.csv", index=False
    )
    manifest = {
        "cross_validation": "afrf-kc-psp-fvs-cv-v1",
        "folds": list(FOLDS),
        "target_year": TARGET_YEAR,
        "max_iter": args.max_iter,
        "tolerance": TOLERANCE,
        "loss_tolerance": LOSS_TOLERANCE,
        "note": (
            "Each fold fits on two blocks and evaluates the third. "
            "No age or site index is assigned."
        ),
        "caveats": [
            "Only three blocks; each held-out estimate uses eight plots.",
            "The calibration target is species-group BA/TPH, not QMD.",
            "PL/MPB remains unmodelled in FVS-BC.",
            "The raw workbook is private; only derived tables are committed.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(pd.DataFrame(fold_rows).to_string(index=False))


if __name__ == "__main__":
    main()
