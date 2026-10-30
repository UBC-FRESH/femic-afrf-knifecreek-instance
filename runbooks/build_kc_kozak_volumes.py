#!/usr/bin/env python3
"""Compute Kozak merchantable volumes for the normalized Marshal trees.

The R implementation from the UBC Research Forests Kozak package is run as a
subprocess.  Outputs stay in the private DataLad store.

Usage::

    python runbooks/build_kc_kozak_volumes.py \
      --trees external/ubc-research-forests-data/processed/kc_spatial/kc_marshal_trees.parquet \
      --r-script runbooks/compute_kc_kozak_volume.R \
      --out-dir external/ubc-research-forests-data/processed/kc_spatial
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import pandas as pd


def main() -> None:
    """Run the R taper calculation and join volumes to the tree table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees", type=Path, required=True)
    parser.add_argument("--r-script", type=Path, required=True)
    parser.add_argument("--kozak-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    trees = pd.read_parquet(args.trees).reset_index(drop=True)
    trees["row_id"] = range(1, len(trees) + 1)
    source = trees[["row_id", "species", "dbh_cm", "height_m"]].rename(
        columns={"height_m": "height_m"}
    )
    input_path = args.out_dir / "kc_marshal_trees_kozak_input.csv"
    output_path = args.out_dir / "kc_marshal_trees_kozak_output.csv"
    source.to_csv(input_path, index=False)
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
            "merch.ht": "merch_ht",
            "stump.vol": "stump_vol",
            "top.vol": "top_vol",
            "break.vol": "break_vol",
            "merch.vol": "merch_vol",
            "wsv.vol": "wsv_vol",
        }
    )
    joined = trees.merge(volumes, on="row_id", how="left")
    joined.to_parquet(args.out_dir / "kc_marshal_trees_kozak.parquet", index=False)
    joined.to_csv(args.out_dir / "kc_marshal_trees_kozak.csv", index=False)
    summary = (
        joined.groupby(["source_plot", "species"], as_index=False)
        .agg(
            n_trees=("row_id", "size"),
            mean_dbh_cm=("dbh_cm", "mean"),
            mean_height_m=("height_m", "mean"),
            merch_vol_m3=("merch_vol", "sum"),
            wsv_vol_m3=("wsv_vol", "sum"),
        )
        .sort_values(["source_plot", "species"])
    )
    summary.to_csv(args.out_dir / "kc_marshal_kozak_summary.csv", index=False)
    print(
        joined[["source_plot", "species", "dbh_cm", "height_m", "merch_ht", "merch_vol"]]
        .head(10)
        .to_string(index=False)
    )
    print(summary.groupby("species")[["n_trees", "merch_vol_m3", "wsv_vol_m3"]].sum())
    print(f"rows={len(joined)} output={args.out_dir}")


if __name__ == "__main__":
    main()
