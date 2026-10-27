#!/usr/bin/env python3
"""Build synthetic IDF Cariboo stem lists from public FAIB PSPs.

The FAIB ground-plot compilation is public under the Open Government Licence -
British Columbia. This script filters the PSP tree detail to live trees in
first-measurement, Douglas-fir-leading IDF stands in the Williams Lake and
100 Mile House TSAs, fits a shifted Weibull DBH distribution, and generates
synthetic one-hectare stem lists by inverse-CDF sampling.

The synthetic lists are a regional IDF analog, not Knife Creek data. The
effective information is the number of sampled PSP plots and trees; drawing
more trees does not create new independent plots.

Usage::

    python runbooks/build_psp_stemlists.py \
        --raw-dir /path/to/faib_psp_csvs \
        --out-dir data/psp \
        --stands 24
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from nemora.core import InventorySpec
from nemora.fit import fit_inventory
from nemora.sampling import sample_distribution

LOWER_CM = 9.1
MAX_TREES = 999
CROWN_RATIO = {"C": 0.65, "I": 0.55, "S": 0.45, "D": 0.30}


def _read_raw(raw_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Read the FAIB header, visit, tree and site-age CSVs."""
    header = pd.read_csv(raw_dir / "faib_header.csv", low_memory=False)
    visits = pd.read_csv(raw_dir / "faib_sample_byvisit.csv", low_memory=False)
    trees = pd.read_csv(raw_dir / "faib_tree_detail.csv", low_memory=False)
    site_age = pd.read_csv(raw_dir / "faib_compiled_spcsmries_siteage.csv", low_memory=False)
    return header, visits, trees, site_age


def _select_plots(header: pd.DataFrame, visits: pd.DataFrame) -> pd.DataFrame:
    """Select first-measurement IDF PSPs in the Cariboo TSAs."""
    idf = header[
        (header["BEC_ZONE"] == "IDF")
        & header["TSA_DESC"].isin(["Williams Lake TSA", "100 Mile House TSA"])
    ][
        [
            "SITE_IDENTIFIER",
            "BEC_ZONE",
            "BEC_SBZ",
            "BEC_VAR",
            "TSA_DESC",
            "SAMPLE_ESTABLISHMENT_TYPE",
        ]
    ]
    first = visits[visits["FIRST_MSMT"] == "Y"][
        ["SITE_IDENTIFIER", "CLSTR_ID", "VISIT_NUMBER", "DBH_LIMIT_TAG", "PROJ_AGE_1"]
    ]
    selected = idf.merge(first, on="SITE_IDENTIFIER", how="inner")
    return selected[selected["SAMPLE_ESTABLISHMENT_TYPE"].isin(["PSP_G", "PSP_R"])].copy()


def _clean_trees(trees: pd.DataFrame, plots: pd.DataFrame) -> pd.DataFrame:
    """Filter live trees and join the plot metadata."""
    trees = trees[trees["CLSTR_ID"].isin(set(plots["CLSTR_ID"]))].copy()
    for column in ("DBH", "PHF_TREE", "PLOT_WT"):
        trees[column] = pd.to_numeric(trees[column], errors="coerce")
    trees = trees[
        (trees["LV_D"] == "L")
        & trees["DBH"].notna()
        & (trees["DBH"] > 0)
        & trees["PHF_TREE"].notna()
        & (trees["PHF_TREE"] > 0)
    ].copy()
    trees = trees.merge(
        plots[["CLSTR_ID", "DBH_LIMIT_TAG", "PROJ_AGE_1", "BEC_SBZ", "BEC_VAR", "TSA_DESC"]],
        on="CLSTR_ID",
        how="left",
    )
    # Use a common 9.1 cm lower bound so the fitted distribution and the
    # comparison across plots are consistent; the raw PSP tag varies (2.0 or
    # 9.1 cm), and including 2-9 cm saplings dominates the DBH PDF.
    trees = trees[trees["DBH"] >= LOWER_CM].copy()
    trees["ba"] = 0.00007854 * trees["DBH"] ** 2 * trees["PHF_TREE"]
    return trees


def _plot_summary(trees: pd.DataFrame) -> pd.DataFrame:
    """Summarise each plot and retain the Douglas-fir-leading mature IDF stands."""
    lead = (
        trees.groupby(["CLSTR_ID", "SPECIES"])["ba"]
        .sum()
        .reset_index()
        .sort_values(["CLSTR_ID", "ba"], ascending=[True, False])
        .groupby("CLSTR_ID")
        .head(1)[["CLSTR_ID", "SPECIES"]]
    )
    summary = (
        trees.groupby("CLSTR_ID")
        .agg(
            tpa=("PHF_TREE", "sum"),
            ba=("ba", "sum"),
            qmd=(
                "DBH",
                lambda values: float(
                    np.sqrt(
                        np.sum(values**2 * trees.loc[values.index, "PHF_TREE"])
                        / np.sum(trees.loc[values.index, "PHF_TREE"])
                    )
                ),
            ),
            n=("DBH", "size"),
        )
        .reset_index()
        .merge(lead, on="CLSTR_ID")
        .merge(
            trees[["CLSTR_ID", "PROJ_AGE_1", "BEC_SBZ", "BEC_VAR", "TSA_DESC"]].drop_duplicates(
                "CLSTR_ID"
            ),
            on="CLSTR_ID",
        )
    )
    return summary[
        (summary["SPECIES"] == "FD")
        & summary["PROJ_AGE_1"].between(80, 180)
        & summary["ba"].between(20, 40)
        & summary["qmd"].between(15, 25)
    ].copy()


