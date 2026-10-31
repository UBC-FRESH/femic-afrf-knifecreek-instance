#!/usr/bin/env python3
"""Compare Kozak merchantable volume with FVS total stem volume.

The AU product curves use FVS total cubic metres.  This script computes Kozak
merchantable volume on the same initial FVS tree lists so the model can carry a
defensible volume-basis correction by AU.

Usage::

    python runbooks/build_kc_volume_basis.py \
      --runs data/psp/kc_au_200y/runs \
      --r-script runbooks/compute_kc_kozak_volume.R \
      --kozak-dir external/.../KozakTaper_Version6 \
      --out-dir external/.../processed/kc_spatial
"""

from __future__ import annotations

import argparse
import sqlite3
import subprocess
from pathlib import Path

import pandas as pd


def main() -> None:
    """Write plot- and AU-level volume-basis ratios."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--r-script", type=Path, required=True)
    parser.add_argument("--kozak-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    summaries = []
    for run in sorted(args.runs.iterdir()):
        database = run / "FVSOut.db"
        if not database.exists() or "__" not in run.name:
            continue
        au_id = run.name.split("__", 1)[0]
        with sqlite3.connect(database) as connection:
            trees = pd.read_sql(
                "SELECT Year, SpeciesFVS, DBH, Ht, TPH FROM FVS_TreeList_Metric WHERE Year = 0",
                connection,
            )
            summary = pd.read_sql(
                "SELECT Year, TCuM FROM FVS_Summary_Metric WHERE Year = 0",
                connection,
            )
        if trees.empty or summary.empty:
            continue
        trees = trees.rename(columns={"SpeciesFVS": "species", "DBH": "dbh_cm", "Ht": "height_m"})
        trees["plot_id"] = run.name
        rows.append(trees)
        summaries.append(
            {
                "plot_id": run.name,
                "au_id": au_id,
                "fvs_tcum_m3_ha": float(summary["TCuM"].iloc[0]),
            }
        )
    trees = pd.concat(rows, ignore_index=True)
    trees["row_id"] = range(1, len(trees) + 1)
    input_path = args.out_dir / "kc_volume_basis_input.csv"
    output_path = args.out_dir / "kc_volume_basis_output.csv"
    args.out_dir.mkdir(parents=True, exist_ok=True)
    trees[["row_id", "species", "dbh_cm", "height_m"]].to_csv(input_path, index=False)
    subprocess.run(
        [
            "Rscript",
            str(args.r_script.resolve()),
            str(input_path.resolve()),
            str(output_path.resolve()),
        ],
        check=True,
        cwd=args.kozak_dir,
    )
    volumes = pd.read_csv(output_path).rename(
        columns={
            "merch.vol": "merch_vol",
            "wsv.vol": "wsv_vol",
        }
    )
    merged = trees.merge(volumes, on="row_id", how="left")
    merged["kozak_merch_m3_ha"] = merged["merch_vol"] * merged["TPH"]
    merged["kozak_wsv_m3_ha"] = merged["wsv_vol"] * merged["TPH"]
    plot = (
        merged.groupby("plot_id", as_index=False)
        .agg(
            kozak_merch_m3_ha=("kozak_merch_m3_ha", "sum"),
            kozak_wsv_m3_ha=("kozak_wsv_m3_ha", "sum"),
        )
        .merge(pd.DataFrame(summaries), on="plot_id", how="left")
    )
    plot["merch_to_fvs"] = plot["kozak_merch_m3_ha"] / plot["fvs_tcum_m3_ha"]
    plot["wsv_to_fvs"] = plot["kozak_wsv_m3_ha"] / plot["fvs_tcum_m3_ha"]
    au = (
        plot.groupby("au_id", as_index=False)
        .agg(
            n_plots=("plot_id", "size"),
            kozak_merch_m3_ha=("kozak_merch_m3_ha", "mean"),
            kozak_wsv_m3_ha=("kozak_wsv_m3_ha", "mean"),
            fvs_tcum_m3_ha=("fvs_tcum_m3_ha", "mean"),
            merch_to_fvs=("merch_to_fvs", "mean"),
            wsv_to_fvs=("wsv_to_fvs", "mean"),
        )
        .sort_values("au_id")
    )
    plot.to_csv(args.out_dir / "kc_volume_basis_plots.csv", index=False)
    au.to_csv(args.out_dir / "kc_volume_basis_au.csv", index=False)
    print(au.to_string(index=False))


if __name__ == "__main__":
    main()
