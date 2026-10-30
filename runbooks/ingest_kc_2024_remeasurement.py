#!/usr/bin/env python3
"""Ingest the 2024/2025 Knife Creek Marshall plot remeasurement.

The raw workbook is private.  This script writes a private tree-level table and
public derived summaries, including the 2013->2024/2025 transition used for
out-of-sample FVS validation.

The 2024 workbook uses a different schema from the 1993-2013 workbook:
``DBH``/``DBH13``, ``HT``/``HT13``, ``HCB``/``HCB13``, crown radii ``CR1``-``CR4``,
and explicit ``RESIDUAL``/``DEAD``/``INGROWTH`` status.

Usage::

    python runbooks/ingest_kc_2024_remeasurement.py \
      --workbook /path/to/inst88-11_2024meas_clean.xlsx \
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

AREA_HA = 0.05
LARGE_DBH = 37.5
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
GROUPS = {"FD": ("FD",), "SE": ("SE",), "PL": ("PL",), "HW": ("EP", "AT", "OH")}
SPECIES_GROUP = {"FD": "FD", "SE": "SE", "PL": "PL", "EP": "HW", "AT": "HW", "OH": "HW"}


def _number(frame: pd.DataFrame, name: str) -> pd.Series:
    """Return a numeric column, or an all-missing series when absent."""
    if name not in frame.columns:
        return pd.Series(np.nan, index=frame.index)
    return pd.to_numeric(frame[name], errors="coerce")


def _measurement_date(value: object) -> pd.Timestamp:
    """Parse the workbook's compact ddmmyyyy / dmmyyyy integer date."""
    text = str(int(value)) if pd.notna(value) else ""
    if len(text) == 7:
        day, month, year = text[0], text[1:3], text[3:]
    elif len(text) == 8:
        day, month, year = text[:2], text[2:4], text[4:]
    else:
        return pd.NaT
    return pd.to_datetime(f"{year}-{month}-{day}", errors="coerce")


def _metrics(group: pd.DataFrame) -> dict[str, float]:
    """Stand metrics for one plot and measurement year."""
    if group.empty:
        return {
            "n": 0,
            "ba_m2_ha": np.nan,
            "tph": np.nan,
            "qmd_cm": np.nan,
            "mean_height_m": np.nan,
            "large_ba_m2_ha": np.nan,
            "large_tph": np.nan,
        }
    ba = 0.00007854 * group["dbh_cm"] ** 2 / AREA_HA
    large = group[group["dbh_cm"] >= LARGE_DBH]
    return {
        "n": len(group),
        "ba_m2_ha": float(ba.sum()),
        "tph": len(group) / AREA_HA,
        "qmd_cm": float(np.sqrt((group["dbh_cm"] ** 2).sum() / len(group))),
        "mean_height_m": float(group["height_m"].mean()),
        "large_ba_m2_ha": float((0.00007854 * large["dbh_cm"] ** 2 / AREA_HA).sum()),
        "large_tph": len(large) / AREA_HA,
    }


def _group_metrics(group: pd.DataFrame) -> dict[str, dict[str, float]]:
    """Species-group BA and TPH for one plot and year."""
    grouped = group.assign(group=group["species"].map(SPECIES_GROUP).fillna("OTHER"))
    result = {}
    for name, subset in grouped.groupby("group"):
        if name == "OTHER":
            continue
        result[name] = {
            "ba_m2_ha": float((0.00007854 * subset["dbh_cm"] ** 2 / AREA_HA).sum()),
            "tph": len(subset) / AREA_HA,
        }
    return result


