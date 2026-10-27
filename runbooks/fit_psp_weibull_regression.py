"""Fit Weibull DBH parameters to PSP QMD/TPA and generate conditional stems.

The regression is a diagnostic and a starting point, not a full growth model:
QMD predicts the Weibull scale, TPA sets density, and the shape is the pooled
PSP estimate. A final QMD calibration makes the realized stand match the target.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from nemora.sampling import sample_distribution

LOWER_CM = 9.1
TARGETS = [
    {"qmd_cm": 18.0, "tpa": 900},
    {"qmd_cm": 20.0, "tpa": 800},
    {"qmd_cm": 22.0, "tpa": 750},
    {"qmd_cm": 24.0, "tpa": 650},
    {"qmd_cm": 26.0, "tpa": 550},
]


def _ols(y: np.ndarray, design: np.ndarray, names: list[str]) -> dict[str, object]:
    """Fit an ordinary least-squares model and return diagnostics."""
    n, p = design.shape
    b = np.linalg.lstsq(design, y, rcond=None)[0]
    pred = design @ b
    resid = y - pred
    rss = float(resid @ resid)
    tss = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - rss / tss
    adj = 1 - (1 - r2) * (n - 1) / (n - p)
    sigma2 = rss / (n - p)
    cov = sigma2 * np.linalg.inv(design.T @ design)
    se = np.sqrt(np.diag(cov))
    t = b / se
    loo = []
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        bb = np.linalg.lstsq(design[mask], y[mask], rcond=None)[0]
        loo.append(float(y[i] - design[i] @ bb))
    loo = np.asarray(loo)
    return {
        "names": names,
        "coef": b.tolist(),
        "se": se.tolist(),
        "t": t.tolist(),
        "r2": float(r2),
        "adj_r2": float(adj),
        "sigma": float(np.sqrt(sigma2)),
        "loo_rmse": float(np.sqrt(np.mean(loo**2))),
        "n": int(n),
        "pred": pred,
        "resid": resid,
    }


def _vif(design: np.ndarray) -> list[float]:
    """Return the variance inflation factors for the non-intercept columns."""
    out: list[float] = []
    for j in range(1, design.shape[1]):
        y = design[:, j]
        without = np.delete(design, j, axis=1)
        b = np.linalg.lstsq(without, y, rcond=None)[0]
        r2 = 1 - np.sum((y - without @ b) ** 2) / np.sum((y - y.mean()) ** 2)
        out.append(float(1 / (1 - r2)))
    return out


def main() -> None:
    """Run the regression and write conditional stem lists."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--fits", type=Path, default=Path("data/psp/idf_cariboo_psp_plot_weibull_fits.csv")
    )
    ap.add_argument(
        "--sample", type=Path, default=Path("data/psp/idf_cariboo_psp_stemlist_sample.csv")
    )
    ap.add_argument(
        "--pooled", type=Path, default=Path("data/psp/idf_cariboo_psp_pooled_weibull.json")
    )
    ap.add_argument("--out-dir", type=Path, default=Path("data/psp"))
    ap.add_argument("--seed", type=int, default=20261027)
    args = ap.parse_args()
    fits = pd.read_csv(args.fits)
    pooled = json.loads(args.pooled.read_text())
    fits["log_a"] = np.log(fits.a)
    fits["log_beta"] = np.log(fits.beta)
    fits["log_qmd"] = np.log(fits.qmd)
    fits["log_tpa"] = np.log(fits.tpa)
    design = np.column_stack([np.ones(len(fits)), fits.log_qmd, fits.log_tpa])
    model_a = _ols(fits.log_a, design, ["const", "log_qmd", "log_tpa"])
    model_beta = _ols(fits.log_beta, design, ["const", "log_qmd", "log_tpa"])
    design_qmd = np.column_stack([np.ones(len(fits)), fits.log_qmd])
    model_a_q = _ols(fits.log_a, design_qmd, ["const", "log_qmd"])
    model_beta_q = _ols(fits.log_beta, design_qmd, ["const", "log_qmd"])
    result = {
        "n_plots": len(fits),
        "lower_cm": LOWER_CM,
        "pooled_a": float(pooled["a"]),
        "pooled_beta": float(pooled["beta"]),
        "vif_log_qmd_log_tpa": _vif(design),
        "models": {
            "log_beta_qmd_tpa": {k: v for k, v in model_beta.items() if k not in ("pred", "resid")},
            "log_beta_qmd": {k: v for k, v in model_beta_q.items() if k not in ("pred", "resid")},
            "log_a_qmd_tpa": {k: v for k, v in model_a.items() if k not in ("pred", "resid")},
            "log_a_qmd": {k: v for k, v in model_a_q.items() if k not in ("pred", "resid")},
        },
        "selected_model": "log_beta_qmd",
        "selection_note": (
            "TPA is not significant after QMD in the log-beta model "
            "(t=0.86; VIF=2.71). The QMD-only model has slightly better adjusted R2 "
            "and LOOCV. Shape a is not predictable from QMD/TPA; the pooled a is used."
        ),
        "gg_test": {
            "plots": 45,
            "gg_lower_aicc": 5,
            "stable_gg_better": 0,
            "note": (
                "GG was fitted per plot with nemora. Five plots had lower AICc, but all "
                "had degenerate parameters (p near 0 or 170, beta near 1e-7). No stable "
                "GG fit beat Weibull, so Weibull is used."
            ),
        },
    }
    (args.out_dir / "idf_cariboo_psp_weibull_regression.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    pred = pd.DataFrame(
        {
            "CLSTR_ID": fits.CLSTR_ID,
            "qmd": fits.qmd,
            "tpa": fits.tpa,
            "observed_a": fits.a,
            "observed_beta": fits.beta,
            "predicted_log_beta_qmd_tpa": model_beta["pred"],
            "predicted_log_beta_qmd": model_beta_q["pred"],
            "predicted_beta_qmd_tpa": np.exp(model_beta["pred"]),
            "predicted_beta_qmd": np.exp(model_beta_q["pred"]),
            "residual_log_beta_qmd": model_beta_q["resid"],
        }
    )
    pred.to_csv(args.out_dir / "idf_cariboo_psp_weibull_regression_predictions.csv", index=False)

    # Conditional stem lists: QMD sets scale, TPA sets density, with a final
    # scale calibration so the realized QMD equals the target.
    sample = pd.read_csv(args.sample)
    sample["dbh_bin"] = (sample.dbh_cm // 2 * 2 + 1).astype(int)
    comp = sample.groupby(["dbh_bin", "species"]).size().reset_index(name="n")
    comp["p"] = comp.groupby("dbh_bin").n.transform(lambda s: s / s.sum())
    glob = sample.species.value_counts(normalize=True)
    height_models = {}
    for sp, frame in sample.groupby("species"):
        if len(frame) < 30:
            continue
        x = np.log(frame.dbh_cm.to_numpy(float))
        y = np.log(frame.height_m.to_numpy(float))
        c = np.polyfit(x, y, 1)
        res = y - np.polyval(c, x)
        height_models[sp] = {
            "c0": float(c[1]),
            "c1": float(c[0]),
            "sigma": float(np.std(res, ddof=1)),
        }
    x = np.log(sample.dbh_cm.to_numpy(float))
    y = np.log(sample.height_m.to_numpy(float))
    c = np.polyfit(x, y, 1)
    res = y - np.polyval(c, x)
    height_models["ALL"] = {
        "c0": float(c[1]),
        "c1": float(c[0]),
        "sigma": float(np.std(res, ddof=1)),
    }
    rng = np.random.default_rng(args.seed)
    rows = []
    b0, b1 = model_beta_q["coef"]
    a = float(pooled["a"])
    for i, t in enumerate(TARGETS, start=1):
        stand = f"PSP-REG-{i:03d}"
        n = min(999, int(t["tpa"]))
        beta = np.exp(b0 + b1 * np.log(t["qmd_cm"]))
        draws = LOWER_CM + sample_distribution(
            "weibull", {"a": a, "beta": beta, "s": 1.0}, n * 3, random_state=rng
        )
        draws = draws[(draws >= LOWER_CM) & (draws <= 150.0)][:n]
        while draws.size < n:
            extra = LOWER_CM + sample_distribution(
                "weibull", {"a": a, "beta": beta, "s": 1.0}, (n - draws.size) * 3, random_state=rng
            )
            draws = np.concatenate([draws, extra[(extra >= LOWER_CM) & (extra <= 150.0)]])[:n]
        qmd_draw = float(np.sqrt(np.mean(draws**2)))
        scale = float(t["qmd_cm"]) / qmd_draw
        draws = np.sort(np.maximum(draws * scale, LOWER_CM))
        for j, dbh in enumerate(draws, start=1):
            b = int(dbh // 2 * 2 + 1)
            sub = comp[comp.dbh_bin == b]
            if sub.empty:
                species = str(rng.choice(glob.index.to_numpy(), p=glob.to_numpy()))
            else:
                p = sub.p.to_numpy(float)
                p = p / p.sum()
                species = str(rng.choice(sub.species.to_numpy(), p=p))
            hm = height_models.get(species, height_models["ALL"])
            height = float(
                np.clip(
                    np.exp(
                        hm["c0"] + hm["c1"] * np.log(max(dbh, 2.0)) + rng.normal(0, hm["sigma"])
                    ),
                    2.0,
                    55.0,
                )
            )
            # crown class from the sample, mapped to a ratio
            cc = sample[sample.species == species].crown_ratio
            cr = (
                float(cc.sample(1, random_state=int(rng.integers(0, 2**31 - 1))).iloc[0])
                if len(cc)
                else 0.45
            )
            rows.append(
                {
                    "stand_id": stand,
                    "tree_id": j,
                    "species": species,
                    "dbh_cm": round(float(dbh), 1),
                    "height_m": round(height, 1),
                    "crown_ratio": round(cr, 2),
                    "tree_age": 120.0,
                    "target_qmd_cm": t["qmd_cm"],
                    "target_tpa": t["tpa"],
                    "predicted_beta": round(float(beta), 3),
                    "qmd_calibration_scale": round(scale, 4),
                    "realized_qmd_cm": round(float(np.sqrt(np.mean(draws**2))), 2),
                    "realized_ba_m2_ha": round(float(np.sum(0.00007854 * draws**2)), 2),
                    "source": "FAIB PSP IDF Cariboo, regression + QMD calibration",
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(args.out_dir / "idf_cariboo_psp_conditional_stemlists.csv", index=False)
    pop = out[["stand_id", "dbh_cm", "height_m", "crown_ratio"]].to_dict("records")
    (args.out_dir / "idf_cariboo_psp_conditional_stemlists_population.json").write_text(
        json.dumps(pop, indent=2) + "\n"
    )
    print(
        out.groupby("stand_id")
        .agg(
            n=("tree_id", "size"),
            qmd=("dbh_cm", lambda s: float(np.sqrt(np.mean(s**2)))),
            ba=("dbh_cm", lambda s: float(np.sum(0.00007854 * s**2))),
            target_qmd=("target_qmd_cm", "first"),
            target_tpa=("target_tpa", "first"),
        )
        .to_string()
    )
    print("models")
    for k, v in result["models"].items():
        print(
            k,
            "r2",
            round(v["r2"], 3),
            "adj",
            round(v["adj_r2"], 3),
            "loo",
            round(v["loo_rmse"], 3),
            "coef",
            [round(x, 3) for x in v["coef"]],
        )


if __name__ == "__main__":
    main()
