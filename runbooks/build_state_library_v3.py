#!/usr/bin/env python3
"""Build the Knife Creek GWM 2007 state-transition library v3.

The v3 library extends v2 in two ways. It follows each stand/regime chain
through eight 30-year entries, and it counts the post-FVS clump harvest volume
in the transition cut. The v2 library counted only the FVS `RTCuM` cut and
therefore under-reported clump harvest. The selected clump-reserve rule is:

1. FVS-BC runs a GWM full-range BDq cut to the legal D and B.
2. The after-treatment tree list is post-processed: mature trees >=37.5 cm are
   grouped into DBH-ranked chunks of six (a non-spatial clump proxy); the
   largest three trees above D in each chunk are reserved and the remaining
   trees above D are harvested.
3. The residual list is resampled to a one-hectare population and grown for the
   next 30-year entry.

The extra entries allow the canonical state graph to contain repeated state
classes, which is the minimum evidence needed for a multi-entry policy graph.
The clump proxy remains provisional and the library is not a legal-compliance
product.

Usage::

    PYTHONPATH=/path/to/fresh-fvsbc/src \
      /path/to/fvsbc-build-venv/bin/python runbooks/build_state_library_v3.py \
      --sample data/psp/idf_cariboo_psp_stemlist_sample.csv \
      --out-dir ws4/state_library_v3 \
      --runtime-dir runtime/state_library_v3 \
      --entries 8
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import UnknownTableError, read_table
from fresh_fvsbc.run import run_population

DEFAULT_STANDS = (
    "PSP-IDF-024",
    "PSP-IDF-005",
    "PSP-IDF-015",
    "PSP-IDF-012",
    "PSP-IDF-004",
    "PSP-IDF-013",
    "PSP-IDF-006",
    "PSP-IDF-008",
)
REGIMES = {
    "GWM_HIGH": {"B": 29.0, "large_ba": 16.0, "D": 70.0, "q": 1.25, "q_min": 1.20, "q_max": 1.35},
    "GWM_MODERATE": {
        "B": 22.0,
        "large_ba": 11.0,
        "D": 60.0,
        "q": 1.25,
        "q_min": 1.25,
        "q_max": 1.35,
    },
    "GWM_LOW": {"B": 16.0, "large_ba": 6.0, "D": 50.0, "q": 1.30, "q_min": 1.25, "q_max": 1.40},
}
LARGE_THRESHOLD = 37.5
FT2_PER_M2 = 4.356
CLUMP_SIZE = 6
RESERVE_TREES = 3
MAX_POPULATION = 900
RNG_SEED = 20261028


def _q_factor(rows: pd.DataFrame) -> float:
    """Return the median q-factor from 5 cm TPH classes."""
    if rows.empty:
        return float("nan")
    classes = (rows["DBH"] // 5 * 5 + 2.5).astype(float)
    density = rows.assign(dbh_class=classes).groupby("dbh_class")["TPH"].sum()
    all_classes = np.arange(classes.min(), classes.max() + 5.0, 5.0)
    density = density.reindex(all_classes, fill_value=0.0)
    ratios = []
    for lower, upper in itertools.pairwise(all_classes):
        if density.loc[lower] > 0 and density.loc[upper] > 0:
            ratios.append(float(density.loc[lower] / density.loc[upper]))
    return float(np.median(ratios)) if ratios else float("nan")


def _ba(rows: pd.DataFrame) -> float:
    """Return basal area in m²/ha from DBH and TPH."""
    return float((0.00007854 * rows["DBH"] ** 2 * rows["TPH"]).sum()) if len(rows) else 0.0


def _reserve_mark(after: pd.DataFrame, regime: str) -> tuple[pd.DataFrame, dict[str, float]]:
    """Apply the selected clump-reserve rule to an after-treatment list."""
    spec = REGIMES[regime]
    large = after[after["DBH"] >= LARGE_THRESHOLD].sort_values("DBH", ascending=False)
    harvest_indices: set[int] = set()
    reserved_indices: set[int] = set()
    for start in range(0, len(large), CLUMP_SIZE):
        chunk = large.iloc[start : start + CLUMP_SIZE]
        above_d = chunk[chunk["DBH"] > spec["D"]]
        reserved_indices.update(above_d.head(RESERVE_TREES).index)
        harvest_indices.update(above_d.iloc[RESERVE_TREES:].index)
    kept = after[~after.index.isin(harvest_indices)].copy()
    kept_large = kept[kept["DBH"] >= LARGE_THRESHOLD]
    reserve = kept[kept["DBH"] > spec["D"]]
    q_factor = _q_factor(kept)
    metrics = {
        "post_ba_m2_ha": _ba(kept),
        "post_qmd_cm": float(np.sqrt(np.sum(kept["DBH"] ** 2 * kept["TPH"]) / kept["TPH"].sum()))
        if len(kept) and kept["TPH"].sum() > 0
        else np.nan,
        "post_tph": float(kept["TPH"].sum()),
        "post_large_ba_m2_ha": _ba(kept_large),
        "post_large_tph": float(kept_large["TPH"].sum()),
        "post_reserve_above_d_m2_ha": _ba(reserve),
        "post_max_dbh_cm": float(kept["DBH"].max()) if len(kept) else np.nan,
        "post_q_factor": q_factor,
        "mean_large_crown_width_m": float(kept_large["CrWidth"].mean()) if len(kept_large) else 0.0,
        "mean_large_crown_ratio": float(kept_large["PctCr"].mean()) if len(kept_large) else 0.0,
        "clump_count_per_ha": float(kept_large["TPH"].sum()) / CLUMP_SIZE,
        "clump_crown_cover_fraction": min(
            1.0,
            float(kept_large["TPH"].sum())
            * np.pi
            * (float(kept_large["CrWidth"].mean()) / 2.0) ** 2
            / 10000.0,
        )
        if len(kept_large)
        else 0.0,
        "reserved_trees": float(len(reserved_indices)),
        "clump_harvested_trees": float(len(harvest_indices)),
        "clump_removed_large_ba_m2_ha": _ba(after) - _ba(kept),
        "clump_removed_large_tph": float(
            after.loc[list(harvest_indices), "TPH"].sum() if harvest_indices else 0.0
        ),
        "clump_removed_m3_ha": float(
            (
                after.loc[list(harvest_indices), "TCuM"] * after.loc[list(harvest_indices), "TPH"]
            ).sum()
            if harvest_indices
            else 0.0
        ),
    }
    metrics["total_ba_ok"] = bool(metrics["post_ba_m2_ha"] >= spec["B"])
    metrics["large_ba_ok"] = bool(metrics["post_large_ba_m2_ha"] >= spec["large_ba"])
    metrics["max_dbh_ok"] = bool(
        np.isfinite(metrics["post_max_dbh_cm"]) and metrics["post_max_dbh_cm"] >= spec["D"]
    )
    metrics["q_ok"] = bool(
        np.isfinite(metrics["post_q_factor"])
        and spec["q_min"] <= metrics["post_q_factor"] <= spec["q_max"]
    )
    metrics["stand_structure_pass"] = all(
        metrics[name] for name in ("total_ba_ok", "large_ba_ok", "max_dbh_ok", "q_ok")
    )
    return kept, metrics


def _keywords(regime: str, cycle: int) -> list[Keyword]:
    """Return the GWM full-range BDq keyword for one entry."""
    spec = REGIMES[regime]
    return [
        Keyword(
            "THINQFA",
            (
                str(cycle),
                "0.0",
                str(spec["D"]),
                "0",
                str(spec["q"]),
                "5.0",
                str(round(spec["B"] * FT2_PER_M2, 2)),
            ),
            supplemental=("0",),
        )
    ]


def _run_case(
    population: list[dict[str, object]],
    *,
    stand: str,
    age: float,
    regime: str,
    runtime_dir: Path,
) -> object:
    """Run one 30-year GWM entry."""
    keywords = [
        Keyword(
            "DATABASE",
            (),
            ("DSNOut", "FVSOut.db", "TreeLIDB", "CutLIDB", "ATRTLIDB", "Summary"),
        ),
        Keyword("STDIDENT", (f"{stand} {regime}",)),
        Keyword("STDINFO", ("CAR", "IDFdk3/01", "0", "200", "35", "16")),
        Keyword("MANAGED", ("0", "1")),
        Keyword("SITECODE", ("FD", "60")),
        Keyword("INVYEAR", ("0",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", "10")),
        Keyword("NUMCYCLE", ("4",)),
        Keyword("RANNSEED", ("1",)),
        Keyword("TREELIST", ("4",)),
        Keyword("CUTLIST", ("4",)),
        Keyword("ATRTLIST", ("4",)),
        *_keywords(regime, 4),
        Keyword("PROCESS"),
        Keyword("STOP"),
    ]
    return run_population(
        population,
        directory=runtime_dir / f"{stand}__{regime}",
        species="FD",
        tree_age=age,
        keywords=keywords,
    )


def _run_no_cut(
    population: list[dict[str, object]],
    *,
    stand: str,
    age: float,
    runtime_dir: Path,
) -> object:
    """Grow one 30-year entry without a cut to obtain the year-30 tree list."""
    keywords = [
        Keyword(
            "DATABASE",
            (),
            ("DSNOut", "FVSOut.db", "TreeLIDB", "CutLIDB", "ATRTLIDB", "Summary"),
        ),
        Keyword("STDIDENT", (f"{stand} NO CUT",)),
        Keyword("STDINFO", ("CAR", "IDFdk3/01", "0", "200", "35", "16")),
        Keyword("MANAGED", ("0", "1")),
        Keyword("SITECODE", ("FD", "60")),
        Keyword("INVYEAR", ("0",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", "10")),
        Keyword("NUMCYCLE", ("3",)),
        Keyword("RANNSEED", ("1",)),
        Keyword("TREELIST", ("3",)),
        Keyword("PROCESS"),
        Keyword("STOP"),
    ]
    return run_population(
        population,
        directory=runtime_dir,
        species="FD",
        tree_age=age,
        keywords=keywords,
    )


def _extract_no_cut(
    result: object,
    *,
    stand: str,
    regime: str,
    entry: int,
    age: float,
) -> tuple[dict[str, object], pd.DataFrame, list[dict[str, object]]]:
    """Extract a no-cut entry from the year-30 tree list and mark the reserve."""
    summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
    trees = read_table(result.database, "FVS_TreeList_Metric")
    after = trees[trees["Year"] == 30].copy()
    if after.empty:
        raise RuntimeError(f"no year-30 tree list for {stand} entry {entry}")
    after["ba"] = 0.00007854 * after["DBH"] ** 2 * after["TPH"]
    kept, metrics = _reserve_mark(after, regime)
    row = summary.loc[summary["Year"] == 30].iloc[0]
    transition = _transition_from_metrics(
        metrics,
        stand=stand,
        regime=regime,
        entry=entry,
        age=age,
        summary_row=row,
        fvs_cut_tph=0.0,
        fvs_cut_m3=0.0,
    )
    curves = _curve_rows(summary, transition["transition_id"], stand, regime, entry)
    return transition, kept, curves


def _population_from_tree_list(
    kept: pd.DataFrame, stand: str, seed: int
) -> list[dict[str, object]]:
    """Resample a weighted after-treatment list into a one-hectare population."""
    tph = kept["TPH"].clip(lower=0.0)
    if tph.sum() <= 0:
        return []
    count = min(MAX_POPULATION, max(1, round(tph.sum())))
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(kept), size=count, replace=True, p=(tph / tph.sum()).to_numpy())
    rows = kept.iloc[indices]
    return [
        {
            "stand_id": stand,
            "dbh_cm": float(row.DBH),
            "height_m": float(row.Ht),
            "crown_ratio": min(0.89, max(0.0, float(row.PctCr) / 100.0)),
        }
        for row in rows.itertuples(index=False)
    ]


def _transition_from_metrics(
    metrics: dict[str, float],
    *,
    stand: str,
    regime: str,
    entry: int,
    age: float,
    summary_row: object,
    fvs_cut_tph: float,
    fvs_cut_m3: float,
) -> dict[str, object]:
    """Build a transition row from the marked stand metrics."""
    return {
        "transition_id": f"GWM_E{entry}__{stand}__{regime}",
        "from_state": f"GWM_E{entry}__{stand}__{regime}",
        "to_state": f"GWM_R{entry}__{stand}__{regime}",
        "stand": stand,
        "basis": "GWM_2007",
        "regime": regime,
        "entry": entry,
        "entry_age": age,
        "target_b_m2_ha": REGIMES[regime]["B"],
        "target_large_ba_m2_ha": REGIMES[regime]["large_ba"],
        "target_d_cm": REGIMES[regime]["D"],
        "target_q": REGIMES[regime]["q"],
        "pre_ba_m2_ha": float(summary_row.BA),
        "pre_qmd_cm": float(summary_row.QMD),
        "pre_tph": float(summary_row.Tph),
        "pre_volume_m3_ha": float(summary_row.TCuM),
        "post_ba_m2_ha": metrics["post_ba_m2_ha"],
        "post_qmd_cm": metrics["post_qmd_cm"],
        "post_tph": metrics["post_tph"],
        "post_q_factor": metrics["post_q_factor"],
        "post_max_dbh_cm": metrics["post_max_dbh_cm"],
        "post_canopy_ccf": float(summary_row.ATCCF)
        if hasattr(summary_row, "ATCCF")
        else float(summary_row.CCF),
        "post_large_ba_m2_ha": metrics["post_large_ba_m2_ha"],
        "post_large_tph": metrics["post_large_tph"],
        "post_reserve_above_d_m2_ha": metrics["post_reserve_above_d_m2_ha"],
        "mean_large_crown_width_m": metrics["mean_large_crown_width_m"],
        "mean_large_crown_ratio": metrics["mean_large_crown_ratio"],
        "clump_count_per_ha": metrics["clump_count_per_ha"],
        "clump_crown_cover_fraction": metrics["clump_crown_cover_fraction"],
        "reserved_trees": metrics["reserved_trees"],
        "clump_harvested_trees": metrics["clump_harvested_trees"],
        "clump_removed_large_ba_m2_ha": metrics["clump_removed_large_ba_m2_ha"],
        "clump_removed_large_tph": metrics["clump_removed_large_tph"],
        "fvs_cut_tph": fvs_cut_tph + metrics.get("clump_removed_large_tph", 0.0),
        "fvs_cut_m3_ha": fvs_cut_m3 + metrics.get("clump_removed_m3_ha", 0.0),
        "clump_removed_m3_ha": metrics.get("clump_removed_m3_ha", 0.0),
        "stand_structure_pass": metrics["stand_structure_pass"],
        "legal_compliance": False,
    }


def _curve_rows(
    summary: pd.DataFrame,
    transition_id: str,
    stand: str,
    regime: str,
    entry: int,
) -> list[dict[str, object]]:
    """Convert an FVS summary to transition curve rows."""
    return [
        {
            "transition_id": transition_id,
            "stand": stand,
            "regime": regime,
            "entry": entry,
            "year": int(point.Year),
            "ba_m2_ha": float(point.BA),
            "qmd_cm": float(point.QMD),
            "tph": float(point.Tph),
            "volume_m3_ha": float(point.TCuM),
            "canopy_ccf": float(point.CCF),
        }
        for point in summary[summary["Year"] <= 30].itertuples(index=False)
    ]


def _extract_case(
    result: object,
    *,
    stand: str,
    regime: str,
    entry: int,
    age: float,
) -> tuple[dict[str, object], pd.DataFrame, list[dict[str, object]]]:
    """Extract one entry, its marked residual list and curve rows."""
    summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
    try:
        atrt = read_table(result.database, "FVS_ATRTList_Metric")
        after = atrt[atrt["Year"] == 30].copy()
    except UnknownTableError:
        after = pd.DataFrame()
    if after.empty:
        raise RuntimeError(f"no after-treatment list for {stand} {regime} entry {entry}")
    after["ba"] = 0.00007854 * after["DBH"] ** 2 * after["TPH"]
    kept, metrics = _reserve_mark(after, regime)
    row = summary.loc[summary["Year"] == 30].iloc[0]
    state_id = f"GWM_R{entry}__{stand}__{regime}"
    transition = {
        "transition_id": f"GWM_E{entry}__{stand}__{regime}",
        "from_state": f"GWM_E{entry}__{stand}__{regime}",
        "to_state": state_id,
        "stand": stand,
        "basis": "GWM_2007",
        "regime": regime,
        "entry": entry,
        "entry_age": age,
        "target_b_m2_ha": REGIMES[regime]["B"],
        "target_large_ba_m2_ha": REGIMES[regime]["large_ba"],
        "target_d_cm": REGIMES[regime]["D"],
        "target_q": REGIMES[regime]["q"],
        "pre_ba_m2_ha": float(row.BA),
        "pre_qmd_cm": float(row.QMD),
        "pre_tph": float(row.Tph),
        "pre_volume_m3_ha": float(row.TCuM),
        "post_ba_m2_ha": metrics["post_ba_m2_ha"],
        "post_qmd_cm": metrics["post_qmd_cm"],
        "post_tph": metrics["post_tph"],
        "post_q_factor": metrics["post_q_factor"],
        "post_max_dbh_cm": metrics["post_max_dbh_cm"],
        "post_canopy_ccf": float(row.ATCCF) if hasattr(row, "ATCCF") else float(row.CCF),
        "post_large_ba_m2_ha": metrics["post_large_ba_m2_ha"],
        "post_large_tph": metrics["post_large_tph"],
        "post_reserve_above_d_m2_ha": metrics["post_reserve_above_d_m2_ha"],
        "mean_large_crown_width_m": metrics["mean_large_crown_width_m"],
        "mean_large_crown_ratio": metrics["mean_large_crown_ratio"],
        "clump_count_per_ha": metrics["clump_count_per_ha"],
        "clump_crown_cover_fraction": metrics["clump_crown_cover_fraction"],
        "reserved_trees": metrics["reserved_trees"],
        "clump_harvested_trees": metrics["clump_harvested_trees"],
        "clump_removed_large_ba_m2_ha": metrics["clump_removed_large_ba_m2_ha"],
        "clump_removed_large_tph": metrics["clump_removed_large_tph"],
        "fvs_cut_tph": float(row.RTph) + metrics.get("clump_removed_large_tph", 0.0),
        "fvs_cut_m3_ha": float(row.RTCuM) + metrics.get("clump_removed_m3_ha", 0.0),
        "stand_structure_pass": metrics["stand_structure_pass"],
        "legal_compliance": False,
    }
    curves = []
    for point in summary[summary["Year"] <= 30].itertuples(index=False):
        curves.append(
            {
                "transition_id": transition["transition_id"],
                "stand": stand,
                "regime": regime,
                "entry": entry,
                "year": int(point.Year),
                "ba_m2_ha": float(point.BA),
                "qmd_cm": float(point.QMD),
                "tph": float(point.Tph),
                "volume_m3_ha": float(point.TCuM),
                "canopy_ccf": float(point.CCF),
            }
        )
    return transition, kept, curves


def _run_entry(
    population: list[dict[str, object]],
    *,
    chain_stand: str,
    regime: str,
    entry: int,
    age: float,
    runtime_dir: Path,
) -> tuple[object, dict[str, object], pd.DataFrame, list[dict[str, object]]]:
    """Run one entry and return its result, transition, residual list and curves."""
    try:
        result = _run_case(
            population,
            stand=chain_stand,
            age=age,
            regime=regime,
            runtime_dir=runtime_dir / f"E{entry}",
        )
        transition, kept, curve_rows = _extract_case(
            result, stand=chain_stand, regime=regime, entry=entry, age=age
        )
    except RuntimeError:
        result = _run_no_cut(
            population,
            stand=chain_stand,
            age=age,
            runtime_dir=runtime_dir / f"E{entry}_nocut",
        )
        transition, kept, curve_rows = _extract_no_cut(
            result, stand=chain_stand, regime=regime, entry=entry, age=age
        )
    return result, transition, kept, curve_rows


def main() -> None:
    """Build the v2 library with a configurable number of entries."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--stands", nargs="*", default=list(DEFAULT_STANDS))
    parser.add_argument("--entries", type=int, default=8)
    args = parser.parse_args()
    if args.entries < 2:
        raise ValueError("--entries must be at least 2")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.runtime_dir.mkdir(parents=True, exist_ok=True)
    sample = pd.read_csv(args.sample)
    transitions: list[dict[str, object]] = []
    curves: list[dict[str, object]] = []
    runs: list[dict[str, object]] = []
    state_rows: list[dict[str, object]] = []
    for stand in args.stands:
        frame = sample[sample["stand_id"] == stand].copy()
        if frame.empty:
            raise ValueError(f"stand {stand!r} is not in {args.sample}")
        initial_population = frame[["stand_id", "dbh_cm", "height_m", "crown_ratio"]].to_dict(
            "records"
        )
        age = (
            float(frame["source_age"].iloc[0])
            if "source_age" in frame
            else float(frame["tree_age"].iloc[0])
        )
        initial_ba = float((0.00007854 * frame["dbh_cm"] ** 2).sum())
        initial_qmd = float(np.sqrt(np.mean(frame["dbh_cm"] ** 2)))
        for regime in REGIMES:
            population = initial_population
            previous_state = f"GWM_E1__{stand}__{regime}"
            chain_stand = stand
            for entry in range(1, args.entries + 1):
                entry_age = age + 30.0 * (entry - 1)
                result, transition, kept, curve_rows = _run_entry(
                    population,
                    chain_stand=chain_stand,
                    regime=regime,
                    entry=entry,
                    age=entry_age,
                    runtime_dir=args.runtime_dir / f"{stand}__{regime}__E{entry}",
                )
                transition["from_state"] = previous_state
                transition["to_state"] = f"GWM_R{entry}__{stand}__{regime}"
                transition["transition_id"] = f"GWM_E{entry}__{stand}__{regime}"
                for row_curve in curve_rows:
                    row_curve["transition_id"] = transition["transition_id"]
                transitions.append(transition)
                curves.extend(curve_rows)
                runs.append(
                    {
                        "stand": chain_stand,
                        "regime": regime,
                        "entry": entry,
                        "case_id": result.provenance.case_id,
                    }
                )
                if entry == 1:
                    state_rows.append(
                        {
                            "state_id": transition["from_state"],
                            "state_kind": "initial",
                            "source_stand": stand,
                            "regime": regime,
                            "entry": 1,
                            "ba_m2_ha": initial_ba,
                            "qmd_cm": initial_qmd,
                            "tph": float(len(frame)),
                            "legal_compliance": False,
                        }
                    )
                state_rows.append(
                    {
                        "state_id": transition["to_state"],
                        "state_kind": "residual",
                        "source_stand": chain_stand,
                        "regime": regime,
                        "entry": entry,
                        "ba_m2_ha": transition["post_ba_m2_ha"],
                        "qmd_cm": transition["post_qmd_cm"],
                        "tph": transition["post_tph"],
                        "large_ba_m2_ha": transition["post_large_ba_m2_ha"],
                        "reserve_above_d_m2_ha": transition["post_reserve_above_d_m2_ha"],
                        "stand_structure_pass": transition["stand_structure_pass"],
                        "legal_compliance": False,
                    }
                )
                residual_population = _population_from_tree_list(
                    kept, f"{stand}_R{entry}", seed=RNG_SEED + len(runs)
                )
                if not residual_population:
                    break
                previous_state = transition["to_state"]
                chain_stand = f"{stand}_R{entry}"
                population = residual_population
    states_df = pd.DataFrame(state_rows).drop_duplicates("state_id").sort_values("state_id")
    transitions_df = pd.DataFrame(transitions)
    curves_df = pd.DataFrame(curves)
    states_df.to_csv(args.out_dir / "states.csv", index=False)
    transitions_df.to_csv(args.out_dir / "transitions.csv", index=False)
    curves_df.to_csv(args.out_dir / "curves.csv", index=False)
    benchmark = (
        transitions_df.groupby("regime")
        .agg(
            n=("transition_id", "size"),
            mean_post_ba=("post_ba_m2_ha", "mean"),
            mean_large_ba=("post_large_ba_m2_ha", "mean"),
            mean_reserve=("post_reserve_above_d_m2_ha", "mean"),
            mean_q=("post_q_factor", "mean"),
            mean_max_dbh=("post_max_dbh_cm", "mean"),
            mean_clump_removed_ba=("clump_removed_large_ba_m2_ha", "mean"),
            pass_n=("stand_structure_pass", "sum"),
        )
        .reset_index()
    )
    benchmark.to_csv(args.out_dir / "benchmark.csv", index=False)
    graph = {
        "nodes": states_df["state_id"].tolist(),
        "edges": [
            {
                "from": row.from_state,
                "to": row.to_state,
                "regime": row.regime,
                "entry": int(row.entry),
            }
            for row in transitions_df.itertuples(index=False)
        ],
    }
    (args.out_dir / "graph.json").write_text(json.dumps(graph, indent=2) + "\n")
    manifest = {
        "library": "knife-creek-state-transition-v3",
        "basis": "GWM_2007",
        "status": "provisional-clump-reserve",
        "generated_at": datetime.now(UTC).isoformat(),
        "source_stemlist": str(args.sample),
        "source_stemlist_sha256": hashlib.sha256(args.sample.read_bytes()).hexdigest(),
        "stands": list(args.stands),
        "regimes": REGIMES,
        "entries": args.entries,
        "counts": {
            "states": len(states_df),
            "transitions": len(transitions_df),
            "curves": len(curves_df),
        },
        "runs": runs,
        "caveats": [
            "PSP-derived regional IDF Cariboo analog, not Knife Creek data.",
            "GWM 2007 basis; not a legal-compliance product.",
            "Clump reserve uses a DBH-ranked six-tree proxy, not spatial clumps.",
            "Cut volume includes the post-FVS clump harvest; v2 counted only FVS RTCuM.",
            "Residual populations are weighted resamples of the FVS after-treatment list.",
            f"{args.entries} entries per chain; graph closure is empirical, not imposed.",
            "No KC calibration; FVS-BC is used structurally.",
            "The UWR/HMZ spatial layer is not tested.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"states={len(states_df)} transitions={len(transitions_df)} "
        f"curves={len(curves_df)} "
        f"pass={int(transitions_df['stand_structure_pass'].sum())}/{len(transitions_df)}"
    )


if __name__ == "__main__":
    main()
