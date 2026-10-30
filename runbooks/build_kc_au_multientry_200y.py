#!/usr/bin/env python3
"""Build multi-entry AU selection curves for KC.

Each matched FAIB plot gets repeated GWM entries at cycles 4, 7, 10, 13, 16 and
19 (nominally years 30 to 180), followed by residual growth to year 200. The
entry residual state is taken from the FVS summary (`ATBA`, `ATQMD`, `ATCCF`,
removed TPH and removed volume), not from the pre-cut stand.

Usage::

    python runbooks/build_kc_au_multientry_200y.py \
      --au-table data/kc_au/kc_au_table.csv \
      --matches data/psp/kc_au_200y/kc_au_plot_matches.csv \
      --panel data/psp/idf_cariboo_space_for_time_plots.csv \
      --raw-dir /path/to/faib/raw \
      --out-dir data/psp/kc_au_200y \
      --regime GWM_MODERATE
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

HORIZON_YEARS = 200
STEP_YEARS = 10
CYCLES = (4, 7, 10, 13, 16, 19)
ENTRY_YEARS = tuple((cycle - 1) * STEP_YEARS for cycle in CYCLES)
FT2_PER_M2 = 4.356
REGIMES = {
    "GWM_LOW": {"B": 16.0, "D": 50.0, "q": 1.30},
    "GWM_MODERATE": {"B": 22.0, "D": 60.0, "q": 1.25},
}
SPECIES_MAP = {"FDI": "FD", "PLI": "PL", "SX": "SW", "AT": "AT"}


def _bec_variant(row: pd.Series) -> str:
    """Return the BEC variant string for a FAIB plot."""
    variant = row["BEC_VAR"]
    if pd.isna(variant):
        variant_text = ""
    elif float(variant).is_integer():
        variant_text = str(int(variant))
    else:
        variant_text = str(variant)
    return f"IDF{row['BEC_SBZ']}{variant_text}"


def _records(state: pd.Series, trees: pd.DataFrame) -> list[dict[str, object]]:
    """Build FVS tree records from one FAIB plot state."""
    selected = trees[
        (trees["CLSTR_ID"] == state["CLSTR_ID"]) & (trees["VISIT_NUMBER"] == state["VISIT_NUMBER"])
    ].copy()
    records = []
    for number, row in enumerate(selected.itertuples(index=False), start=1):
        species = str(row.SPECIES).strip().upper()
        species = SPECIES_MAP.get(species, species)
        try:
            species = resolve_species(species)
        except Exception:
            species = "OH"
        crown = {"C": 0.65, "I": 0.55, "S": 0.45, "D": 0.30}.get(
            str(row.CR_CL).strip().upper(), 0.45
        )
        height = float(row.HEIGHT) if np.isfinite(row.HEIGHT) else 1.3 + 0.5 * float(row.DBH)
        records.append(
            {
                "plot_id": 1,
                "tree_num": number,
                "tree_count": float(row.PHF_TREE),
                "tree_history": 0,
                "species": species,
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


def _keywords(site_index: float, regime: str) -> list[Keyword]:
    """Return the 200-year multi-entry key set."""
    spec = REGIMES[regime]
    thinning = [
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
        for cycle in CYCLES
    ]
    return [
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary")),
        Keyword("STDIDENT", (f"KC-AU-{regime}-MULTI-200Y",)),
        Keyword("STDINFO", ("712", "CHS131", "0", str(HORIZON_YEARS), "35", "16")),
        Keyword("MANAGED", ("0", "1")),
        Keyword("SITECODE", ("FD", f"{site_index:.1f}")),
        Keyword("INVYEAR", ("0",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", str(STEP_YEARS))),
        Keyword("NUMCYCLE", (str(HORIZON_YEARS // STEP_YEARS),)),
        Keyword("RANNSEED", ("1",)),
        *thinning,
        Keyword("PROCESS"),
        Keyword("STOP"),
    ]


def main() -> None:
    """Run the AU multi-entry curves."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--au-table", type=Path, required=True)
    parser.add_argument("--matches", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--regime", choices=sorted(REGIMES), default="GWM_MODERATE")
    args = parser.parse_args()

    au = pd.read_csv(args.au_table).set_index("au_id")
    matches = pd.read_csv(args.matches)
    panel = pd.read_csv(args.panel)
    panel["bec"] = panel.apply(_bec_variant, axis=1)
    panel = panel.set_index(["CLSTR_ID", "VISIT_NUMBER"])
    trees = pd.read_csv(
        args.raw_dir / "faib_tree_detail.csv",
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
    trees = trees[
        (trees["LV_D"] == "L")
        & (trees["CLSTR_ID"].isin(set(matches["CLSTR_ID"])))
        & trees["DBH"].notna()
        & trees["PHF_TREE"].notna()
    ].copy()

    run_root = args.out_dir / f"multi_{args.regime.lower()}_runs"
    if run_root.exists():
        shutil.rmtree(run_root)
    run_root.mkdir(parents=True)
    rows: list[dict[str, object]] = []
    for au_id, group in matches.groupby("au_id"):
        au_row = au.loc[au_id]
        cases = []
        for match in group.itertuples(index=False):
            key = (match.CLSTR_ID, int(match.VISIT_NUMBER))
            if key not in panel.index:
                continue
            state = panel.loc[key]
            if isinstance(state, pd.DataFrame):
                state = state.iloc[0]
            state = state.copy()
            state["CLSTR_ID"] = key[0]
            state["VISIT_NUMBER"] = key[1]
            records = _records(state, trees)
            if not records:
                continue
            result = run_case(
                records,
                _keywords(float(au_row.site_index_median), args.regime),
                directory=run_root / f"{au_id}__{match.CLSTR_ID}",
            )
            summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
            summary = summary[summary["CaseID"] == result.provenance.case_id]
            stage_rows: list[dict[str, object]] = []
            for stage, (_cycle, entry_year) in enumerate(
                zip(CYCLES, ENTRY_YEARS, strict=True), start=1
            ):
                entry = summary[summary["Year"] == entry_year]
                if entry.empty:
                    continue
                entry = entry.iloc[0]
                cut_tph = float(entry["RTph"])
                cut_volume = float(entry["RTCuM"])
                stage_rows.append(
                    {
                        "stage": stage,
                        "year": 0,
                        "ba_m2_ha": float(entry["ATBA"]),
                        "tph": float(entry["Tph"]) - cut_tph,
                        "qmd_cm": float(entry["ATQMD"]),
                        "volume_m3_ha": float(entry["TCuM"]) - cut_volume,
                        "canopy_ccf": float(entry["ATCCF"]),
                        "cut_tph": cut_tph,
                        "cut_m3_ha": cut_volume,
                    }
                )
                next_year = ENTRY_YEARS[stage] if stage < len(ENTRY_YEARS) else HORIZON_YEARS
                post = summary[(summary["Year"] > entry_year) & (summary["Year"] <= next_year)]
                for point in post.itertuples(index=False):
                    stage_rows.append(
                        {
                            "stage": stage,
                            "year": int(point.Year - entry_year),
                            "ba_m2_ha": float(point.BA),
                            "tph": float(point.Tph),
                            "qmd_cm": float(point.QMD),
                            "volume_m3_ha": float(point.TCuM),
                            "canopy_ccf": float(point.CCF),
                            "cut_tph": 0.0,
                            "cut_m3_ha": 0.0,
                        }
                    )
            if stage_rows:
                cases.append(pd.DataFrame(stage_rows))
        if not cases:
            raise ValueError(f"no multi-entry FVS cases completed for {au_id}")
        stacked = pd.concat(cases, ignore_index=True)
        mean = stacked.groupby(["stage", "year"], as_index=False).mean(numeric_only=True)
        mean.insert(0, "au_id", au_id)
        mean.insert(1, "si_level", au_row.si_level)
        mean.insert(2, "n_plots", len(cases))
        rows.extend(mean.to_dict(orient="records"))

    curves = pd.DataFrame(rows)
    suffix = (
        "moderate" if args.regime == "GWM_MODERATE" else args.regime.lower().removeprefix("gwm_")
    )
    curves.to_csv(args.out_dir / f"kc_au_multientry_{suffix}_200y.csv", index=False)
    manifest = {
        "au_table": str(args.au_table),
        "matches": str(args.matches),
        "regime": args.regime,
        "horizon_years": HORIZON_YEARS,
        "entries": list(zip(CYCLES, ENTRY_YEARS, strict=True)),
        "aus": int(curves["au_id"].nunique()),
        "curve_rows": len(curves),
        "caveats": [
            "Six entries, then residual growth to 200 years.",
            "Residual x=0 uses ATBA, ATQMD, ATCCF and pre-cut minus removed TPH/volume.",
            "No calibration or legal-compliance claim.",
        ],
    }
    (args.out_dir / f"multientry_{suffix}_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
