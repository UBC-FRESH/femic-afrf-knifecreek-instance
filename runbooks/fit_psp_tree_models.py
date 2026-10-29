#!/usr/bin/env python3
"""Fit tree-level growth, survival and ingrowth models to the KC PSP data.

This is the empirical alternative to forcing a sparse plot-level state matrix.
The models use interval-start tree and stand attributes; validation is
leave-one-block-out. No age or site index is assigned.

Usage::

    python runbooks/fit_psp_tree_models.py \
      --trees data/private/afrf_kc_psp/trees_long.csv \
      --transitions data/psp/kc_afrf_psp_transitions.csv \
      --out-dir ws4/kc_psp_tree_models
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

YEARS = (1993, 1997, 2004, 2008, 2013)
AREA_HA = 0.05
SPECIES_GROUP = {
    "FD": "FD",
    "SE": "SE",
    "PL": "PL",
    "EP": "HW",
    "AT": "HW",
    "OH": "HW",
}
BLOCKS = ("B", "C", "D")
EPS = 1e-9


def _pairs(trees: pd.DataFrame) -> pd.DataFrame:
    """Build start/end tree observations for each remeasurement interval."""
    trees = trees[
        (trees["position"] == "I")
        & trees["plot"].notna()
        & trees["tree"].notna()
        & trees["year"].isin(YEARS)
    ].copy()
    trees = trees[trees["species"].isin(SPECIES_GROUP) & (trees["species"] != "OH")]
    rows = []
    for start, end in itertools.pairwise(YEARS):
        begin = trees[(trees["year"] == start) & trees["dbh_cm"].notna()].copy()
        finish = trees[trees["year"] == end][["plot", "tree", "dbh_cm", "height_m"]].rename(
            columns={"dbh_cm": "dbh_end", "height_m": "height_end"}
        )
        frame = begin.merge(finish, on=["plot", "tree"], how="left")
        frame["years"] = end - start
        frame["survived"] = frame["dbh_end"].notna().astype(int)
        frame["dg_cm_year"] = np.where(
            frame["survived"] == 1,
            (frame["dbh_end"] - frame["dbh_cm"]) / frame["years"],
            np.nan,
        )
        rows.append(frame)
    pairs = pd.concat(rows, ignore_index=True)
    pairs["species_group"] = pairs["species"].map(SPECIES_GROUP)
    pairs["ba_tree"] = 0.00007854 * pairs["dbh_cm"] ** 2 / AREA_HA
    pairs["plot_ba"] = pairs.groupby(["plot", "year"])["ba_tree"].transform("sum")
    pairs["plot_tph"] = pairs.groupby(["plot", "year"])["tree"].transform("size") / AREA_HA
    bal = []
    for _, group in pairs.groupby(["plot", "year"]):
        ordered = group.sort_values("dbh_cm", ascending=False)
        cumulative = ordered["ba_tree"].cumsum() - ordered["ba_tree"]
        bal.append(pd.Series(cumulative.to_numpy(), index=ordered.index))
    pairs["bal"] = pd.concat(bal).sort_index()
    pairs["crown_ratio"] = pairs["crown_ratio"].fillna(
        pairs.groupby("species_group")["crown_ratio"].transform("median")
    )
    pairs["crown_ratio"] = pairs["crown_ratio"].fillna(0.5).clip(0.05, 0.95)
    pairs["log_dbh"] = np.log(pairs["dbh_cm"].clip(lower=1.0))
    pairs["log_plot_ba"] = np.log(pairs["plot_ba"].clip(lower=0.1))
    pairs["log_plot_tph"] = np.log(pairs["plot_tph"].clip(lower=1.0))
    pairs["log_years"] = np.log(pairs["years"])
    return pairs


def _design(pairs: pd.DataFrame, *, survival: bool = False) -> pd.DataFrame:
    """Build the common design matrix for tree models."""
    frame = pd.DataFrame(index=pairs.index)
    frame["intercept"] = 1.0
    frame["log_dbh"] = pairs["log_dbh"]
    frame["dbh"] = pairs["dbh_cm"]
    frame["bal"] = pairs["bal"]
    frame["plot_ba"] = pairs["plot_ba"]
    frame["crown_ratio"] = pairs["crown_ratio"]
    if survival:
        frame["log_years"] = pairs["log_years"]
    for group in ("SE", "PL", "HW"):
        frame[f"species_{group}"] = (pairs["species_group"] == group).astype(float)
    return frame


def _standardize(train: pd.DataFrame, test: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, dict]:
    """Standardize continuous columns using training means/scales."""
    names = list(train.columns)
    means = train.mean()
    scales = train.std(ddof=0).replace(0, 1.0)
    return (
        ((train - means) / scales).to_numpy(),
        ((test - means) / scales).to_numpy(),
        {"columns": names, "means": means.to_dict(), "scales": scales.to_dict()},
    )


def _fit_dg(pairs: pd.DataFrame) -> dict:
    """Fit an OLS diameter-increment model."""
    fit = pairs[pairs["survived"] == 1].copy()
    x = _design(fit)
    y = fit["dg_cm_year"].to_numpy()
    beta, *_ = np.linalg.lstsq(x.to_numpy(), y, rcond=None)
    return {"kind": "ols", "columns": list(x.columns), "coefficients": beta.tolist()}


def _fit_survival(pairs: pd.DataFrame) -> dict:
    """Fit a logistic interval-survival model with a log-years term."""
    y = pairs["survived"].to_numpy()
    raw = _design(pairs, survival=True)
    means = raw.mean()
    scales = raw.std(ddof=0).replace(0, 1.0)
    means["intercept"] = 0.0
    scales["intercept"] = 1.0
    x = ((raw - means) / scales).to_numpy()
    n_features = x.shape[1]

    def objective(beta: np.ndarray) -> float:
        z = x @ beta
        p = 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))
        loss = -(y * np.log(p + EPS) + (1.0 - y) * np.log(1.0 - p + EPS)).sum()
        return float(loss + 1e-4 * np.sum(beta[1:] ** 2))

    result = minimize(
        objective,
        np.zeros(n_features),
        method="L-BFGS-B",
        options={"maxiter": 1000},
    )
    if not result.success:
        raise RuntimeError(result.message)
    return {
        "kind": "logistic",
        "columns": list(raw.columns),
        "means": means.to_dict(),
        "scales": scales.to_dict(),
        "coefficients": result.x.tolist(),
    }


def _fit_ingrowth(transitions: pd.DataFrame) -> dict:
    """Fit a Poisson plot-interval ingrowth model."""
    frame = transitions.copy()
    frame["log_ba"] = np.log(frame["ba_start_m2_ha"].clip(lower=0.1))
    frame["log_tph"] = np.log(frame["tph_start"].clip(lower=1.0))
    frame["treatment_C1"] = (frame["treatment"] == "C1").astype(float)
    frame["treatment_C2"] = (frame["treatment"] == "C2").astype(float)
    frame["treatment_S"] = (frame["treatment"] == "S").astype(float)
    x = pd.DataFrame(
        {
            "intercept": 1.0,
            "log_ba": frame["log_ba"],
            "log_tph": frame["log_tph"],
            "treatment_C1": frame["treatment_C1"],
            "treatment_C2": frame["treatment_C2"],
            "treatment_S": frame["treatment_S"],
        }
    )
    means = x.mean()
    scales = x.std(ddof=0).replace(0, 1.0)
    means["intercept"] = 0.0
    scales["intercept"] = 1.0
    z = ((x - means) / scales).to_numpy()
    y = frame["ingrowth_n"].to_numpy()

    def objective(beta: np.ndarray) -> float:
        eta = z @ beta
        mu = np.exp(np.clip(eta, -20, 20))
        return float((mu - y * eta).sum() + 1e-4 * np.sum(beta[1:] ** 2))

    result = minimize(
        objective,
        np.zeros(z.shape[1]),
        method="L-BFGS-B",
        options={"maxiter": 1000},
    )
    if not result.success:
        raise RuntimeError(result.message)
    return {
        "kind": "poisson",
        "columns": list(x.columns),
        "means": means.to_dict(),
        "scales": scales.to_dict(),
        "coefficients": result.x.tolist(),
    }


def _predict_dg(model: dict, pairs: pd.DataFrame) -> np.ndarray:
    """Predict annual DBH increment."""
    x = _design(pairs)[model["columns"]].to_numpy()
    return x @ np.asarray(model["coefficients"])


def _predict_survival(model: dict, pairs: pd.DataFrame) -> np.ndarray:
    """Predict interval survival probability."""
    raw = _design(pairs, survival=True)[model["columns"]]
    means = pd.Series(model["means"])
    scales = pd.Series(model["scales"])
    z = ((raw - means) / scales).to_numpy() @ np.asarray(model["coefficients"])
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def _predict_ingrowth(model: dict, transitions: pd.DataFrame) -> np.ndarray:
    """Predict plot-interval ingrowth count."""
    frame = transitions.copy()
    frame["log_ba"] = np.log(frame["ba_start_m2_ha"].clip(lower=0.1))
    frame["log_tph"] = np.log(frame["tph_start"].clip(lower=1.0))
    frame["treatment_C1"] = (frame["treatment"] == "C1").astype(float)
    frame["treatment_C2"] = (frame["treatment"] == "C2").astype(float)
    frame["treatment_S"] = (frame["treatment"] == "S").astype(float)
    x = pd.DataFrame(
        {
            "intercept": 1.0,
            "log_ba": frame["log_ba"],
            "log_tph": frame["log_tph"],
            "treatment_C1": frame["treatment_C1"],
            "treatment_C2": frame["treatment_C2"],
            "treatment_S": frame["treatment_S"],
        }
    )[model["columns"]]
    means = pd.Series(model["means"])
    scales = pd.Series(model["scales"])
    eta = ((x - means) / scales).to_numpy() @ np.asarray(model["coefficients"])
    return np.exp(np.clip(eta, -20, 20))


def _auc(y: np.ndarray, p: np.ndarray) -> float:
    """Rank-based AUC."""
    order = np.argsort(p)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(p) + 1)
    positives = y == 1
    n_pos = int(positives.sum())
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    return float((ranks[positives].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def _metrics(pairs: pd.DataFrame, pred_dg: np.ndarray, pred_surv: np.ndarray) -> dict:
    """Tree-level validation metrics."""
    survival = pairs["survived"].to_numpy()
    dg = pairs["dg_cm_year"].to_numpy()
    survived = survival == 1
    pred_surv = np.clip(pred_surv, 0, 1)
    return {
        "n_tree_intervals": len(pairs),
        "n_survived": int(survival.sum()),
        "dg_rmse": float(np.sqrt(np.nanmean((pred_dg[survived] - dg[survived]) ** 2))),
        "dg_mae": float(np.nanmean(np.abs(pred_dg[survived] - dg[survived]))),
        "dg_bias": float(np.nanmean(pred_dg[survived] - dg[survived])),
        "survival_brier": float(np.mean((pred_surv - survival) ** 2)),
        "survival_auc": _auc(survival, pred_surv),
        "survival_mean_pred": float(pred_surv.mean()),
        "survival_prevalence": float(survival.mean()),
    }


def main() -> None:
    """Fit, validate and write the tree-level model artifacts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--transitions", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    trees = pd.read_csv(args.trees)
    transitions = pd.read_csv(args.transitions)
    pairs = _pairs(trees)
    fold_rows = []
    ingrowth_rows = []
    for heldout in BLOCKS:
        train = pairs[pairs["block"] != heldout].copy()
        test = pairs[pairs["block"] == heldout].copy()
        dg_model = _fit_dg(train)
        surv_model = _fit_survival(train)
        ing_model = _fit_ingrowth(transitions[transitions["block"] != heldout].copy())
        pred_dg = _predict_dg(dg_model, test)
        pred_surv = _predict_survival(surv_model, test)
        metrics = _metrics(test, pred_dg, pred_surv)
        metrics["heldout_block"] = heldout
        fold_rows.append(metrics)
        test_transitions = transitions[transitions["block"] == heldout].copy()
        pred_ingrowth = _predict_ingrowth(ing_model, test_transitions)
        ingrowth_rows.append(
            {
                "heldout_block": heldout,
                "n_intervals": len(test_transitions),
                "observed_total": int(test_transitions["ingrowth_n"].sum()),
                "predicted_total": float(pred_ingrowth.sum()),
                "observed_mean": float(test_transitions["ingrowth_n"].mean()),
                "predicted_mean": float(pred_ingrowth.mean()),
                "mae": float(np.mean(np.abs(pred_ingrowth - test_transitions["ingrowth_n"]))),
                "poisson_deviance": float(
                    2
                    * np.sum(
                        np.where(
                            test_transitions["ingrowth_n"] > 0,
                            test_transitions["ingrowth_n"]
                            * np.log(
                                test_transitions["ingrowth_n"] / np.maximum(pred_ingrowth, EPS)
                            ),
                            0,
                        )
                        - (test_transitions["ingrowth_n"] - pred_ingrowth)
                    )
                ),
            }
        )
    pd.DataFrame(fold_rows).to_csv(args.out_dir / "tree_validation.csv", index=False)
    pd.DataFrame(ingrowth_rows).to_csv(args.out_dir / "ingrowth_validation.csv", index=False)

    final_dg = _fit_dg(pairs)
    final_surv = _fit_survival(pairs)
    final_ing = _fit_ingrowth(transitions)
    models = {
        "diameter_increment": final_dg,
        "survival": final_surv,
        "ingrowth": final_ing,
    }
    (args.out_dir / "tree_models.json").write_text(json.dumps(models, indent=2) + "\n")
    manifest = {
        "models": "afrf-kc-psp-tree-models-v1",
        "tree_intervals": len(pairs),
        "mortality_events": int((pairs["survived"] == 0).sum()),
        "ingrowth_intervals": len(transitions),
        "validation": "leave-one-block-out",
        "folds": list(BLOCKS),
        "no_age_or_site_index": True,
        "caveats": [
            "Tree records within plots are correlated; block CV is a transfer "
            "test, not independent replication.",
            "Survival and ingrowth use DBH presence as the working live-tree indicator.",
            "OH is excluded: only two OH trees are present and both die.",
            "No age or site index is assigned.",
            "No treatment response is fitted; treatment is only an ingrowth covariate.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(pd.DataFrame(fold_rows).to_string(index=False))
    print(pd.DataFrame(ingrowth_rows).to_string(index=False))


if __name__ == "__main__":
    main()
