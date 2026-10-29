#!/usr/bin/env python3
"""Summarize observed mortality and ingrowth in the AFRF KC PSP plots.

DBH presence at each measurement is the working live/dead indicator. This is
not a substitute for the unresolved `TS`/`TC` codes.

Usage::

    python runbooks/summarize_psp_dynamics.py \
      --trees data/private/afrf_kc_psp/trees_long.parquet \
      --out-dir data/psp
"""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import numpy as np
import pandas as pd

YEARS = (1993, 1997, 2004, 2008, 2013)
AREA_HA = 0.05


def main() -> None:
    """Write observed mortality/ingrowth summaries."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    trees = pd.read_parquet(args.trees)
    trees = trees[(trees["position"] == "I") & trees["plot"].notna() & trees["tree"].notna()].copy()
    alive = trees[trees["dbh_cm"].notna()].copy()
    first = alive.groupby(["plot", "tree"], as_index=False).agg(
        first_year=("year", "min"),
        block=("block", "first"),
        treatment=("treatment", "first"),
    )
    rows = []
    for start, end in itertools.pairwise(YEARS):
        begin = alive[alive["year"] == start][
            ["plot", "tree", "block", "treatment", "dbh_cm"]
        ].copy()
        alive_end = set(map(tuple, alive[alive["year"] == end][["plot", "tree"]].to_numpy()))
        begin["alive_end"] = [
            (plot, tree) in alive_end
            for plot, tree in zip(begin["plot"], begin["tree"], strict=True)
        ]
        begin["size_class"] = pd.cut(
            begin["dbh_cm"],
            [0.0, 10.0, 20.0, 30.0, 1e9],
            labels=["2_10", "10_20", "20_30", "30_PLUS"],
            right=False,
        )
        recruit = first[(first["first_year"] > start) & (first["first_year"] <= end)]
        years = end - start
        for keys, group in begin.groupby(["block", "treatment", "size_class"], observed=True):
            block, treatment, size_class = keys
            n = len(group)
            dead = int((~group["alive_end"]).sum())
            annual = 1.0 - (1.0 - dead / n) ** (1.0 / years) if n else np.nan
            rec = recruit[(recruit["block"] == block) & (recruit["treatment"] == treatment)]
            rows.append(
                {
                    "interval": f"{start}-{end}",
                    "years": years,
                    "block": block,
                    "treatment": treatment,
                    "size_class": str(size_class),
                    "alive_start": n,
                    "dead": dead,
                    "survivors": n - dead,
                    "annual_mortality": annual,
                    "recruitment_tph": len(rec) / AREA_HA,
                }
            )
    detail = pd.DataFrame(rows)
    detail.to_csv(args.out_dir / "kc_afrf_psp_dynamics.csv", index=False)
    plot_rows = []
    for start, end in itertools.pairwise(YEARS):
        begin = alive[alive["year"] == start][["plot", "tree", "block", "treatment"]].copy()
        alive_end = set(map(tuple, alive[alive["year"] == end][["plot", "tree"]].to_numpy()))
        begin["alive_end"] = [
            (plot, tree) in alive_end
            for plot, tree in zip(begin["plot"], begin["tree"], strict=True)
        ]
        recruit = first[(first["first_year"] > start) & (first["first_year"] <= end)]
        years = end - start
        for (plot, block, treatment), group in begin.groupby(
            ["plot", "block", "treatment"], observed=True
        ):
            n = len(group)
            dead = int((~group["alive_end"]).sum())
            annual = 1.0 - (1.0 - dead / n) ** (1.0 / years) if n else np.nan
            rec = recruit[recruit["plot"] == plot]
            plot_rows.append(
                {
                    "interval": f"{start}-{end}",
                    "years": years,
                    "plot": plot,
                    "block": block,
                    "treatment": treatment,
                    "alive_start": n,
                    "dead": dead,
                    "survivors": n - dead,
                    "annual_mortality": annual,
                    "recruitment_tph": len(rec) / AREA_HA,
                }
            )
    plot = pd.DataFrame(plot_rows)
    plot.to_csv(args.out_dir / "kc_afrf_psp_mortality_by_plot.csv", index=False)
    summary = plot.groupby(["interval", "block", "treatment"], as_index=False).agg(
        alive_start=("alive_start", "sum"),
        dead=("dead", "sum"),
        survivors=("survivors", "sum"),
        recruitment_tph=("recruitment_tph", "mean"),
    )
    summary["annual_mortality"] = 1.0 - (summary["survivors"] / summary["alive_start"]) ** (
        1.0
        / summary["interval"]
        .str.split("-")
        .str[1]
        .astype(int)
        .sub(summary["interval"].str.split("-").str[0].astype(int))
    )
    summary.to_csv(args.out_dir / "kc_afrf_psp_dynamics_summary.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
