#!/usr/bin/env python3
"""Ingest the AFRF Knife Creek PSP workbook into tidy tables.

The raw workbook is private and is not committed. Tree-level output goes under
data/private/; a public plot summary and schema are written under data/psp/.

Assumptions are documented in notes/reference/kc-afrf-psp-dataset.md.

Usage::

    python runbooks/ingest_afrf_kc_psp.py \
      --workbook /path/to/88-11.xlsx \
      --private-dir data/private/afrf_kc_psp \
      --public-dir data/psp
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

YEARS = (1993, 1997, 2004, 2008, 2013)
AREA_HA = 0.05
TREATMENT = {
    1: ("B", "C1"),
    2: ("B", "C1"),
    3: ("B", "U"),
    4: ("B", "U"),
    5: ("B", "C2"),
    6: ("B", "C2"),
    7: ("B", "S"),
    8: ("B", "S"),
    9: ("D", "S"),
    10: ("D", "S"),
    11: ("D", "C1"),
    12: ("D", "C1"),
    13: ("D", "C2"),
    14: ("D", "C2"),
    15: ("D", "U"),
    16: ("D", "U"),
    17: ("C", "C2"),
    18: ("C", "C2"),
    19: ("C", "U"),
    20: ("C", "U"),
    21: ("C", "C1"),
    22: ("C", "C1"),
    23: ("C", "S"),
    24: ("C", "S"),
}
SPECIES = {"FD": "FD", "SX": "SE", "PL": "PL", "EP": "EP", "AT": "AT", "W": "OH"}


def _read_workbook(path: Path) -> pd.DataFrame:
    frames = []
    for sheet in pd.ExcelFile(path).sheet_names:
        frame = pd.read_excel(path, sheet_name=sheet, header=0)
        frame = frame.loc[:, ~frame.columns.astype(str).str.startswith("Unnamed")]
        base = frame.columns.astype(str).str.replace(r"\.\d+$", "", regex=True)
        frame = frame.loc[:, ~base.duplicated()]
        frame["sheet"] = sheet
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def _num(frame: pd.DataFrame, name: str) -> pd.Series:
    """Return a numeric column, or an all-missing series when absent."""
    if name not in frame.columns:
        return pd.Series(np.nan, index=frame.index)
    return pd.to_numeric(frame[name], errors="coerce")


def _long(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year in YEARS:
        suffix = str(year)[-2:]
        d = pd.DataFrame(
            {
                "plot": pd.to_numeric(frame["Plot"], errors="coerce"),
                "position": frame["P"].astype(str).str.strip().str.upper(),
                "tree": pd.to_numeric(frame["T"], errors="coerce"),
                "species": frame["SP"].astype(str).str.strip().str.upper().replace(SPECIES),
                "x_m": pd.to_numeric(frame["X"], errors="coerce"),
                "y_m": pd.to_numeric(frame["Y"], errors="coerce"),
                "year": year,
                "dbh_cm": _num(frame, f"D-{suffix}"),
                "height_m": _num(frame, f"HT-{suffix}"),
                "cw1_m": _num(frame, f"CW1-{suffix}"),
                "cw2_m": _num(frame, f"CW2-{suffix}"),
                "lc1_m": _num(frame, f"LC1-{suffix}"),
                "lc2_m": _num(frame, f"LC2-{suffix}"),
                "lc3_m": _num(frame, f"LC3-{suffix}"),
                "lc4_m": _num(frame, f"LC4-{suffix}"),
                "vigor": _num(frame, f"V-{suffix}"),
                "status": pd.to_numeric(frame["TS"], errors="coerce"),
                "tree_class": pd.to_numeric(frame["TC"], errors="coerce"),
            }
        )
        rows.append(d)
    long = pd.concat(rows, ignore_index=True)
    long["crown_width_m"] = long[["cw1_m", "cw2_m"]].mean(axis=1)
    long["live_crown_base_m"] = long[["lc1_m", "lc2_m", "lc3_m", "lc4_m"]].mean(axis=1)
    long["crown_ratio"] = np.where(
        (long["height_m"] > 0) & long["live_crown_base_m"].notna(),
        (long["height_m"] - long["live_crown_base_m"]) / long["height_m"],
        np.nan,
    )
    long.loc[(long["crown_ratio"] < 0) | (long["crown_ratio"] > 1), "crown_ratio"] = np.nan
    long["block"] = long["plot"].map(
        lambda p: TREATMENT.get(int(p), ("?", "?"))[0] if pd.notna(p) else "?"
    )
    long["treatment"] = long["plot"].map(
        lambda p: TREATMENT.get(int(p), ("?", "?"))[1] if pd.notna(p) else "?"
    )
    return long


def _plot_summary(long: pd.DataFrame) -> pd.DataFrame:
    live = long[(long["position"] == "I") & (long["dbh_cm"].notna())].copy()
    rows = []
    for (plot, year), group in live.groupby(["plot", "year"]):
        ba = float((0.00007854 * group["dbh_cm"] ** 2).sum() / AREA_HA)
        qmd = float(np.sqrt((group["dbh_cm"] ** 2).sum() / len(group))) if len(group) else np.nan
        large = group[group["dbh_cm"] >= 37.5]
        species_ba = (0.00007854 * group["dbh_cm"] ** 2).groupby(group["species"]).sum() / AREA_HA
        rows.append(
            {
                "plot": int(plot),
                "block": TREATMENT[int(plot)][0],
                "treatment": TREATMENT[int(plot)][1],
                "year": int(year),
                "area_ha": AREA_HA,
                "n": len(group),
                "tph": len(group) / AREA_HA,
                "ba_m2_ha": ba,
                "qmd_cm": qmd,
                "mean_height_m": float(group["height_m"].mean()),
                "large_ba_m2_ha": float((0.00007854 * large["dbh_cm"] ** 2).sum() / AREA_HA),
                "large_tph": len(large) / AREA_HA,
                "fd_ba_share": float(species_ba.get("FD", 0.0) / ba) if ba else 0.0,
                "sx_ba_share": float(species_ba.get("SE", 0.0) / ba) if ba else 0.0,
                "pl_ba_share": float(species_ba.get("PL", 0.0) / ba) if ba else 0.0,
            }
        )
    return pd.DataFrame(rows).sort_values(["plot", "year"])


def main() -> None:
    """Read the workbook and write the private/public tables."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--private-dir", type=Path, required=True)
    parser.add_argument("--public-dir", type=Path, required=True)
    args = parser.parse_args()
    args.private_dir.mkdir(parents=True, exist_ok=True)
    args.public_dir.mkdir(parents=True, exist_ok=True)
    raw = _read_workbook(args.workbook)
    long = _long(raw)
    summary = _plot_summary(long)
    long.to_parquet(args.private_dir / "trees_long.parquet", index=False)
    long.to_csv(args.private_dir / "trees_long.csv", index=False)
    summary.to_csv(args.private_dir / "plot_summary.csv", index=False)
    summary.to_csv(args.public_dir / "kc_afrf_psp_plot_summary.csv", index=False)
    schema = long.dtypes.astype(str).reset_index().rename(columns={"index": "column", 0: "dtype"})
    schema.to_csv(args.public_dir / "kc_afrf_psp_schema.csv", index=False)
    metadata = {
        "source": "AFRF Knife Creek PSP workbook",
        "sha256": hashlib.sha256(args.workbook.read_bytes()).hexdigest(),
        "rows": len(long),
        "plots": int(long["plot"].nunique()),
        "years": list(YEARS),
        "area_ha": AREA_HA,
        "position_counts": long["position"].value_counts().to_dict(),
        "public_files": [
            "kc_afrf_psp_plot_summary.csv",
            "kc_afrf_psp_schema.csv",
        ],
        "private_files": ["trees_long.parquet", "plot_summary.csv"],
        "assumptions": [
            "P=I is the plot population; P=B is the 5 m buffer.",
            "Plot area 0.05 ha, expansion 20.",
            "X/Y are metres from plot centre; no conversion applied "
            "(P. Marshall, pers. comm., 2026-10-29).",
            "DBH cm, height/crown/live-crown-base m.",
            "TS/TC/D1/D2/DA/DS/WTA are not used.",
        ],
    }
    (args.public_dir / "kc_afrf_psp_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )
    print(
        f"rows={len(long)} plots={long['plot'].nunique()} summary={len(summary)} "
        f"public={args.public_dir / 'kc_afrf_psp_plot_summary.csv'}"
    )


if __name__ == "__main__":
    main()
