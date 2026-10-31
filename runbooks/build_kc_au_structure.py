#!/usr/bin/env python3
"""Build the AU/HMZ structural layer from plot and LiDAR metrics.

This combines:

- empirical clump distributions from the eight Marshal tree maps;
- 2019 LiDAR canopy height, cover and gap metrics for all 24 plots;
- the calibrated LiDAR clump proxy.

The empirical tree-map clumps are only available in the AU/HMZ groups covered
by the eight mapped plots. Other groups are LiDAR-only and are labelled as such.

Outputs are private and live in the DataLad store.

Usage::

    python runbooks/build_kc_au_structure.py \
      --plots external/.../processed/kc_spatial/kc_marshal_plots.gpkg \
      --tree-clumps external/.../processed/kc_spatial/kc_marshal_tree_clumps.csv \
      --lidar external/.../processed/kc_spatial/kc_marshal_lidar_structure.csv \
      --lidar-clumps external/.../processed/kc_spatial/kc_marshal_lidar_clumps_calibrated.csv \
      --fragments data/patchworks_knifecreek/spatial_split/fragments.shp \
      --assignment data/kc_au/kc_au_assignment.csv \
      --out-dir external/.../processed/kc_spatial
"""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd


def _plot_au(plots: gpd.GeoDataFrame, fragments: gpd.GeoDataFrame) -> pd.DataFrame:
    """Assign each plot to the block/AU/HMZ with maximum overlap."""
    rows = []
    for plot in plots.itertuples(index=False):
        best = None
        for block in fragments.itertuples(index=False):
            overlap = plot.geometry.intersection(block.geometry).area
            if overlap > 0 and (best is None or overlap > best[0]):
                best = (overlap, block)
        if best is None:
            continue
        overlap, block = best
        rows.append(
            {
                "plot_id": int(plot.PLOT_ID),
                "block_id": int(block.BLOCK),
                "au_id": block.au_id,
                "hmz": block.HMZ,
                "plot_area_ha": plot.geometry.area / 10000.0,
                "overlap_ha": overlap / 10000.0,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    """Write the plot-to-AU map and AU/HMZ structure table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plots", type=Path, required=True)
    parser.add_argument("--tree-clumps", type=Path, required=True)
    parser.add_argument("--lidar", type=Path, required=True)
    parser.add_argument("--lidar-clumps", type=Path, required=True)
    parser.add_argument("--fragments", type=Path, required=True)
    parser.add_argument("--assignment", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    plots = gpd.read_file(args.plots).to_crs(3005)
    fragments = gpd.read_file(args.fragments).to_crs(3005)
    assignment = pd.read_csv(args.assignment)[["POLYGON_ID", "au_id"]].rename(
        columns={"POLYGON_ID": "POLY_ID"}
    )
    fragments = fragments.merge(assignment, on="POLY_ID", how="left")
    mapping = _plot_au(plots, fragments)
    tree = pd.read_csv(args.tree_clumps)
    tree = tree[(tree.spacing_m == 3.0) & (tree.min_dbh_cm == 10.0)].copy()
    tree = tree.rename(
        columns={
            "source_plot": "plot_id",
            "clump_4_10": "tree_clump_4_10",
            "clump_gt10": "tree_clump_gt10",
            "mean_clump_size": "tree_mean_clump_size",
        }
    )
    lidar = pd.read_csv(args.lidar).rename(columns={"plot_id": "plot_id"})
    lidar_clumps = pd.read_csv(args.lidar_clumps).rename(columns={"plot_id": "plot_id"})
    data = mapping.merge(lidar, on="plot_id", how="left")
    data = data.merge(
        lidar_clumps[
            [
                "plot_id",
                "detected_tree_tops",
                "clump_count",
                "clump_4_10_fraction",
                "max_clump_size",
            ]
        ],
        on="plot_id",
        how="left",
    )
    data = data.merge(
        tree[
            [
                "plot_id",
                "tree_clump_4_10",
                "tree_clump_gt10",
                "tree_mean_clump_size",
                "n_trees",
            ]
        ],
        on="plot_id",
        how="left",
    )
    data.to_csv(args.out_dir / "kc_marshal_plot_au.csv", index=False)
    structure = (
        data.groupby(["au_id", "hmz"], as_index=False)
        .agg(
            n_lidar_plots=("plot_id", "nunique"),
            lidar_area_ha=("plot_area_ha", "sum"),
            mean_height_m=("mean_height_m", "mean"),
            mean_cover_2m=("cover_2m", "mean"),
            mean_gap_2m=("gap_2m", "mean"),
            mean_lidar_clump_4_10_fraction=("clump_4_10_fraction", "mean"),
            mean_detected_tops=("detected_tree_tops", "mean"),
            n_tree_map_plots=("tree_clump_4_10", "count"),
            mean_tree_clump_4_10=("tree_clump_4_10", "mean"),
            mean_tree_clump_gt10=("tree_clump_gt10", "mean"),
            mean_tree_clump_size=("tree_mean_clump_size", "mean"),
            mean_tree_n=("n_trees", "mean"),
        )
        .reset_index()
    )
    tree_area = (
        data[data["tree_clump_4_10"].notna()]
        .groupby(["au_id", "hmz"], as_index=False)["plot_area_ha"]
        .sum()
        .rename(columns={"plot_area_ha": "tree_area_ha"})
    )
    structure = structure.merge(tree_area, on=["au_id", "hmz"], how="left")
    structure["tree_area_ha"] = structure["tree_area_ha"].fillna(0.0)
    structure["empirical_tree_map"] = structure["n_tree_map_plots"] > 0
    structure["structure_basis"] = structure["empirical_tree_map"].map(
        {True: "tree-map + LiDAR", False: "LiDAR only"}
    )
    structure.to_csv(args.out_dir / "kc_au_structure.csv", index=False)
    print(structure.to_string(index=False))


if __name__ == "__main__":
    main()
