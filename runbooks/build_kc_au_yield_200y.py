#!/usr/bin/env python3
"""Build AU-level 200-year FVS-BC yield curves for KC.

The AU table follows the FEMIC stage-01a pattern: BEC + leading species,
then L/M/H SI quantile classes. This script matches each AU to public FAIB PSP
plots in the same BEC and leading species, preferentially within the AU's SI
band, and runs a 200-year no-cut FVS-BC case for each selected plot.

Usage::

    python runbooks/build_kc_au_yield_200y.py \
      --au-table data/kc_au/kc_au_table.csv \
      --panel data/psp/idf_cariboo_space_for_time_plots.csv \
      --raw-dir /path/to/faib/raw \
      --out-dir data/psp/kc_au_200y \
      --plots-per-au 5
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

TREE_AGE_DEFAULT = 60.0
HORIZON_YEARS = 200
STEP_YEARS = 10
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


def _keywords() -> list[Keyword]:
    """Return the no-cut 200-year FVS-BC key set."""
    return [
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary", "TREELIDB")),
        Keyword("STDIDENT", ("KC-AU-200Y",)),
        Keyword("STDINFO", ("712", "CHS131", "0", str(HORIZON_YEARS), "35", "16")),
        Keyword("MANAGED", ("0", "1")),
        Keyword("SITECODE", ("FD", "60")),
        Keyword("INVYEAR", ("0",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", str(STEP_YEARS))),
        Keyword("NUMCYCLE", (str(HORIZON_YEARS // STEP_YEARS),)),
        Keyword("RANNSEED", ("1",)),
        *[Keyword("TREELIST", (str(cycle),)) for cycle in range(1, 21)],
        Keyword("PROCESS"),
        Keyword("STOP"),
    ]


def main() -> None:
    """Match FAIB plots to AUs and write AU-level 200-year curves."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--au-table", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--plots-per-au", type=int, default=5)
    args = parser.parse_args()

    au = pd.read_csv(args.au_table)
    panel = pd.read_csv(args.panel)
    panel["bec"] = panel.apply(_bec_variant, axis=1)
    panel["species"] = (
        panel["leading_species"]
        .astype(str)
        .str.upper()
        .map(lambda value: SPECIES_MAP.get(value, value))
    )
    siteage = pd.read_csv(args.raw_dir / "faib_compiled_spcsmries_siteage.csv", low_memory=False)
    siteage["si"] = siteage[["SI1", "SI2", "SI3"]].bfill(axis=1).iloc[:, 0]
    siteage = siteage[["CLSTR_ID", "VISIT_NUMBER", "SPECIES", "si"]].dropna()
    siteage["SPECIES"] = siteage["SPECIES"].astype(str).str.upper()
    panel = panel.merge(
        siteage.rename(columns={"SPECIES": "species"}),
        on=["CLSTR_ID", "VISIT_NUMBER", "species"],
        how="left",
    )
    if panel["si"].isna().any():
        # Use the plot's first available species SI when the leading-species row is absent.
        first_si = siteage.sort_values(["CLSTR_ID", "VISIT_NUMBER"]).drop_duplicates(
            ["CLSTR_ID", "VISIT_NUMBER"]
        )[["CLSTR_ID", "VISIT_NUMBER", "si"]]
        panel = panel.drop(columns="si").merge(
            first_si, on=["CLSTR_ID", "VISIT_NUMBER"], how="left"
        )
    panel = panel.dropna(subset=["si"]).reset_index(drop=True)

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
        & (trees["CLSTR_ID"].isin(set(panel["CLSTR_ID"])))
        & trees["DBH"].notna()
        & trees["PHF_TREE"].notna()
    ].copy()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    run_root = args.out_dir / "runs"
    if run_root.exists():
        shutil.rmtree(run_root)
    run_root.mkdir(parents=True)
    match_rows: list[dict[str, object]] = []
    curve_rows: list[dict[str, object]] = []
    for au_row in au.itertuples(index=False):
        same_bec = panel["bec"] == au_row.bec
        same_species = panel["species"] == au_row.leading_species
        candidates = panel[same_bec & same_species].copy()
        if candidates.empty:
            candidates = panel[panel["bec"] == au_row.bec].copy()
        if candidates.empty:
            raise ValueError(f"no FAIB plots for AU {au_row.au_id}")
        in_band = candidates[
            (candidates["si"] >= au_row.site_index_min)
            & (candidates["si"] <= au_row.site_index_max)
        ].copy()
        source = in_band if len(in_band) >= 2 else candidates
        source["distance"] = (source["si"] - au_row.site_index_median).abs()
        source = source.sort_values(["distance", "ba"]).head(args.plots_per_au)
        case_curves = []
        for state in source.itertuples(index=False):
            state_series = pd.Series(state._asdict())
            records = _records(state_series, trees)
            if not records:
                continue
            case_dir = run_root / f"{au_row.au_id}__{state_series['CLSTR_ID']}"
            result = run_case(records, _keywords(), directory=case_dir)
            summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
            summary = summary[summary["CaseID"] == result.provenance.case_id]
            tree_list = read_table(result.database, "FVS_TreeList_Metric")
            tree_list = tree_list[tree_list["CaseID"] == result.provenance.case_id].copy()
            large = (
                tree_list[tree_list["DBH"] >= 37.5]
                .assign(ba=lambda frame: 0.00007854 * frame["DBH"] ** 2 * frame["TPH"])
                .groupby("Year", as_index=False)
                .agg(large_ba_m2_ha=("ba", "sum"), large_tph=("TPH", "sum"))
            )
            summary = summary.merge(large, on="Year", how="left").fillna(
                {"large_ba_m2_ha": 0.0, "large_tph": 0.0}
            )
            summary["reserve_ba_m2_ha"] = 0.0
            summary["reserve_tph"] = 0.0
            case_curves.append(
                summary[
                    [
                        "Year",
                        "BA",
                        "Tph",
                        "QMD",
                        "TCuM",
                        "CCF",
                        "large_ba_m2_ha",
                        "large_tph",
                        "reserve_ba_m2_ha",
                        "reserve_tph",
                    ]
                ].rename(
                    columns={
                        "Year": "year",
                        "BA": "ba_m2_ha",
                        "Tph": "tph",
                        "QMD": "qmd_cm",
                        "TCuM": "volume_m3_ha",
                        "CCF": "canopy_ccf",
                    }
                )
            )
            match_rows.append(
                {
                    "au_id": au_row.au_id,
                    "CLSTR_ID": state_series["CLSTR_ID"],
                    "VISIT_NUMBER": int(state_series["VISIT_NUMBER"]),
                    "bec": state_series["bec"],
                    "species": state_series["species"],
                    "si": float(state_series["si"]),
                    "ba": float(state_series["ba"]),
                    "qmd": float(state_series["qmd"]),
                    "age": float(state_series["PROJ_AGE_1"]),
                }
            )
        if not case_curves:
            raise ValueError(f"no FVS cases completed for AU {au_row.au_id}")
        stacked = pd.concat(case_curves, ignore_index=True)
        mean = stacked.groupby("year", as_index=False).mean(numeric_only=True)
        mean.insert(0, "au_id", au_row.au_id)
        mean.insert(1, "si_level", au_row.si_level)
        mean.insert(2, "n_plots", len(case_curves))
        curve_rows.extend(mean.to_dict(orient="records"))

    matches = pd.DataFrame(match_rows)
    curves = pd.DataFrame(curve_rows)
    matches.to_csv(args.out_dir / "kc_au_plot_matches.csv", index=False)
    curves.to_csv(args.out_dir / "kc_au_yield_200y.csv", index=False)
    manifest = {
        "au_table": str(args.au_table),
        "panel": str(args.panel),
        "horizon_years": HORIZON_YEARS,
        "step_years": STEP_YEARS,
        "plots_per_au": args.plots_per_au,
        "aus": len(au),
        "matched_plots": len(matches),
        "curve_rows": len(curves),
        "fvs": "fresh-fvsbc 0.20.0 / FVS-BC",
        "caveats": [
            "No-cut FVS-BC curves, not observed 200-year growth.",
            "Site index and tree age are structural inputs from the FAIB panel.",
            "AU matching is BEC + leading species + SI band, then nearest SI.",
            "No KC calibration or legal-compliance claim.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
