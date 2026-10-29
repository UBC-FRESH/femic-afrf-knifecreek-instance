#!/usr/bin/env python3
"""Summarize VRI age and site index for the Knife Creek instance.

The VRI is polygon-level. This summary is a stand-level prior for the PSP
backtests; it is not a plot-level join, because the PSP workbook has no
absolute plot centres.

Usage::

    python runbooks/summarize_vri_age_site.py \
      --vri data/inventory/vri_2025_kc.gpkg \
      --out data/inventory/vri_2025_kc_age_site_summary.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

TARGET_YEAR = 1993
PROJECTED_YEAR = 2025


def _weighted_quantile(values: pd.Series, weights: pd.Series, q: float) -> float:
    """Weighted quantile with a cumulative-weight interpolation-free definition."""
    order = np.argsort(values.to_numpy())
    x = values.to_numpy()[order]
    w = weights.to_numpy()[order]
    cumulative = np.cumsum(w) / w.sum()
    return float(x[np.searchsorted(cumulative, q)])


def _summary(frame: pd.DataFrame, label: str) -> dict[str, object]:
    """Return area-weighted and unweighted age/site-index summaries."""
    valid = frame.dropna(subset=["PROJ_AGE_1", "SITE_INDEX"]).copy()
    age = valid["PROJ_AGE_1"]
    site = valid["SITE_INDEX"]
    age_1993 = age - (PROJECTED_YEAR - TARGET_YEAR)
    weights = valid["POLYGON_AREA"]
    return {
        "label": label,
        "polygons": len(valid),
        "area_ha": float(weights.sum()),
        "age_2025_mean": float(age.mean()),
        "age_2025_median": float(age.median()),
        "age_2025_area_weighted_median": _weighted_quantile(age, weights, 0.5),
        "age_1993_area_weighted_median": _weighted_quantile(age_1993, weights, 0.5),
        "site_index_mean_m": float(site.mean()),
        "site_index_median_m": float(site.median()),
        "site_index_area_weighted_median_m": _weighted_quantile(site, weights, 0.5),
        "site_index_min_m": float(site.min()),
        "site_index_max_m": float(site.max()),
    }


def main() -> None:
    """Read the VRI and write the stand-level age/site summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vri", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    vri = gpd.read_file(args.vri)
    fdi = vri[vri["SPECIES_CD_1"] == "FDI"]
    payload = {
        "source": "VRI 2025 R1, Knife Creek",
        "source_path": str(args.vri),
        "target_year": TARGET_YEAR,
        "projected_year": PROJECTED_YEAR,
        "note": (
            "Polygon-level VRI prior only. The PSP workbook has no absolute "
            "plot centres, so these values are not a plot-level join."
        ),
        "all_forest": _summary(vri, "all_forest"),
        "fdi_leading": _summary(fdi, "fdi_leading"),
        "fvs_bc": {
            "site_index_note": (
                "FVS-BC prints 'SITE INDEX IS NOT USED IN THIS VARIANT'; "
                "the value is metadata only."
            ),
            "age_note": (
                "STDINFO age was tested at 64 and 91; it did not change the FVS-BC backtest."
            ),
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload["fdi_leading"], indent=2))


if __name__ == "__main__":
    main()
