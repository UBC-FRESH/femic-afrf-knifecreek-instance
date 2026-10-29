#!/usr/bin/env python3
"""Generate partial no-cut ws4 curves from the KC PSP tree models.

The generator is deliberately partial: it produces BA, TPH, QMD and large-tree
BA curves. It does not invent volume, canopy cover or treatment response.

Ingrowth is an explicit block/treatment scenario, kept separate from the
growth/survival models. The scenario uses observed PSP ingrowth rates and
recruit diameters, so it is a reconstruction input, not a transferable forecast.

Usage::

    python runbooks/generate_psp_transitions.py \
      --trees data/private/afrf_kc_psp/trees_long.csv \
      --transitions data/psp/kc_afrf_psp_transitions.csv \
      --models ws4/kc_psp_tree_models/tree_models.json \
      --out-dir ws4/kc_psp_generator
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
from audit_psp_state_support import (
    BA_BINS,
    BA_LABELS,
    LT_BINS,
    LT_LABELS,
    QMD_BINS,
    QMD_LABELS,
    _bin,
)

STEP_YEARS = 5
HORIZON = 30
AREA_HA = 0.05
GROUPS = ("FD", "SE", "PL", "HW")


def _scenario(trees: pd.DataFrame, transitions: pd.DataFrame) -> dict:
    """Build block/treatment ingrowth counts and recruit-size summaries."""
    alive = trees[
        (trees["position"] == "I")
        & trees["plot"].notna()
        & trees["tree"].notna()
        & trees["dbh_cm"].notna()
    ].copy()
    first = (
        alive.sort_values("year")
        .drop_duplicates(["plot", "tree"])[["plot", "tree", "year", "dbh_cm"]]
        .rename(columns={"year": "first_year", "dbh_cm": "first_dbh_cm"})
    )
    recruit = first.merge(
        transitions[["plot", "block", "treatment"]].drop_duplicates(),
        on="plot",
        how="left",
    )
    recruit = recruit[recruit["first_year"] > 1993]
    by_treatment = {}
    for (block, treatment), group in transitions.groupby(["block", "treatment"]):
        rec = recruit[(recruit["block"] == block) & (recruit["treatment"] == treatment)]
        years = group["years"].sum()
        count_per_year = group["ingrowth_n"].sum() / years if years else 0.0
        by_treatment[f"{block}|{treatment}"] = {
            "count_per_5yr": float(count_per_year * STEP_YEARS),
            "recruit_mean_dbh_cm": float(rec["first_dbh_cm"].mean()) if len(rec) else 0.0,
            "recruit_rms_dbh_cm": (
                float(np.sqrt(np.mean(rec["first_dbh_cm"] ** 2))) if len(rec) else 0.0
            ),
            "n_recruits": len(rec),
            "source": "observed PSP block/treatment",
        }
    global_rec = recruit["first_dbh_cm"]
    fallback = {
        "count_per_5yr": 0.0,
        "recruit_mean_dbh_cm": float(global_rec.mean()) if len(global_rec) else 0.0,
        "recruit_rms_dbh_cm": (float(np.sqrt(np.mean(global_rec**2))) if len(global_rec) else 0.0),
        "n_recruits": len(global_rec),
        "source": "pooled PSP recruits",
    }
    return {"by_block_treatment": by_treatment, "fallback": fallback}


def _design(dbh: np.ndarray, groups: np.ndarray, weights: np.ndarray, years: int) -> pd.DataFrame:
    """Build the predictor frame for the tree models."""
    ba = weights * 0.00007854 * dbh**2
    plot_ba = float(ba.sum())
    bal = np.zeros(len(dbh))
    order = np.argsort(dbh)[::-1]
    cumulative = np.cumsum(ba[order]) - ba[order]
    bal[order] = cumulative
    frame = pd.DataFrame(
        {
            "intercept": 1.0,
            "log_dbh": np.log(np.clip(dbh, 1.0, None)),
            "dbh": dbh,
            "bal": bal,
            "plot_ba": plot_ba,
            "crown_ratio": 0.5,
            "log_years": np.log(years),
            "species_SE": (groups == "SE").astype(float),
            "species_PL": (groups == "PL").astype(float),
            "species_HW": (groups == "HW").astype(float),
        }
    )
    return frame


def _predict_survival(model: dict, frame: pd.DataFrame) -> np.ndarray:
    means = pd.Series(model["means"])
    scales = pd.Series(model["scales"])
    z = ((frame[model["columns"]] - means) / scales).to_numpy() @ np.asarray(model["coefficients"])
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def _predict_dg(model: dict, frame: pd.DataFrame) -> np.ndarray:
    return frame[model["columns"]].to_numpy() @ np.asarray(model["coefficients"])


def _state(ba: float, qmd: float, large_ba: float) -> str:
    ba_bin = _bin(pd.Series([ba]), BA_BINS, BA_LABELS).iloc[0]
    qmd_bin = _bin(pd.Series([qmd]), QMD_BINS, QMD_LABELS).iloc[0]
    lt_bin = _bin(pd.Series([large_ba]), LT_BINS, LT_LABELS).iloc[0]
    return f"{ba_bin}__{qmd_bin}__{lt_bin}"


def _simulate(
    start: pd.DataFrame,
    *,
    scenario: dict,
    models: dict,
) -> tuple[list[dict], str]:
    """Simulate one plot for 30 years in five-year steps."""
    dbh = start["dbh_cm"].to_numpy(dtype=float)
    groups = start["species"].map(tm.SPECIES_GROUP).fillna("FD").to_numpy()
    weights = np.full(len(dbh), 20.0)
    curve = []

    def record(year: int) -> None:
        ba = float(np.sum(weights * 0.00007854 * dbh**2))
        tph = float(weights.sum())
        qmd = float(np.sqrt(ba / (tph * 0.00007854))) if tph > 0 else np.nan
        large = float(np.sum(weights[dbh >= 37.5] * 0.00007854 * dbh[dbh >= 37.5] ** 2))
        curve.append(
            {
                "year": year,
                "ba_m2_ha": ba,
                "tph": tph,
                "qmd_cm": qmd,
                "large_ba_m2_ha": large,
            }
        )

    record(0)
    for year in range(STEP_YEARS, HORIZON + 1, STEP_YEARS):
        frame = _design(dbh, groups, weights, STEP_YEARS)
        survival = _predict_survival(models["survival"], frame)
        dg = _predict_dg(models["diameter_increment"], frame)
        weights = weights * np.clip(survival, 0, 1)
        dbh = dbh + dg * STEP_YEARS
        count = scenario["count_per_5yr"]
        if count > 0 and scenario["recruit_rms_dbh_cm"] > 0:
            # One expected recruit entry; rms diameter preserves BA contribution.
            dbh = np.append(dbh, scenario["recruit_rms_dbh_cm"])
            groups = np.append(groups, "FD")
            weights = np.append(weights, count * 20.0)
        record(year)
    ba = float(np.sum(weights * 0.00007854 * dbh**2))
    tph = float(weights.sum())
    qmd = float(np.sqrt(ba / (tph * 0.00007854))) if tph > 0 else np.nan
    large = float(np.sum(weights[dbh >= 37.5] * 0.00007854 * dbh[dbh >= 37.5] ** 2))
    return curve, _state(ba, qmd, large)


def main() -> None:
    """Write partial generated transition curves and scenario metadata."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--transitions", type=Path, required=True)
    parser.add_argument("--models", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    trees = pd.read_csv(args.trees)
    transitions = pd.read_csv(args.transitions)
    models = json.loads(args.models.read_text())
    scen = _scenario(trees, transitions)
    starts = trees[
        (trees["year"] == 1993) & (trees["position"] == "I") & trees["dbh_cm"].notna()
    ].copy()
    curve_rows = []
    transition_rows = []
    for plot, group in starts.groupby("plot"):
        block = str(group["block"].iloc[0])
        treatment = str(group["treatment"].iloc[0])
        scenario = scen["by_block_treatment"].get(f"{block}|{treatment}", scen["fallback"])
        curve, end_state = _simulate(group, scenario=scenario, models=models)
        transition_id = f"KCPSP{int(plot):02d}_1993"
        start_ba = float((0.00007854 * group["dbh_cm"] ** 2 / AREA_HA).sum())
        start_qmd = float(np.sqrt((group["dbh_cm"] ** 2).sum() / len(group)))
        start_large = float(
            (0.00007854 * group.loc[group["dbh_cm"] >= 37.5, "dbh_cm"] ** 2 / AREA_HA).sum()
        )
        start_state = _state(start_ba, start_qmd, start_large)
        transition_rows.append(
            {
                "transition_id": transition_id,
                "plot": int(plot),
                "block": block,
                "treatment": treatment,
                "start_year": 1993,
                "horizon_years": HORIZON,
                "start_state": start_state,
                "end_state_30": end_state,
                "ingrowth_scenario": f"{block}|{treatment}",
                "ingrowth_count_per_5yr": scenario["count_per_5yr"],
            }
        )
        for point in curve:
            curve_rows.append({"transition_id": transition_id, **point})
    pd.DataFrame(transition_rows).to_csv(args.out_dir / "transitions.csv", index=False)
    pd.DataFrame(curve_rows).to_csv(args.out_dir / "curves.csv", index=False)
    (args.out_dir / "ingrowth_scenarios.json").write_text(json.dumps(scen, indent=2) + "\n")
    manifest = {
        "generator": "kc-psp-partial-ws4-v1",
        "starts": 24,
        "horizon_years": HORIZON,
        "step_years": STEP_YEARS,
        "curves": ["ba_m2_ha", "tph", "qmd_cm", "large_ba_m2_ha"],
        "not_generated": ["volume", "canopy cover", "treatment response", "products"],
        "ingrowth": "block/treatment empirical scenario; not a transferable forecast",
        "models": str(args.models),
        "caveats": [
            "Partial curve library, not a compiled ws4 dataset.",
            "Ingrowth is an observed block/treatment scenario.",
            "No age or site index is assigned.",
            "No treatment response is generated.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"transitions={len(transition_rows)} curves={len(curve_rows)}")


if __name__ == "__main__":
    main()