def _clean_rows(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalise the remeasurement workbook to one live/dead row per stem."""
    frame = frame.copy()
    frame["plot"] = pd.to_numeric(frame["plot"], errors="coerce")
    frame["tree"] = pd.to_numeric(frame["tree"], errors="coerce").astype("Int64")
    frame["status_label"] = frame["status"].astype(str).str.strip().str.upper()
    frame["position"] = np.where(
        frame["buffer"].astype(str).str.strip().str.upper() == "B", "B", "I"
    )
    frame["species"] = frame["spp"].astype(str).str.strip().str.upper().map(SPECIES).fillna("OH")
    frame["date"] = frame["measdate"].map(_measurement_date)
    frame["year"] = frame["date"].dt.year
    frame["dbh_cm"] = _number(frame, "DBH")
    frame["height_m"] = _number(frame, "HT")
    frame["prior_dbh_cm"] = _number(frame, "DBH13")
    frame["prior_height_m"] = _number(frame, "HT13")
    hcb = _number(frame, "HCB")
    frame["live_crown_base_m"] = hcb
    frame["crown_ratio"] = np.where(
        (frame["height_m"] > 0) & hcb.notna(),
        (frame["height_m"] - hcb) / frame["height_m"],
        np.nan,
    )
    for radius in (1, 2, 3, 4):
        frame[f"cw{radius}_m"] = 2.0 * _number(frame, f"CR{radius}")
    frame["crown_width_m"] = frame[["cw1_m", "cw2_m"]].mean(axis=1)
    frame["lc1_m"] = hcb
    frame["lc2_m"] = hcb
    frame["lc3_m"] = hcb
    frame["lc4_m"] = hcb
    frame["vigor"] = np.nan
    frame["tree_class"] = (
        frame["CRCLASS"].astype(str).str.strip().str.upper().map({"D": 1, "C": 2, "I": 3, "S": 4})
    )
    frame["block"] = frame["plot"].map(
        lambda value: TREATMENT.get(int(value), ("?", "?"))[0] if pd.notna(value) else "?"
    )
    frame["treatment"] = frame["plot"].map(
        lambda value: TREATMENT.get(int(value), ("?", "?"))[1] if pd.notna(value) else "?"
    )
    # DBH presence is the working live indicator in the 1993-2013 table.
    # Preserve dead-tree rows but blank the DBH so downstream live filters work.
    dead = frame["status_label"] == "DEAD"
    frame.loc[dead, ["dbh_cm", "height_m", "crown_width_m"]] = np.nan
    # When a stem is duplicated, keep one live row with a DBH, else one dead row.
    frame["_live"] = frame["status_label"].isin(["RESIDUAL", "INGROWTH"]) & frame["dbh_cm"].notna()
    frame = frame.sort_values(["plot", "tree", "_live", "status_label"]).drop_duplicates(
        ["plot", "tree"], keep="last"
    )
    return frame.drop(columns="_live").sort_values(["plot", "tree"])


def main() -> None:
    """Write the private remeasurement table and public transition summaries."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--private-dir", type=Path, required=True)
    parser.add_argument("--public-dir", type=Path, required=True)
    parser.add_argument(
        "--prior-trees",
        type=Path,
        default=Path("data/private/afrf_kc_psp/trees_long.csv"),
    )
    args = parser.parse_args()

    frame = _clean_rows(pd.read_excel(args.workbook, sheet_name=0))
    frame = frame[frame["plot"].notna()].copy()
    if frame["year"].isna().any():
        missing = sorted(frame.loc[frame["year"].isna(), "plot"].unique().tolist())
        raise ValueError(f"missing measurement date for plots: {missing}")
    args.private_dir.mkdir(parents=True, exist_ok=True)
    long_path = args.private_dir / "trees_long_2024.csv"
    columns = [
        "plot",
        "position",
        "tree",
        "species",
        "year",
        "dbh_cm",
        "height_m",
        "cw1_m",
        "cw2_m",
        "cw3_m",
        "cw4_m",
        "lc1_m",
        "lc2_m",
        "lc3_m",
        "lc4_m",
        "vigor",
        "tree_class",
        "crown_width_m",
        "live_crown_base_m",
        "crown_ratio",
        "block",
        "treatment",
        "status_label",
        "prior_dbh_cm",
        "prior_height_m",
    ]
    frame[columns].to_csv(long_path, index=False)

    live = frame[
        (frame["position"] == "I")
        & frame["dbh_cm"].notna()
        & frame["status_label"].isin(["RESIDUAL", "INGROWTH"])
    ].copy()
    summary_rows = []
    for (plot, year), group in live.groupby(["plot", "year"]):
        metrics = _metrics(group)
        groups = _group_metrics(group)
        summary_rows.append(
            {
                "plot": int(plot),
                "block": group["block"].iloc[0],
                "treatment": group["treatment"].iloc[0],
                "year": int(year),
                "area_ha": AREA_HA,
                **metrics,
                "fd_ba_share": groups.get("FD", {}).get("ba_m2_ha", 0.0) / metrics["ba_m2_ha"],
                "se_ba_share": groups.get("SE", {}).get("ba_m2_ha", 0.0) / metrics["ba_m2_ha"],
                "pl_ba_share": groups.get("PL", {}).get("ba_m2_ha", 0.0) / metrics["ba_m2_ha"],
            }
        )
    summary = pd.DataFrame(summary_rows).sort_values(["plot", "year"])
    summary.to_csv(args.public_dir / "kc_afrf_psp_plot_summary_2024.csv", index=False)

    prior = pd.read_csv(args.prior_trees)
    prior = prior[
        (prior["year"] == 2013) & (prior["position"] == "I") & prior["dbh_cm"].notna()
    ].copy()
    transition_rows = []
    species_rows = []
    for plot in sorted(set(prior["plot"]).intersection(set(live["plot"]))):
        start = prior[prior["plot"] == plot]
        end = live[live["plot"] == plot]
        end_year = int(end["year"].max())
        start_keys = set(start["tree"].astype(int))
        end_keys = set(end["tree"].astype(int))
        survivors = start_keys & end_keys
        ingrowth = end_keys - start_keys
        mortality = start_keys - end_keys
        start_metrics = _metrics(start)
        end_metrics = _metrics(end)
        years = end_year - 2013
        row = {
            "interval_id": f"2013-{end_year}",
            "plot": int(plot),
            "block": end["block"].iloc[0],
            "treatment": end["treatment"].iloc[0],
            "subset_cd": end["block"].iloc[0] in {"C", "D"},
            "start_year": 2013,
            "end_year": end_year,
            "years": years,
            "n_start": len(start),
            "n_end": len(end),
            "n_survivors": len(survivors),
            "mortality_n": len(mortality),
            "ingrowth_n": len(ingrowth),
            "ba_start_m2_ha": start_metrics["ba_m2_ha"],
            "ba_end_m2_ha": end_metrics["ba_m2_ha"],
            "tph_start": start_metrics["tph"],
            "tph_end": end_metrics["tph"],
            "qmd_start_cm": start_metrics["qmd_cm"],
            "qmd_end_cm": end_metrics["qmd_cm"],
            "mean_height_start_m": start_metrics["mean_height_m"],
            "mean_height_end_m": end_metrics["mean_height_m"],
            "large_ba_start_m2_ha": start_metrics["large_ba_m2_ha"],
            "large_ba_end_m2_ha": end_metrics["large_ba_m2_ha"],
            "large_tph_start": start_metrics["large_tph"],
            "large_tph_end": end_metrics["large_tph"],
            "annual_mortality": (
                1.0 - (len(survivors) / len(start_keys)) ** (1.0 / years) if start_keys else np.nan
            ),
            "mortality_tph": len(mortality) / AREA_HA,
            "ingrowth_tph": len(ingrowth) / AREA_HA,
        }
        transition_rows.append(row)
        start_groups = _group_metrics(start)
        end_groups = _group_metrics(end)
        for group in GROUPS:
            species_rows.append(
                {
                    "interval_id": row["interval_id"],
                    "plot": int(plot),
                    "block": row["block"],
                    "treatment": row["treatment"],
                    "subset_cd": row["subset_cd"],
                    "species_group": group,
                    "ba_start_m2_ha": start_groups.get(group, {}).get("ba_m2_ha", 0.0),
                    "ba_end_m2_ha": end_groups.get(group, {}).get("ba_m2_ha", 0.0),
                    "tph_start": start_groups.get(group, {}).get("tph", 0.0),
                    "tph_end": end_groups.get(group, {}).get("tph", 0.0),
                }
            )
    transitions = pd.DataFrame(transition_rows).sort_values(["plot", "start_year"])
    transitions.to_csv(args.public_dir / "kc_afrf_psp_transitions_2024.csv", index=False)
    pd.DataFrame(species_rows).sort_values(["plot", "species_group"]).to_csv(
        args.public_dir / "kc_afrf_psp_transitions_2024_species.csv", index=False
    )
    metadata = {
        "source": "AFRF Knife Creek 2024/2025 Marshall plot remeasurement",
        "workbook_sha256": hashlib.sha256(args.workbook.read_bytes()).hexdigest(),
        "plots": int(transitions["plot"].nunique()),
        "intervals": int(transitions["interval_id"].nunique()),
        "rows": len(transitions),
        "measurement_years": transitions["end_year"].value_counts().to_dict(),
        "area_ha": AREA_HA,
        "large_dbh_cm": LARGE_DBH,
        "assumptions": [
            "The 2013 measurement is the pre-entry state; the 2024/2025 "
            "measurement is the end state.",
            "Interior trees only (buffer B excluded).",
            "DBH presence is the working live-tree indicator.",
            "A 2013 tree absent from the 2024 live list is mortality; a new live tree is ingrowth.",
            "Plot 1 and plot 2 end in 2024; the remaining plots end in 2025.",
            "Each stem is expanded by 20 (0.05 ha plot).",
        ],
        "caveats": [
            "Raw tree-level data are private and are not committed.",
            "Some residual stems have no current DBH and are treated as non-live for metrics.",
            "The 24-plot thinning experiment is not a whole-block sample.",
            "No age or site index is assigned; the stands are uneven-aged.",
        ],
        "files": [
            "trees_long_2024.csv",
            "kc_afrf_psp_plot_summary_2024.csv",
            "kc_afrf_psp_transitions_2024.csv",
            "kc_afrf_psp_transitions_2024_species.csv",
        ],
    }
    (args.public_dir / "kc_afrf_psp_2024_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )
    print(
        f"plots={transitions['plot'].nunique()} rows={len(transitions)} "
        f"end_years={transitions['end_year'].value_counts().to_dict()}"
    )
    print(
        transitions[
            ["plot", "end_year", "ba_start_m2_ha", "ba_end_m2_ha", "tph_start", "tph_end"]
        ].head()
    )


if __name__ == "__main__":
    main()
