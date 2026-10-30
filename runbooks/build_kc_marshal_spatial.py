#!/usr/bin/env python3
r"""Normalize the Marshal tree shapefiles and plot polygons.

Outputs live in the private DataLad store, not in the public model repo:

    external/ubc-research-forests-data/processed/kc_spatial/

The normalised tree table keeps source plot identity and flags byte-identical
duplicates (currently plot5 and plot6 duplicate plot2).

Usage::

    python runbooks/build_kc_marshal_spatial.py \
      --raw-dir \
      "external/ubc-research-forests-data/raw/ubc-research-forests-modelling-dropbox/992 Marshal" \
      --out-dir external/ubc-research-forests-data/processed/kc_spatial
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

SPECIES = {
    "FD": "FD",
    "FDI": "FD",
    "DF": "FD",
    "PL": "PL",
    "PLI": "PL",
    "SX": "SE",
    "SW": "SE",
    "SE": "SE",
    "EP": "EP",
    "AT": "AT",
    "W": "OH",
    "OH": "OH",
}
HEIGHT_COLUMNS = (
    "CALCHT_",
    "CALCHT",
    "CALC_HT",
    "MEAS_HT",
    "MEASHT",
    "CORRHT",
    "CORR_HT",
)
TREE_COLUMNS = ("TREE", "TREE_NO_")
SPECIES_COLUMNS = ("SP_", "SPECIES", "SPP_")


def _coalesce(frame: pd.DataFrame, names: tuple[str, ...]) -> pd.Series:
    """Return the first numeric column in the requested order."""
    result = pd.Series(np.nan, index=frame.index, dtype=float)
    for name in names:
        if name in frame.columns:
            values = pd.to_numeric(frame[name], errors="coerce")
            result = result.fillna(values)
    return result


def _text(frame: pd.DataFrame, names: tuple[str, ...]) -> pd.Series:
    """Return the first non-empty text column."""
    result = pd.Series("", index=frame.index, dtype=object)
    for name in names:
        if name in frame.columns:
            values = frame[name].astype(str).str.strip()
            result = result.where(result != "", values)
    return result


def _read_trees(path: Path, source_plot: int) -> gpd.GeoDataFrame:
    """Read and normalize one tree shapefile."""
    frame = gpd.read_file(path)
    if frame.crs is None:
        frame = frame.set_crs(26910)
    frame = frame.to_crs(26910)
    tree_id = _text(frame, TREE_COLUMNS)
    species_raw = _text(frame, SPECIES_COLUMNS).str.upper()
    species = species_raw.map(SPECIES).fillna("OH")
    dbh = pd.to_numeric(frame.get("DBH"), errors="coerce")
    height = _coalesce(frame, HEIGHT_COLUMNS)
    cw1 = _coalesce(frame, ("CW1",))
    cw2 = _coalesce(frame, ("CW2", "CW2__"))
    crown_width = pd.concat([cw1, cw2], axis=1).mean(axis=1, skipna=True)
    lc = _coalesce(frame, ("LCHT1",))
    for name in ("LCHT2", "LCHT3", "LCHT4"):
        lc = pd.concat([lc, _coalesce(frame, (name,))], axis=1).mean(axis=1, skipna=True)
    crown_ratio = np.where((height > 0) & lc.notna(), (height - lc) / height, np.nan)
    crown_ratio = np.clip(crown_ratio, 0.0, 1.0)
    out = gpd.GeoDataFrame(
        {
            "source_plot": source_plot,
            "tree_id": tree_id,
            "species": species,
            "dbh_cm": dbh,
            "height_m": height,
            "crown_width_m": crown_width,
            "live_crown_base_m": lc,
            "crown_ratio": crown_ratio,
            "vigor": _coalesce(frame, ("VIGOR",)),
            "comments": _text(frame, ("COMMENTS",)),
            "utm_e": frame.geometry.x,
            "utm_n": frame.geometry.y,
            "geometry": frame.geometry,
        },
        crs=frame.crs,
    )
    out["tree_id"] = out["tree_id"].replace({"": None})
    out["fingerprint"] = out.apply(
        lambda row: hashlib.sha256(
            (
                f"{row['tree_id']}|{row['species']}|{row['dbh_cm']}|"
                f"{row['height_m']}|{row['crown_width_m']}"
            ).encode()
        ).hexdigest(),
        axis=1,
    )
    return out


def main() -> None:
    """Build the normalized tree and plot tables."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    tree_paths = sorted(args.raw_dir.glob("plot[0-9].shp"))
    if not tree_paths:
        raise ValueError(f"no tree shapefiles in {args.raw_dir}")
    frames = []
    for path in tree_paths:
        source_plot = int(path.stem.removeprefix("plot"))
        frames.append(_read_trees(path, source_plot))
    trees = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs="EPSG:26910")
    # Mark exact duplicate source tables by their normalized fingerprint set.
    signatures = {}
    for source, group in trees.groupby("source_plot"):
        signature = hashlib.sha256(
            "".join(sorted(group["fingerprint"].dropna().unique())).encode()
        ).hexdigest()
        signatures[int(source)] = signature
    canonical = {}
    by_signature = {}
    for source in sorted(signatures):
        signature = signatures[source]
        canonical[source] = by_signature.setdefault(signature, source)
    trees["duplicate_of"] = trees["source_plot"].map(canonical)
    trees["is_duplicate"] = trees["source_plot"] != trees["duplicate_of"]
    trees = trees.drop(columns="fingerprint")

    trees_path = args.out_dir / "kc_marshal_trees.gpkg"
    trees.to_file(trees_path, layer="trees", driver="GPKG")
    trees.drop(columns="geometry").to_parquet(
        args.out_dir / "kc_marshal_trees.parquet", index=False
    )

    plots = gpd.read_file(args.raw_dir / "plots_polys.shp")
    plots = plots.to_crs(26910)
    plots["area_ha"] = plots.geometry.area / 10000.0
    centroids = plots.geometry.centroid
    plots["centroid_e"] = centroids.x
    plots["centroid_n"] = centroids.y
    bounds = plots.geometry.bounds
    plots = plots.assign(
        min_e=bounds["minx"],
        min_n=bounds["miny"],
        max_e=bounds["maxx"],
        max_n=bounds["maxy"],
    )
    plots.to_file(args.out_dir / "kc_marshal_plots.gpkg", layer="plots", driver="GPKG")
    plots.drop(columns="geometry").to_csv(args.out_dir / "kc_marshal_plots.csv", index=False)

    summary = (
        trees.groupby("source_plot")
        .agg(
            n_trees=("tree_id", "size"),
            dbh_min_cm=("dbh_cm", "min"),
            dbh_median_cm=("dbh_cm", "median"),
            dbh_max_cm=("dbh_cm", "max"),
            height_median_m=("height_m", "median"),
            crown_width_median_m=("crown_width_m", "median"),
            duplicate_of=("duplicate_of", "first"),
        )
        .reset_index()
    )
    summary.to_csv(args.out_dir / "kc_marshal_tree_summary.csv", index=False)
    print(summary.to_string(index=False))
    print(f"trees={len(trees)} plots={len(plots)} -> {args.out_dir}")


if __name__ == "__main__":
    main()
