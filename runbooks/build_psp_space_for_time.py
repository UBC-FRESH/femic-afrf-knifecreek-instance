#!/usr/bin/env python3
"""Build a public FAIB space-for-time PSP panel and 50-year FVS-BC curves.

The panel uses all live-tree IDF PSP visits in the Williams Lake and 100 Mile
House TSAs, not only first measurements. Each selected visit is a stand state;
this is a space-for-time design, not a growth chronology.

The 50-year curves are no-cut FVS-BC runs. They span a selection rotation, not
300 years.

Usage::

    PYTHONPATH=/path/to/fresh-fvsbc/src \
      python runbooks/build_psp_space_for_time.py \
      --raw-dir /path/to/faib_psp_csvs \
      --out-dir data/psp \
      --runtime-dir runtime/psp_space_for_time \
      --max-states 120
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.nemora import crown_class
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import resolve_species

LOWER_CM = 9.1
CROWN_RATIO = {"C": 0.65, "I": 0.55, "S": 0.45, "D": 0.30}
SPECIES_MAP = {
    "SX": "SE",
    "SS": "SE",
    "W": "OH",
    "FD": "FD",
    "PL": "PL",
    "EP": "EP",
    "AT": "AT",
    "AC": "AC",
    "CW": "CW",
    "HW": "HW",
    "PY": "PY",
    "BL": "BL",
    "BG": "BG",
    "PW": "PW",
    "LW": "LW",
    "OC": "OC",
    "OH": "OH",
}


def _summary(
    raw_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Select live-tree IDF visits and compute plot states."""
    header = pd.read_csv(raw_dir / "faib_header.csv", low_memory=False)
    visits = pd.read_csv(raw_dir / "faib_sample_byvisit.csv", low_memory=False)
    idf = header[
        (header["BEC_ZONE"] == "IDF")
        & header["TSA_DESC"].isin(["Williams Lake TSA", "100 Mile House TSA"])
    ][["SITE_IDENTIFIER", "TSA_DESC", "BEC_SBZ", "BEC_VAR"]]
    visits = visits.merge(idf, on="SITE_IDENTIFIER", how="inner")
    trees = pd.read_csv(
        raw_dir / "faib_tree_detail.csv",
        usecols=[
            "CLSTR_ID",
            "VISIT_NUMBER",
            "SPECIES",
            "DBH",
            "HEIGHT",
            "LV_D",
            "CR_CL",
            "PHF_TREE",
        ],
        low_memory=False,
    )
    trees = trees[trees["CLSTR_ID"].isin(set(visits["CLSTR_ID"]))].copy()
    for column in ("DBH", "PHF_TREE", "HEIGHT"):
        trees[column] = pd.to_numeric(trees[column], errors="coerce")
    trees = trees[
        (trees["LV_D"] == "L")
        & trees["DBH"].notna()
        & (trees["DBH"] >= LOWER_CM)
        & trees["PHF_TREE"].notna()
        & (trees["PHF_TREE"] > 0)
    ].copy()
    trees["ba"] = 0.00007854 * trees["DBH"] ** 2 * trees["PHF_TREE"]
    states = (
        trees.groupby(["CLSTR_ID", "VISIT_NUMBER"])
        .agg(
            tph=("PHF_TREE", "sum"),
            ba=("ba", "sum"),
            qmd=("DBH", lambda x: float(np.sqrt(np.sum(x**2) / len(x)))),
            n=("DBH", "size"),
        )
        .reset_index()
        .merge(
            visits[
                [
                    "CLSTR_ID",
                    "VISIT_NUMBER",
                    "MEAS_YR",
                    "PROJ_AGE_1",
                    "TSA_DESC",
                    "BEC_SBZ",
                    "BEC_VAR",
                ]
            ],
            on=["CLSTR_ID", "VISIT_NUMBER"],
            how="left",
        )
    )
    states = states[
        states["ba"].between(5.0, 60.0)
        & states["qmd"].between(5.0, 50.0)
        & states["tph"].between(100.0, 5000.0)
        & states["PROJ_AGE_1"].between(20.0, 250.0)
    ].copy()
    states["age_bin"] = pd.cut(
        states["PROJ_AGE_1"], [0, 40, 60, 80, 100, 120, 150, 200, 250]
    ).astype(str)
    states["ba_bin"] = pd.cut(states["ba"], [0, 15, 25, 35, 45, 60]).astype(str)
    return states, visits, trees


def _sample(states: pd.DataFrame, max_states: int, seed: int) -> pd.DataFrame:
    """Stratify by age and BA and cap the number of FVS runs."""
    rng = np.random.default_rng(seed)
    pieces = []
    for _, group in states.groupby(["age_bin", "ba_bin"], observed=True):
        take = min(3, len(group))
        pieces.append(group.sample(n=take, random_state=rng))
    sample = pd.concat(pieces, ignore_index=True)
    if len(sample) > max_states:
        sample = sample.sample(n=max_states, random_state=seed).reset_index(drop=True)
    return sample


