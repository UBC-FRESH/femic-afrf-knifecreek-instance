#!/usr/bin/env python3
"""Build observed AFRF Knife Creek PSP transitions.

The output is a plot-interval transition table, not a tree-level release. Each
interval uses DBH presence as the working live-tree indicator because the
workbook's `TS`/`TC` codes remain undocumented.

Usage::

    python runbooks/build_psp_transitions.py \
      --trees data/private/afrf_kc_psp/trees_long.csv \
      --out-dir data/psp
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

YEARS = (1993, 1997, 2004, 2008, 2013)
AREA_HA = 0.05
LARGE_DBH = 37.5
GROUPS = {
    "FD": ("FD",),
    "SE": ("SE",),
    "PL": ("PL",),
    "HW": ("EP", "AT", "OH"),
}
SPECIES_GROUP = {
    "FD": "FD",
    "SE": "SE",
    "PL": "PL",
    "EP": "HW",
    "AT": "HW",
    "OH": "HW",
}


def _metrics(group: pd.DataFrame) -> dict[str, float]:
    """Stand metrics for one plot and measurement year."""
    n = len(group)
    if n == 0:
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
        "n": n,
        "ba_m2_ha": float(ba.sum()),
        "tph": n / AREA_HA,
        "qmd_cm": float(np.sqrt((group["dbh_cm"] ** 2).sum() / n)),
        "mean_height_m": float(group["height_m"].mean()),
        "large_ba_m2_ha": float((0.00007854 * large["dbh_cm"] ** 2 / AREA_HA).sum()),
        "large_tph": len(large) / AREA_HA,
    }


def _group_metrics(group: pd.DataFrame) -> dict[str, dict[str, float]]:
    """Species-group BA and TPH for one plot and year."""
    result = {}
    grouped = group.assign(group=group["species"].map(SPECIES_GROUP).fillna("OTHER"))
    for name, subset in grouped.groupby("group"):
        if name == "OTHER":
            continue
        result[name] = {
            "ba_m2_ha": float((0.00007854 * subset["dbh_cm"] ** 2 / AREA_HA).sum()),
            "tph": len(subset) / AREA_HA,
        }
    return result


def main() -> None:
    """Write the observed transition tables and metadata."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    trees = pd.read_csv(args.trees)
    trees = trees[
        (trees["position"] == "I")
        & trees["plot"].notna()
        & trees["tree"].notna()
        & trees["year"].isin(YEARS)
    ].copy()
    live = trees[trees["dbh_cm"].notna()].copy()
    transitions = []
    species_rows = []
    for start, end in itertools.pairwise(YEARS):
        years = end - start
        for plot, plot_start in live[live["year"] == start].groupby("plot"):
            start_keys = set(plot_start["tree"])
            end_group = live[(live["plot"] == plot) & (live["year"] == end)]
            end_keys = set(end_group["tree"])
            survivors = start_keys & end_keys
            ingrowth = end_keys - start_keys
            mortality = start_keys - end_keys
            block = str(plot_start["block"].iloc[0])
            treatment = str(plot_start["treatment"].iloc[0])
            start_metrics = _metrics(plot_start)
            end_metrics = _metrics(end_group)
            transitions.append(
                {
                    "interval_id": f"{start}-{end}",
                    "plot": int(plot),
                    "block": block,
                    "treatment": treatment,
                    "subset_cd": block in {"C", "D"},
                    "start_year": start,
                    "end_year": end,
                    "years": years,
                    "n_start": start_metrics["n"],
                    "n_end": end_metrics["n"],
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
                        1.0 - (len(survivors) / len(start_keys)) ** (1.0 / years)
                        if start_keys
                        else np.nan
                    ),
                    "mortality_tph": len(mortality) / AREA_HA,
                    "ingrowth_tph": len(ingrowth) / AREA_HA,
                }
            )
            start_groups = _group_metrics(plot_start)
            end_groups = _group_metrics(end_group)
            for group in GROUPS:
                species_rows.append(
                    {
                        "interval_id": f"{start}-{end}",
                        "plot": int(plot),
                        "block": block,
                        "treatment": treatment,
                        "subset_cd": block in {"C", "D"},
                        "species_group": group,
                        "ba_start_m2_ha": start_groups.get(group, {}).get("ba_m2_ha", 0.0),
                        "ba_end_m2_ha": end_groups.get(group, {}).get("ba_m2_ha", 0.0),
                        "tph_start": start_groups.get(group, {}).get("tph", 0.0),
                        "tph_end": end_groups.get(group, {}).get("tph", 0.0),
                    }
                )
    frame = pd.DataFrame(transitions).sort_values(["plot", "start_year"])
    species = pd.DataFrame(species_rows).sort_values(["plot", "interval_id", "species_group"])
    frame.to_csv(args.out_dir / "kc_afrf_psp_transitions.csv", index=False)
    species.to_csv(args.out_dir / "kc_afrf_psp_transitions_species.csv", index=False)
    metadata = {
        "source": "AFRF Knife Creek PSP workbook, derived transition table",
        "sha256": hashlib.sha256(args.trees.read_bytes()).hexdigest(),
        "plots": int(frame["plot"].nunique()),
        "intervals": int(frame["interval_id"].nunique()),
        "rows": len(frame),
        "block_rows": frame["block"].value_counts().to_dict(),
        "subset_cd_rows": int(frame["subset_cd"].sum()),
        "area_ha": AREA_HA,
        "large_dbh_cm": LARGE_DBH,
        "assumptions": [
            "P=I is the plot population; P=B is excluded.",
            "DBH presence at a measurement is the working live-tree indicator.",
            "A tree with first DBH after the interval start is ingrowth.",
            "A start-live tree without DBH at the end is mortality.",
            "No TS/TC, D1/D2/DA/DS/WTA or age fields are used.",
            "No absolute plot centres are available; no spatial join is implied.",
        ],
        "caveats": [
            "TS/TC are unresolved; DBH presence may misclassify some dead trees.",
            "The 24-plot thinning experiment is not a whole-block sample.",
            "The 16 Block C/D plots are flagged separately; they are not the same sample.",
            "Raw tree-level data are private and not in this release.",
            "No age or site index is assigned; the stands are uneven-aged.",
        ],
        "files": [
            "kc_afrf_psp_transitions.csv",
            "kc_afrf_psp_transitions_species.csv",
        ],
    }
    (args.out_dir / "kc_afrf_psp_transitions_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )
    print(
        f"rows={len(frame)} plots={frame['plot'].nunique()} "
        f"intervals={frame['interval_id'].nunique()} species_rows={len(species)}"
    )


if __name__ == "__main__":
    main()