def _fit_weibull(frame: pd.DataFrame) -> dict[str, float]:
    """Fit a lower-truncated Weibull to one plot's DBH tallies."""
    shifted = frame["DBH"].to_numpy(float) - LOWER_CM
    weights = frame["PHF_TREE"].to_numpy(float)
    bins = np.arange(1.0, max(12.0, shifted.max() + 2.0), 2.0)
    tallies = np.zeros_like(bins)
    for value, weight in zip(shifted, weights, strict=False):
        index = int((value - bins[0]) // 2.0)
        if 0 <= index < bins.size:
            tallies[index] += weight
    inventory = InventorySpec(
        name="psp",
        sampling="psp",
        bins=bins,
        tallies=tallies,
        metadata={"grouped": True},
    )
    result = fit_inventory(inventory, ["weibull"], {})[0]
    return {
        "a": float(result.parameters["a"]),
        "beta": float(result.parameters["beta"]),
        "rss": float(result.gof.get("rss", np.nan)),
        "aicc": float(result.gof.get("aicc", np.nan)),
        "ks": float(result.gof.get("ks", np.nan)),
    }


def _fit_plots(trees: pd.DataFrame, plots: pd.DataFrame) -> pd.DataFrame:
    """Fit every selected plot and keep the stable fits."""
    rows = []
    for cluster in plots["CLSTR_ID"]:
        frame = trees[trees["CLSTR_ID"] == cluster]
        if len(frame) < 20:
            continue
        try:
            fit = _fit_weibull(frame)
        except (ValueError, RuntimeError, FloatingPointError):
            continue
        row = plots[plots["CLSTR_ID"] == cluster].iloc[0].to_dict()
        row.update(fit)
        rows.append(row)
    fitted = pd.DataFrame(rows)
    return fitted[
        fitted["a"].between(0.5, 3.5) & fitted["beta"].between(3.0, 30.0) & (fitted["ks"] < 0.15)
    ].copy()


def _species_models(
    trees: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, float], dict[str, dict[str, float]]]:
    """Build species-by-DBH composition and a simple height-DBH model."""
    trees = trees.copy()
    trees["dbh_bin"] = (trees["DBH"] // 2 * 2 + 1).astype(int)
    composition = trees.groupby(["dbh_bin", "SPECIES"])["PHF_TREE"].sum().reset_index()
    composition["p"] = composition.groupby("dbh_bin")["PHF_TREE"].transform(
        lambda values: values / values.sum()
    )
    global_composition = trees.groupby("SPECIES")["PHF_TREE"].sum()
    global_composition = global_composition / global_composition.sum()
    height_models: dict[str, dict[str, float]] = {}
    for species, frame in trees.groupby("SPECIES"):
        frame = frame[(frame["HEIGHT"] > 0) & (frame["DBH"] > 0)]
        if len(frame) < 30:
            continue
        x = np.log(frame["DBH"].to_numpy(float))
        y = np.log(frame["HEIGHT"].to_numpy(float))
        coefficient = np.polyfit(x, y, 1)
        residual = y - np.polyval(coefficient, x)
        height_models[str(species)] = {
            "c0": float(coefficient[1]),
            "c1": float(coefficient[0]),
            "sigma": float(np.std(residual, ddof=1)),
            "n": len(frame),
        }
    x = np.log(trees["DBH"].to_numpy(float))
    y = np.log(trees["HEIGHT"].to_numpy(float))
    coefficient = np.polyfit(x, y, 1)
    residual = y - np.polyval(coefficient, x)
    height_models["ALL"] = {
        "c0": float(coefficient[1]),
        "c1": float(coefficient[0]),
        "sigma": float(np.std(residual, ddof=1)),
        "n": len(trees),
    }
    return composition, global_composition.to_dict(), height_models


def _sample_crown(rng: np.random.Generator, trees: pd.DataFrame, species: str) -> float:
    """Sample a crown class and map it to a crown ratio."""
    subset = trees[trees["SPECIES"] == species]["CR_CL"].dropna()
    if subset.empty:
        subset = trees["CR_CL"].dropna()
    if subset.empty:
        return 0.45
    counts = subset.value_counts(normalize=True)
    crown_class = str(rng.choice(counts.index.to_numpy(), p=counts.to_numpy()))
    return CROWN_RATIO.get(crown_class, 0.45)


def _draw_stands(
    fitted: pd.DataFrame,
    trees: pd.DataFrame,
    pooled: dict[str, float],
    composition: pd.DataFrame,
    global_composition: dict[str, float],
    height_models: dict[str, dict[str, float]],
    *,
    stands: int,
    seed: int,
) -> pd.DataFrame:
    """Generate synthetic one-hectare stem lists."""
    rng = np.random.default_rng(seed)
    chosen = fitted.sample(n=stands, replace=False, random_state=seed)
    rows: list[dict[str, object]] = []
    for index, plot in enumerate(chosen.itertuples(index=False), start=1):
        stand_id = f"PSP-IDF-{index:03d}"
        target_count = int(max(50, min(MAX_TREES, rng.poisson(plot.tpa))))
        draws = LOWER_CM + sample_distribution(
            "weibull",
            {"a": pooled["a"], "beta": pooled["beta"], "s": 1.0},
            target_count * 3,
            random_state=rng,
        )
        draws = draws[(draws >= LOWER_CM) & (draws <= 150.0)][:target_count]
        while draws.size < target_count:
            extra = LOWER_CM + sample_distribution(
                "weibull",
                {"a": pooled["a"], "beta": pooled["beta"], "s": 1.0},
                (target_count - draws.size) * 3,
                random_state=rng,
            )
            draws = np.concatenate([draws, extra[(extra >= LOWER_CM) & (extra <= 150.0)]])[
                :target_count
            ]
        draw_ba = float(np.sum(0.00007854 * draws**2))
        if draw_ba > 0:
            draws = draws * np.sqrt(float(plot.ba) / draw_ba)
        draws = np.sort(draws)
        for tree_id, dbh in enumerate(draws, start=1):
            dbh_bin = int(dbh // 2 * 2 + 1)
            subset = composition[composition["dbh_bin"] == dbh_bin]
            if subset.empty:
                species = str(
                    rng.choice(
                        list(global_composition),
                        p=np.asarray(list(global_composition.values()), dtype=float),
                    )
                )
            else:
                probabilities = subset["p"].to_numpy(float)
                probabilities = probabilities / probabilities.sum()
                species = str(rng.choice(subset["SPECIES"].to_numpy(), p=probabilities))
            model = height_models.get(species, height_models["ALL"])
            height = float(
                np.exp(
                    model["c0"]
                    + model["c1"] * np.log(max(dbh, 2.0))
                    + rng.normal(0.0, model["sigma"])
                )
            )
            height = float(np.clip(height, 2.0, 55.0))
            rows.append(
                {
                    "stand_id": stand_id,
                    "tree_id": tree_id,
                    "species": species,
                    "dbh_cm": round(float(dbh), 1),
                    "height_m": round(height, 1),
                    "crown_ratio": round(_sample_crown(rng, trees, species), 2),
                    "tree_age": round(
                        float(np.clip(plot.PROJ_AGE_1 + rng.normal(0, 5), 40, 250)), 1
                    ),
                    "source_plot": plot.CLSTR_ID,
                    "source_tpa": round(float(plot.tpa), 1),
                    "source_ba_m2_ha": round(float(plot.ba), 2),
                    "source_qmd_cm": round(float(plot.qmd), 2),
                    "source_age": float(plot.PROJ_AGE_1),
                    "bec": f"IDF{plot.BEC_SBZ}",
                    "tsa": plot.TSA_DESC,
                    "synthetic": True,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    """Run the selection, fitting, generation and export."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--stands", type=int, default=24)
    parser.add_argument("--seed", type=int, default=20261027)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    header, visits, tree_raw, _site_age = _read_raw(args.raw_dir)
    plots = _select_plots(header, visits)
    trees = _clean_trees(tree_raw, plots)
    summary = _plot_summary(trees)
    selected = trees[trees["CLSTR_ID"].isin(set(summary["CLSTR_ID"]))].copy()
    fitted = _fit_plots(selected, summary)
    pooled = _fit_weibull(selected)
    composition, global_composition, height_models = _species_models(selected)
    stemlist = _draw_stands(
        fitted,
        selected,
        pooled,
        composition,
        global_composition,
        height_models,
        stands=args.stands,
        seed=args.seed,
    )

    summary.to_csv(args.out_dir / "idf_cariboo_psp_plots.csv", index=False)
    fitted.to_csv(args.out_dir / "idf_cariboo_psp_plot_weibull_fits.csv", index=False)
    (args.out_dir / "idf_cariboo_psp_pooled_weibull.json").write_text(
        json.dumps(
            {
                **pooled,
                "lower_cm": LOWER_CM,
                "n_plots": len(fitted),
                "n_trees": len(selected),
                "seed": args.seed,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    stemlist.to_csv(args.out_dir / "idf_cariboo_psp_stemlist_sample.csv", index=False)
    population = stemlist[["stand_id", "dbh_cm", "height_m", "crown_ratio"]].to_dict("records")
    (args.out_dir / "idf_cariboo_psp_stemlist_population.json").write_text(
        json.dumps(population, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"selected plots={len(summary)} stable fits={len(fitted)} "
        f"stands={stemlist['stand_id'].nunique()} trees={len(stemlist)}"
    )


if __name__ == "__main__":
    main()