def _records(
    state: pd.Series,
    trees: pd.DataFrame,
) -> list[dict[str, object]]:
    """Build per-tree FVS records from one FAIB visit."""
    selected = trees[
        (trees["CLSTR_ID"] == state["CLSTR_ID"]) & (trees["VISIT_NUMBER"] == state["VISIT_NUMBER"])
    ].copy()
    records = []
    for number, row in enumerate(selected.itertuples(index=False), start=1):
        species = str(row.SPECIES).strip().upper()
        species = SPECIES_MAP.get(species, species)
        try:
            resolved = resolve_species(species)
        except Exception:
            resolved = "OH"
        height = float(row.HEIGHT) if np.isfinite(row.HEIGHT) else 1.3 + 0.5 * float(row.DBH)
        crown = CROWN_RATIO.get(str(row.CR_CL).strip().upper(), 0.45)
        records.append(
            {
                "plot_id": 1,
                "tree_num": number,
                "tree_count": float(row.PHF_TREE),
                "tree_history": 0,
                "species": resolved,
                "diam": float(row.DBH),
                "dg_incr": 0.0,
                "live_ht": height,
                "trunc_ht": 0.0,
                "htg_incr": 0.0,
                "crown_ratio": crown_class(crown),
                "damage1": 0,
                "severity1": 0,
                "damage2": 0,
                "severity2": 0,
                "damage3": 0,
                "severity3": 0,
                "tree_val": 0,
                "tree_rx": 0,
                "plot_slope": 0,
                "plot_aspect": 0,
                "plot_habitat": 0,
                "plot_topo_pos": 0,
                "plot_site_prep": 0,
                "tree_age": float(state["PROJ_AGE_1"]),
            }
        )
    return records


def _keywords(age: float) -> list[Keyword]:
    """Create a no-cut 50-year FVS-BC key set."""
    return [
        Keyword(
            "DATABASE",
            (),
            ("DSNOut", "FVSOut.db", "TreeLIDB", "CutLIDB", "ATRTLIDB", "Summary"),
        ),
        Keyword("STDIDENT", ("FAIB PSP SPACE FOR TIME",)),
        Keyword("STDINFO", ("712", "CHS131", str(round(age)), "0", "0", "0")),
        Keyword("MANAGED", ("0", "1")),
        Keyword("INVYEAR", ("0",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", "10")),
        Keyword("NUMCYCLE", ("5",)),
        Keyword("RANNSEED", ("1",)),
        Keyword("TREELIST", ("5",)),
        Keyword("PROCESS"),
        Keyword("STOP"),
    ]


def main() -> None:
    """Build the panel and run the FVS curves."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--max-states", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20261030)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.runtime_dir.mkdir(parents=True, exist_ok=True)
    states, _visits, trees = _summary(args.raw_dir)
    sample = _sample(states, args.max_states, args.seed)
    sample.to_csv(args.out_dir / "idf_cariboo_space_for_time_plots.csv", index=False)
    curves = []
    runs = []
    for index, state in sample.iterrows():
        state_id = f"FAIB-{state['CLSTR_ID']}-V{int(state['VISIT_NUMBER'])}"
        case_dir = args.runtime_dir / f"case_{index:03d}"
        if case_dir.exists():
            shutil.rmtree(case_dir)
        records = _records(state, trees)
        if not records:
            continue
        result = run_case(records, _keywords(float(state["PROJ_AGE_1"])), directory=case_dir)
        summary = read_table(result.database, "FVS_Summary_Metric")
        summary = summary[summary["CaseID"] == result.provenance.case_id].sort_values("Year")
        for row in summary.itertuples(index=False):
            curves.append(
                {
                    "state_id": state_id,
                    "clstr_id": state["CLSTR_ID"],
                    "visit_number": int(state["VISIT_NUMBER"]),
                    "meas_year": int(state["MEAS_YR"]),
                    "age": float(state["PROJ_AGE_1"]),
                    "ba_start_m2_ha": float(state["ba"]),
                    "tph_start": float(state["tph"]),
                    "qmd_start_cm": float(state["qmd"]),
                    "year": int(row.Year),
                    "ba_m2_ha": float(row.BA),
                    "tph": float(row.Tph),
                    "qmd_cm": float(row.QMD),
                    "volume_m3_ha": float(row.TCuM),
                    "canopy_ccf": float(row.CCF),
                }
            )
        runs.append({"state_id": state_id, "case_id": result.provenance.case_id})
    pd.DataFrame(curves).to_csv(args.out_dir / "idf_cariboo_space_for_time_curves.csv", index=False)
    manifest = {
        "panel": "faib-idf-cariboo-space-for-time-v1",
        "raw_states": len(states),
        "sampled_states": len(sample),
        "fvs_runs": len(runs),
        "horizon_years": 50,
        "step_years": 10,
        "tsas": ["Williams Lake TSA", "100 Mile House TSA"],
        "selection": (
            "live trees >= 9.1 cm DBH; BA 5-60; QMD 5-50; TPH 100-5000; projected age 20-250"
        ),
        "design": "space-for-time: each visit is a state; not a growth chronology",
        "caveats": [
            "Projected age is used as a stand-age prior, not a measured age.",
            "Visits are repeated measurements of the same plots; they are not independent plots.",
            "The 50-year curves are no-cut FVS-BC runs, not observed 50-year growth.",
            "FVS-BC site index is not used; no KC calibration is claimed.",
        ],
        "runs": runs,
    }
    (args.out_dir / "idf_cariboo_space_for_time_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
    print(f"states={len(states)} sampled={len(sample)} curves={len(curves)} runs={len(runs)}")


if __name__ == "__main__":
    main()
