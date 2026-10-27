#!/usr/bin/env python3
"""Build the Knife Creek state-transition library v0 from PSP-derived stands.

The v0 library is a structural pilot, not a compiled ws4 dataset and not a
calibrated KC growth model. It runs selected public PSP-derived stands through
two 30-year cycles of each Table 29 selection regime and records the pre-cut
state, cut, residual state, and interval curves.

Usage::

    PYTHONPATH=/path/to/fresh-fvsbc/src \
      /path/to/fvsbc-build-venv/bin/python runbooks/build_state_library.py \
      --sample data/psp/idf_cariboo_psp_stemlist_sample.csv \
      --out-dir ws4/state_library_v0 \
      --runtime-dir runtime/state_library_v0
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
    "SEL_MDWR_HIGH": {"target_ft2_ac": "126.32", "max_dbh_cm": "60.0", "q": "1.25"},
    "SEL_MDWR_MODERATE": {"target_ft2_ac": "95.83", "max_dbh_cm": "55.0", "q": "1.25"},
    "SEL_MDWR_LOW": {"target_ft2_ac": "69.70", "max_dbh_cm": "50.0", "q": "1.30"},
}


def _ba_class(ba: float) -> str:
    """Return the canonical basal-area class label."""
    if ba < 20:
        return "BA_LT20"
    if ba < 25:
        return "BA20_25"
    if ba < 30:
        return "BA25_30"
    if ba < 35:
        return "BA30_35"
    if ba < 40:
        return "BA35_40"
    return "BA40_PLUS"


def _qmd_class(qmd: float) -> str:
    """Return the canonical QMD class label."""
    if qmd < 18:
        return "QMD_LT18"
    if qmd < 20:
        return "QMD18_20"
    if qmd < 22:
        return "QMD20_22"
    if qmd < 24:
        return "QMD22_24"
    return "QMD24_PLUS"


def _state_key(prefix: str, ba: float, qmd: float, origin: str) -> str:
    """Return a compact state key from BA/QMD classes."""
    return f"PSP_IDF__FD__{_ba_class(ba)}__{_qmd_class(qmd)}__{origin}"


def _regime_keywords(regime: str, first_cycle: int, second_cycle: int) -> list[Keyword]:
    """Return two THINQFA records for the same regime."""
    spec = REGIMES[regime]
    rows = []
    for cycle in (first_cycle, second_cycle):
        rows.append(
            Keyword(
                "THINQFA",
                (
                    str(cycle),
                    "0.0",
                    spec["max_dbh_cm"],
                    "0",
                    spec["q"],
                    "5.0",
                    spec["target_ft2_ac"],
                ),
                supplemental=("0",),
            )
        )
    return rows


def _run_one(
    population: list[dict[str, object]],
    *,
    stand_id: str,
    age: float,
    regime: str,
    runtime_dir: Path,
) -> object:
    """Run one two-cycle FVS-BC case and return the result."""
    keywords = [
        Keyword(
            "DATABASE",
            (),
            ("DSNOut", "FVSOut.db", "TreeLIDB", "CutLIDB", "ATRTLIDB", "Summary"),
        ),
        Keyword("STDIDENT", (f"STATE {stand_id} {regime}",)),
        Keyword("STDINFO", ("712", "CHS131", "0", "200", "35", "16")),
        Keyword("MANAGED", ("0", "1")),
        Keyword("SITECODE", ("FD", "60")),
        Keyword("INVYEAR", ("0",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", "10")),
        Keyword("NUMCYCLE", ("10",)),
        Keyword("RANNSEED", ("1",)),
        Keyword("TREELIST", ("4",)),
        Keyword("TREELIST", ("7",)),
        Keyword("CUTLIST", ("4",)),
        Keyword("CUTLIST", ("7",)),
        Keyword("ATRTLIST", ("4",)),
        Keyword("ATRTLIST", ("7",)),
        *_regime_keywords(regime, 4, 7),
        Keyword("PROCESS"),
        Keyword("STOP"),
    ]
    return run_population(
        population,
        directory=runtime_dir / f"{stand_id}__{regime}",
        species="FD",
        tree_age=age,
        keywords=keywords,
    )


def _post_species(atrt: pd.DataFrame, year: int) -> tuple[str, float, float, float, float]:
    """Return leading species, large-tree BA, total BA, max DBH and q from ATRT."""
    rows = atrt[atrt["Year"] == year].copy()
    if rows.empty:
        return "FD", 0.0, 0.0, 0.0, float("nan")
    rows["ba"] = 0.00007854 * rows["DBH"] ** 2 * rows["TPH"]
    by_species = rows.groupby("SpeciesFVS")["ba"].sum().sort_values(ascending=False)
    leading = str(by_species.index[0]) if len(by_species) else "FD"
    large = float(rows.loc[rows["DBH"] >= 37.5, "ba"].sum())
    classes = (rows["DBH"] // 5 * 5 + 2.5).astype(float)
    density = rows.assign(dbh_class=classes).groupby("dbh_class")["TPH"].sum()
    all_classes = np.arange(classes.min(), classes.max() + 5.0, 5.0)
    density = density.reindex(all_classes, fill_value=0.0)
    ratios = []
    for lower, upper in itertools.pairwise(all_classes):
        if density.loc[lower] > 0 and density.loc[upper] > 0:
            ratios.append(float(density.loc[lower] / density.loc[upper]))
    q_factor = float(np.median(ratios)) if ratios else float("nan")
    return leading, large, float(rows["ba"].sum()), float(rows["DBH"].max()), q_factor


def _summary_records(
    result: object,
    *,
    source_state: str,
    regime: str,
    stand: str,
    age: float,
) -> tuple[
    list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], dict[str, object]
]:
    """Extract curves, transitions and residual-state rows from one run."""
    database = result.database
    summary = read_table(database, "FVS_Summary_Metric").sort_values("Year")
    try:
        atrt = read_table(database, "FVS_ATRTList_Metric")
    except UnknownTableError:
        atrt = pd.DataFrame(columns=["Year", "SpeciesFVS", "DBH", "TPH"])
    curves: list[dict[str, object]] = []
    transitions: list[dict[str, object]] = []
    residual_rows: list[dict[str, object]] = []
    initial_ba = float(summary.loc[summary["Year"] == 0, "BA"].iloc[0])
    initial_qmd = float(summary.loc[summary["Year"] == 0, "QMD"].iloc[0])
    initial_tph = float(summary.loc[summary["Year"] == 0, "Tph"].iloc[0])
    for entry_year in (30, 60):
        window = summary[(summary["Year"] >= entry_year) & (summary["Year"] <= entry_year + 30)]
        for row in window.itertuples(index=False):
            at_entry = int(row.Year) == entry_year
            curves.append(
                {
                    "curve_id": f"{source_state}__{regime}__entry{entry_year}",
                    "state_id": source_state,
                    "regime": regime,
                    "entry_year": entry_year,
                    "years_since_entry": int(row.Year - entry_year),
                    "ba_m2_ha": float(row.ATBA if at_entry else row.BA),
                    "qmd_cm": float(row.ATQMD if at_entry else row.QMD),
                    "tph": float(max(0.0, row.Tph - row.RTph) if at_entry else row.Tph),
                    "volume_m3_ha": float(max(0.0, row.TCuM - row.RTCuM) if at_entry else row.TCuM),
                    "canopy_ccf": float(row.ATCCF if at_entry else row.CCF),
                }
            )
        row = summary.loc[summary["Year"] == entry_year].iloc[0]
        leading, large_ba, total_ba, max_dbh, q_factor = _post_species(atrt, entry_year)
        post_ba = float(row.ATBA)
        post_qmd = float(row.ATQMD)
        post_tph = max(0.0, float(row.Tph) - float(row.RTph))
        residual = _state_key("", post_ba, post_qmd, "selection")
        transition = {
            "transition_id": f"{source_state}__{regime}__entry{entry_year}",
            "from_state": source_state,
            "regime": regime,
            "entry_year": entry_year,
            "pre_ba_m2_ha": float(row.BA),
            "pre_qmd_cm": float(row.QMD),
            "pre_tph": float(row.Tph),
            "pre_volume_m3_ha": float(row.TCuM),
            "post_ba_m2_ha": post_ba,
            "post_qmd_cm": post_qmd,
            "post_tph": post_tph,
            "post_leading_species": leading,
            "post_large_tree_ba_m2_ha": large_ba,
            "post_total_ba_check": total_ba,
            "post_max_dbh_cm": max_dbh,
            "post_q_factor": q_factor,
            "post_canopy_ccf": float(row.ATCCF) if hasattr(row, "ATCCF") else float(row.CCF),
            "cut_tph": float(row.RTph),
            "cut_m3_ha": float(row.RTCuM),
            "residual_state": residual,
            "run_id": f"{stand}__{regime}",
        }
        transitions.append(transition)
        residual_rows.append(
            {
                "state_id": residual,
                "state_kind": "residual",
                "source_stand": stand,
                "ba_m2_ha": post_ba,
                "qmd_cm": post_qmd,
                "tph": post_tph,
                "age_years": age + entry_year,
                "leading_species": leading,
                "species_group": "FD",
                "canonical": True,
                "ba_min": post_ba,
                "ba_max": post_ba,
                "qmd_min": post_qmd,
                "qmd_max": post_qmd,
                "n_transitions": 1,
                "notes": f"from {source_state} / {regime} at year {entry_year}",
            }
        )
    return (
        curves,
        transitions,
        residual_rows,
        {
            "initial_ba_m2_ha": initial_ba,
            "initial_qmd_cm": initial_qmd,
            "initial_tph": initial_tph,
        },
    )


def main() -> None:
    """Run the selected stands, regimes and write the library."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--stands", nargs="*", default=list(DEFAULT_STANDS))
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.runtime_dir.mkdir(parents=True, exist_ok=True)
    sample = pd.read_csv(args.sample)
    all_curves: list[dict[str, object]] = []
    all_transitions: list[dict[str, object]] = []
    all_residual: list[dict[str, object]] = []
    initial_states: list[dict[str, object]] = []
    runs: list[dict[str, object]] = []
    for stand in args.stands:
        frame = sample[sample["stand_id"] == stand].copy()
        if frame.empty:
            raise ValueError(f"stand {stand!r} is not in {args.sample}")
        population = frame[["stand_id", "dbh_cm", "height_m", "crown_ratio"]].to_dict("records")
        age = float(frame["source_age"].iloc[0])
        initial_ba = float(np.sum(0.00007854 * frame["dbh_cm"] ** 2))
        initial_qmd = float(np.sqrt(np.mean(frame["dbh_cm"] ** 2)))
        initial_tph = float(len(frame))
        source_state = (
            f"PSP_IDF_{stand.split('-')[-1]}__FD__{_ba_class(initial_ba)}__"
            f"{_qmd_class(initial_qmd)}__natural"
        )
        initial_states.append(
            {
                "state_id": source_state,
                "state_kind": "initial",
                "source_stand": stand,
                "ba_m2_ha": initial_ba,
                "qmd_cm": initial_qmd,
                "tph": initial_tph,
                "age_years": age,
                "leading_species": "FD",
                "species_group": "FD",
                "canonical": False,
                "ba_min": initial_ba,
                "ba_max": initial_ba,
                "qmd_min": initial_qmd,
                "qmd_max": initial_qmd,
                "n_transitions": len(REGIMES) * 2,
                "notes": "PSP-derived synthetic IDF stand",
            }
        )
        for regime in REGIMES:
            result = _run_one(
                population,
                stand_id=stand,
                age=age,
                regime=regime,
                runtime_dir=args.runtime_dir,
            )
            curves, transitions, residual_rows, initial = _summary_records(
                result,
                source_state=source_state,
                regime=regime,
                stand=stand,
                age=age,
            )
            all_curves.extend(curves)
            all_transitions.extend(transitions)
            all_residual.extend(residual_rows)
            runs.append(
                {
                    "stand": stand,
                    "regime": regime,
                    "run_id": f"{stand}__{regime}",
                    "run_dir": str(Path(result.directory).relative_to(Path.cwd())),
                    "case_id": result.provenance.case_id,
                    "keyword_hash": result.provenance.keyword_set_hash,
                    "treelist_hash": result.provenance.treelist_hash,
                    "initial_ba_m2_ha": initial["initial_ba_m2_ha"],
                    "initial_qmd_cm": initial["initial_qmd_cm"],
                    "initial_tph": initial["initial_tph"],
                }
            )
    curves_df = pd.DataFrame(all_curves).sort_values(
        ["state_id", "regime", "entry_year", "years_since_entry"]
    )
    transitions_df = pd.DataFrame(all_transitions).sort_values(
        ["from_state", "regime", "entry_year"]
    )
    residual_raw = pd.DataFrame(all_residual)
    residual_df = (
        residual_raw.groupby("state_id", as_index=False)
        .agg(
            state_kind=("state_kind", "first"),
            source_stand=("source_stand", lambda values: ", ".join(sorted(set(values)))),
            ba_m2_ha=("ba_m2_ha", "mean"),
            qmd_cm=("qmd_cm", "mean"),
            tph=("tph", "mean"),
            age_years=("age_years", "mean"),
            leading_species=("leading_species", "first"),
            species_group=("species_group", "first"),
            canonical=("canonical", "first"),
            ba_min=("ba_m2_ha", "min"),
            ba_max=("ba_m2_ha", "max"),
            qmd_min=("qmd_cm", "min"),
            qmd_max=("qmd_cm", "max"),
            n_transitions=("state_id", "size"),
            notes=("notes", lambda values: "; ".join(values)),
        )
        .sort_values("state_id")
    )
    states_df = pd.concat([pd.DataFrame(initial_states), residual_df], ignore_index=True)
    states_df.to_csv(args.out_dir / "states.csv", index=False)
    transitions_df.to_csv(args.out_dir / "transitions.csv", index=False)
    curves_df.to_csv(args.out_dir / "curves.csv", index=False)
    target_ba = {"SEL_MDWR_HIGH": 29.0, "SEL_MDWR_MODERATE": 22.0, "SEL_MDWR_LOW": 16.0}
    target_q = {"SEL_MDWR_HIGH": 1.25, "SEL_MDWR_MODERATE": 1.25, "SEL_MDWR_LOW": 1.30}
    target_d = {"SEL_MDWR_HIGH": 60.0, "SEL_MDWR_MODERATE": 55.0, "SEL_MDWR_LOW": 50.0}
    benchmark_rows = []
    for regime, group in transitions_df.groupby("regime"):
        benchmark_rows.append(
            {
                "regime": regime,
                "n": len(group),
                "target_post_ba_m2_ha": target_ba[regime],
                "mean_post_ba_m2_ha": float(group["post_ba_m2_ha"].mean()),
                "mean_abs_ba_error_m2_ha": float(
                    (group["post_ba_m2_ha"] - target_ba[regime]).abs().mean()
                ),
                "within_2_m2_ha": int(
                    ((group["post_ba_m2_ha"] - target_ba[regime]).abs() <= 2.0).sum()
                ),
                "target_q": target_q[regime],
                "mean_post_q": float(group["post_q_factor"].mean()),
                "target_max_dbh_cm": target_d[regime],
                "mean_post_max_dbh_cm": float(group["post_max_dbh_cm"].mean()),
                "mean_cut_m3_ha": float(group["cut_m3_ha"].mean()),
                "mean_cut_tph": float(group["cut_tph"].mean()),
            }
        )
    benchmark_df = pd.DataFrame(benchmark_rows)
    benchmark_df.to_csv(args.out_dir / "benchmark.csv", index=False)
    (args.out_dir / "benchmark.json").write_text(json.dumps(benchmark_rows, indent=2) + "\n")
    graph = {
        "nodes": states_df["state_id"].tolist(),
        "edges": [
            {
                "from": row.from_state,
                "to": row.residual_state,
                "regime": row.regime,
                "entry_year": int(row.entry_year),
            }
            for row in transitions_df.itertuples(index=False)
        ],
    }
    (args.out_dir / "graph.json").write_text(json.dumps(graph, indent=2) + "\n")
    manifest = {
        "library": "knife-creek-state-transition-v0",
        "status": "provisional-one-entry-per-regime",
        "generated_at": datetime.now(UTC).isoformat(),
        "source_stemlist": str(args.sample),
        "source_stemlist_sha256": hashlib.sha256(args.sample.read_bytes()).hexdigest(),
        "stands": list(args.stands),
        "regimes": REGIMES,
        "counts": {
            "states": len(states_df),
            "initial_states": len(initial_states),
            "residual_states": len(residual_df),
            "transitions": len(transitions_df),
            "curves": len(curves_df),
        },
        "runs": runs,
        "caveats": [
            "PSP-derived regional IDF Cariboo analog, not Knife Creek data.",
            "Not a compiled ws4 dataset; fragments, blocks and topology are not built.",
            "Two entries per run; residual states are terminal in v0.",
            "No KC calibration; FVS-BC is used structurally.",
            "Residual BA may exceed the Table 29 target because of q deficits in the grown stand.",
            "Habitat assignment is structural, not the legal UWR order.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"states={len(states_df)} initial={len(initial_states)} residual={len(residual_df)} "
        f"transitions={len(transitions_df)} curves={len(curves_df)}"
    )


if __name__ == "__main__":
    main()
