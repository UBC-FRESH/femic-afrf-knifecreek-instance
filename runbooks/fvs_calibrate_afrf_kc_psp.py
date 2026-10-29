#!/usr/bin/env python3
"""Calibrate FVS-BC to the AFRF Knife Creek PSP remeasurements.

This is a species-group fixed-point calibration, not a black-box fit. It
adjusts FVS ``BAIMULT`` and ``MORTMULT`` so that the 2013 species-group basal
area and trees/ha move toward the measured 2013 values, then re-runs the
24-plot backtest.

The iteration stops when the largest parameter change is below
``--parameter-tolerance`` and the objective change is below
``--loss-tolerance``, or at ``--max-iter``. A non-converged result is recorded
as such; it is not silently treated as calibrated. No stand age or site index
is assigned: uneven-aged plots have no single age, and FVS-BC ignores site
index.

Usage::

    python runbooks/fvs_calibrate_afrf_kc_psp.py \
      --trees data/private/afrf_kc_psp/trees_long.csv \
      --observed data/psp/kc_afrf_psp_plot_summary.csv \
      --out-dir ws4/kc_psp_calibration \
      --runtime-dir runtime/kc_psp_calibration
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

import fvs_validate_afrf_kc_psp as base
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case

YEARS = (1993, 1997, 2004, 2008, 2013)
AREA_HA = 0.05
TARGET_YEAR = 2013
GROUPS = {
    "FD": ("FD",),
    "SE": ("SE",),
    "PL": ("PL",),
    "HW": ("EP", "AT", "OH"),
}
SPECIES_GROUP = {
    "FD": "FD",
    "SE": "SE",
    "PL": "PL",
    "EP": "HW",
    "AT": "HW",
    "OH": "HW",
}
# No plot age is available; keep the FVS age fields at an explicit unknown.
TREE_AGE = 0.0
STAND_AGE = 0.0
SITE_INDEX = None
BA_BOUNDS = (0.25, 4.0)
MORT_BOUNDS = (0.25, 8.0)


def _expand(values: dict[str, float]) -> dict[str, float]:
    """Expand group values to the individual FVS species codes."""
    return {
        species: float(values[group])
        for group, species_plan in GROUPS.items()
        for species in species_plan
    }


def _observed_groups(trees: pd.DataFrame, year: int) -> pd.DataFrame:
    """Return observed species-group BA and TPH for one measurement."""
    live = trees[
        (trees["year"] == year) & (trees["position"] == "I") & trees["dbh_cm"].notna()
    ].copy()
    live["group"] = live["species"].map(SPECIES_GROUP).fillna("OTHER")
    live = live[live["group"] != "OTHER"]
    live["ba"] = 0.00007854 * live["dbh_cm"] ** 2 / AREA_HA
    return (
        live.groupby("group", as_index=False)
        .agg(ba_m2_ha=("ba", "sum"), tph=("tree", "size"))
        .assign(tph=lambda frame: frame["tph"] / AREA_HA)
        .set_index("group")
    )


def _predicted_groups(tree_list: pd.DataFrame) -> pd.DataFrame:
    """Aggregate a final FVS tree list to species-group BA and TPH."""
    frame = tree_list.copy()
    frame["group"] = frame["SpeciesFVS"].map(SPECIES_GROUP).fillna("OTHER")
    frame = frame[frame["group"] != "OTHER"]
    frame["ba"] = 0.00007854 * frame["DBH"] ** 2 * frame["TPH"]
    return (
        frame.groupby("group", as_index=False)
        .agg(ba_m2_ha=("ba", "sum"), tph=("TPH", "sum"))
        .set_index("group")
    )


def _run_iteration(
    initial: pd.DataFrame,
    *,
    ba_multipliers: dict[str, float],
    mort_multipliers: dict[str, float],
    runtime_dir: Path,
    iteration: int,
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, object]]]:
    """Run all plots with one parameter set and return summaries and groups."""
    summaries = []
    group_frames = []
    runs = []
    ba_map = _expand(ba_multipliers)
    mort_map = _expand(mort_multipliers)
    for plot, group in initial.groupby("plot"):
        case_dir = runtime_dir / f"iter_{iteration:02d}" / f"plot_{int(plot):02d}"
        if case_dir.exists():
            shutil.rmtree(case_dir)
        records = [
            base._record(
                row,
                plot_id=int(plot),
                tree_num=index + 1,
                tree_age=TREE_AGE,
            )
            for index, (_, row) in enumerate(group.iterrows())
        ]
        result = run_case(
            records,
            base._keywords(
                int(plot),
                site_index=SITE_INDEX,
                ba_multipliers=ba_map,
                mort_multipliers=mort_map,
                stand_age=STAND_AGE,
            ),
            directory=case_dir,
        )
        case_id = result.provenance.case_id
        summary = read_table(result.database, "FVS_Summary_Metric")
        summary = summary[summary["CaseID"] == case_id].sort_values("Year")
        for row in summary.itertuples(index=False):
            summaries.append(
                {
                    "plot": int(plot),
                    "year": int(row.Year),
                    "pred_ba_m2_ha": float(row.BA),
                    "pred_tph": float(row.Tph),
                    "pred_qmd_cm": float(row.QMD),
                    "pred_top_height_m": float(row.TopHt),
                    "pred_ccf": float(row.CCF),
                }
            )
        tree_list = read_table(result.database, "FVS_TreeList_Metric")
        tree_list = tree_list[(tree_list["CaseID"] == case_id) & (tree_list["Year"] == TARGET_YEAR)]
        groups = _predicted_groups(tree_list).reset_index()
        groups["plot"] = int(plot)
        group_frames.append(groups)
        runs.append(
            {
                "plot": int(plot),
                "case_id": case_id,
                "keyword_hash": result.provenance.keyword_set_hash,
                "treelist_hash": result.provenance.treelist_hash,
            }
        )
    return (
        pd.DataFrame(summaries),
        pd.concat(group_frames, ignore_index=True),
        runs,
    )


def _loss(
    observed_2013: pd.DataFrame,
    predicted_2013: pd.DataFrame,
) -> float:
    """Symmetric log-ratio loss across groups and the whole stand."""
    terms = []
    for group in GROUPS:
        obs = observed_2013.loc[group] if group in observed_2013.index else None
        pred = predicted_2013.loc[group] if group in predicted_2013.index else None
        if obs is None or pred is None:
            continue
        if obs["ba_m2_ha"] > 0.5:
            terms.append(np.log((pred["ba_m2_ha"] + 1.0) / (obs["ba_m2_ha"] + 1.0)) ** 2)
        if obs["tph"] > 20.0:
            terms.append(np.log((pred["tph"] + 10.0) / (obs["tph"] + 10.0)) ** 2)
    obs_total = observed_2013.sum()
    pred_total = predicted_2013.sum()
    terms.append(np.log((pred_total["ba_m2_ha"] + 1.0) / (obs_total["ba_m2_ha"] + 1.0)) ** 2)
    terms.append(np.log((pred_total["tph"] + 10.0) / (obs_total["tph"] + 10.0)) ** 2)
    return float(np.sqrt(np.mean(terms)))


def _next_parameters(
    *,
    observed_1993: pd.DataFrame,
    observed_2013: pd.DataFrame,
    predicted_2013: pd.DataFrame,
    ba: dict[str, float],
    mort: dict[str, float],
    damping: float,
) -> tuple[dict[str, float], dict[str, float]]:
    """One damped fixed-point update from measured to predicted groups."""
    next_ba = dict(ba)
    next_mort = dict(mort)
    for group in GROUPS:
        if group not in observed_2013.index or group not in observed_1993.index:
            continue
        obs = observed_2013.loc[group]
        pred = predicted_2013.loc[group] if group in predicted_2013.index else None
        if pred is None:
            continue
        if obs["tph"] >= 20.0:
            ratio = (pred["tph"] + 10.0) / (obs["tph"] + 10.0)
            next_mort[group] = float(np.clip(mort[group] * ratio**damping, *MORT_BOUNDS))
        obs_inc = obs["ba_m2_ha"] - observed_1993.loc[group, "ba_m2_ha"]
        pred_inc = pred["ba_m2_ha"] - observed_1993.loc[group, "ba_m2_ha"]
        # A group whose measured BA falls (notably lodgepole pine) is handled by
        # mortality; do not force a growth multiplier below the bound.
        if obs_inc > 2.0 and pred_inc > 2.0:
            ratio = (obs_inc + 1.0) / (pred_inc + 1.0)
            next_ba[group] = float(np.clip(ba[group] * ratio**damping, *BA_BOUNDS))
    return next_ba, next_mort


def main() -> None:
    """Run the fixed-point calibration and write all diagnostics."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--observed", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--max-iter", type=int, default=30)
    parser.add_argument("--damping", type=float, default=0.6)
    parser.add_argument("--parameter-tolerance", type=float, default=0.02)
    parser.add_argument("--loss-tolerance", type=float, default=1e-4)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.runtime_dir.mkdir(parents=True, exist_ok=True)
    trees = pd.read_csv(args.trees)
    initial = trees[
        (trees["year"] == 1993) & (trees["position"] == "I") & trees["dbh_cm"].notna()
    ].copy()
    observed = pd.read_csv(args.observed)
    observed_1993 = _observed_groups(trees, 1993)
    observed_2013 = _observed_groups(trees, TARGET_YEAR)
    ba = dict.fromkeys(GROUPS, 1.0)
    mort = dict.fromkeys(GROUPS, 1.0)
    history: list[dict[str, object]] = []
    previous_loss = np.inf
    converged = False
    final_runs: list[dict[str, object]] = []
    final_pred = pd.DataFrame()
    final_comparison = pd.DataFrame()
    for iteration in range(1, args.max_iter + 1):
        pred, group_frames, runs = _run_iteration(
            initial,
            ba_multipliers=ba,
            mort_multipliers=mort,
            runtime_dir=args.runtime_dir,
            iteration=iteration,
        )
        predicted_2013 = (
            group_frames.groupby("group")[["ba_m2_ha", "tph"]].sum()
            if not group_frames.empty
            else pd.DataFrame(columns=["ba_m2_ha", "tph"])
        )
        comparison = observed_2013.join(
            predicted_2013, lsuffix="_obs", rsuffix="_pred", how="outer"
        )
        loss = _loss(observed_2013, predicted_2013)
        next_ba, next_mort = _next_parameters(
            observed_1993=observed_1993,
            observed_2013=observed_2013,
            predicted_2013=predicted_2013,
            ba=ba,
            mort=mort,
            damping=args.damping,
        )
        changes = [abs(next_ba[group] - ba[group]) / max(ba[group], 1e-9) for group in GROUPS] + [
            abs(next_mort[group] - mort[group]) / max(mort[group], 1e-9) for group in GROUPS
        ]
        max_change = max(changes)
        row: dict[str, object] = {
            "iteration": iteration,
            "loss": loss,
            "max_parameter_change": max_change,
            "loss_change": abs(loss - previous_loss),
            **{f"bai_{group}": ba[group] for group in GROUPS},
            **{f"mort_{group}": mort[group] for group in GROUPS},
        }
        history.append(row)
        print(f"iter={iteration} loss={loss:.6f} max_change={max_change:.4f} bai={ba} mort={mort}")
        final_runs = runs
        final_pred = pred
        final_comparison = comparison
        if (
            max_change < args.parameter_tolerance
            and abs(loss - previous_loss) < args.loss_tolerance
        ):
            converged = True
            break
        previous_loss = loss
        ba, mort = next_ba, next_mort
    pd.DataFrame(history).to_csv(args.out_dir / "calibration_history.csv", index=False)
    final_comparison.reset_index().to_csv(args.out_dir / "group_comparison.csv", index=False)
    final_pred.to_csv(args.out_dir / "fvs_predictions.csv", index=False)
    joined = observed.merge(final_pred, on=["plot", "year"], how="inner")
    joined["ba_error"] = joined["pred_ba_m2_ha"] - joined["ba_m2_ha"]
    joined["qmd_error"] = joined["pred_qmd_cm"] - joined["qmd_cm"]
    joined["tph_error"] = joined["pred_tph"] - joined["tph"]
    joined.to_csv(args.out_dir / "validation.csv", index=False)
    summary = (
        joined.groupby("year")
        .agg(
            n=("plot", "size"),
            obs_ba=("ba_m2_ha", "mean"),
            pred_ba=("pred_ba_m2_ha", "mean"),
            ba_bias=("ba_error", "mean"),
            ba_mae=("ba_error", lambda values: float(np.abs(values).mean())),
            obs_qmd=("qmd_cm", "mean"),
            pred_qmd=("pred_qmd_cm", "mean"),
            qmd_bias=("qmd_error", "mean"),
            obs_tph=("tph", "mean"),
            pred_tph=("pred_tph", "mean"),
            tph_bias=("tph_error", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(args.out_dir / "validation_summary.csv", index=False)
    final_metrics = summary.loc[summary["year"] == TARGET_YEAR].iloc[0]
    diagnostics = {
        "year": TARGET_YEAR,
        "ba_bias": float(final_metrics["ba_bias"]),
        "qmd_bias": float(final_metrics["qmd_bias"]),
        "tph_bias": float(final_metrics["tph_bias"]),
        "note": (
            "Local diagnostics only. The earlier 1.0 m2/ha, 100 TPH and "
            "0.5 cm thresholds were ad hoc and are not used as a gate."
        ),
    }
    status = "converged-in-sample" if converged else "not-converged"
    parameters = {
        "groups": {group: list(species) for group, species in GROUPS.items()},
        "species_to_group": SPECIES_GROUP,
        "ba_multiplier": ba,
        "mortality_multiplier": mort,
    }
    (args.out_dir / "calibration_parameters.json").write_text(
        json.dumps(parameters, indent=2) + "\n"
    )
    manifest = {
        "calibration": "afrf-kc-psp-fvs-calibration-v1",
        "status": status,
        "target_year": TARGET_YEAR,
        "plots": int(initial["plot"].nunique()),
        "tree_age": TREE_AGE,
        "stand_age": STAND_AGE,
        "site_index": (None if SITE_INDEX is None else {"species": "FD", "value": SITE_INDEX}),
        "max_iter": args.max_iter,
        "damping": args.damping,
        "parameter_tolerance": args.parameter_tolerance,
        "loss_tolerance": args.loss_tolerance,
        "iterations": len(history),
        "final_loss": history[-1]["loss"],
        "diagnostics": diagnostics,
        "out_of_sample_validation": "ws4/kc_psp_cv",
        "parameters": parameters,
        "runs": final_runs,
        "caveats": [
            "The calibration target is 2013 species-group BA and TPH.",
            "No stand age or site index assigned; uneven-aged plots have no single age.",
            "The model is distance-independent and has no explicit MPB module.",
            "Parameters are bounded to avoid numerically unstable fits.",
            "Not a legal-compliance or whole-block inventory claim.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(summary.to_string(index=False))
    print(f"converged={converged} iterations={len(history)} loss={history[-1]['loss']:.6f}")


if __name__ == "__main__":
    main()
