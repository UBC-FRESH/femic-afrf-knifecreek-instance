#!/usr/bin/env python3
"""Build the KC AU layer from BEC, leading species and SI quantiles.

Workflow adapted from the FEMIC stage-00/01a contract:

1. stratify the VRI by BEC variant + leading species;
2. keep the top-area strata covering 95% of the forested area;
3. alias sparse strata to the same-BEC dominant stratum;
4. split each selected stratum into L/M/H by the standard 30-point SI
   quantile bands (5-35, 35-65, 65-95);
5. write the static/matched AU assignment and the AU table.

Usage::

    python runbooks/build_kc_au_table.py \
      --vri data/inventory/vri_2025_kc.gpkg \
      --out-dir data/kc_au
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
from femic.pipeline.tsa import assign_si_levels_from_stratum_quantiles

SI_LEVELQUANTS = {"L": [5, 20, 35], "M": [35, 50, 65], "H": [65, 80, 95]}
COVERAGE_TARGET = 0.95


def main() -> None:
    """Write the AU table, polygon assignment and manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vri", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    vri = gpd.read_file(args.vri).to_crs(3005)
    vri["area_ha"] = vri.geometry.area / 10000.0
    forest = vri[
        vri["SITE_INDEX"].notna()
        & vri["SPECIES_CD_1"].notna()
        & (vri["BASAL_AREA"].fillna(0) > 0)
        & (vri["VRI_LIVE_STEMS_PER_HA"].fillna(0) > 0)
    ].copy()
    if forest.empty:
        raise ValueError("no forested VRI polygons with a site index")
    forest["bec"] = (
        forest["BEC_ZONE_CODE"].fillna("").astype(str)
        + forest["BEC_SUBZONE"].fillna("").astype(str)
        + forest["BEC_VARIANT"].fillna("").astype(str)
    )
    forest["leading_species"] = forest["SPECIES_CD_1"].astype(str).str.upper()
    forest["stratum_static"] = forest["bec"] + "__" + forest["leading_species"]

    # Top-area coverage selection, then same-BEC dominant-species remap.
    area_by_stratum = forest.groupby("stratum_static")["area_ha"].sum().sort_values(ascending=False)
    cumulative = area_by_stratum.cumsum() / area_by_stratum.sum()
    selected = list(area_by_stratum.index[cumulative <= COVERAGE_TARGET])
    if not selected:
        selected = [str(area_by_stratum.index[0])]
    if cumulative.iloc[len(selected) - 1] < COVERAGE_TARGET:
        selected.append(str(area_by_stratum.index[len(selected)]))

    # Same-BEC dominant species target for sparse strata.
    target_by_bec: dict[str, str] = {}
    for stratum in selected:
        bec, _species = stratum.split("__", 1)
        target_by_bec.setdefault(bec, stratum)
    forest["stratum_matched"] = [
        stratum
        if stratum in selected
        else target_by_bec.get(stratum.split("__", 1)[0], selected[0])
        for stratum in forest["stratum_static"]
    ]

    assigned, _stats = assign_si_levels_from_stratum_quantiles(
        f_table=forest,
        si_levelquants=SI_LEVELQUANTS,
        stratum_matched_col="stratum_matched",
        site_index_col="SITE_INDEX",
        message_fn=lambda *_args: None,
    )
    if assigned["si_level"].isna().any():
        missing = int(assigned["si_level"].isna().sum())
        raise ValueError(f"{missing} polygons did not receive an SI level")
    assigned["au_id"] = (
        "KC_"
        + assigned["stratum_matched"].str.replace("__", "_", regex=False)
        + "_"
        + assigned["si_level"].astype(str)
    )

    au_table = (
        assigned.groupby("au_id")
        .agg(
            stratum_matched=("stratum_matched", "first"),
            si_level=("si_level", "first"),
            bec=("bec", "first"),
            stands=("POLYGON_ID", "size"),
            area_ha=("area_ha", "sum"),
            site_index_min=("SITE_INDEX", "min"),
            site_index_median=("SITE_INDEX", "median"),
            site_index_max=("SITE_INDEX", "max"),
        )
        .reset_index()
        .sort_values("au_id")
    )
    au_table["leading_species"] = au_table["stratum_matched"].str.split("__").str[1]
    assignment_columns = [
        "POLYGON_ID",
        "FEATURE_ID",
        "bec",
        "leading_species",
        "SITE_INDEX",
        "area_ha",
        "stratum_static",
        "stratum_matched",
        "si_level",
        "au_id",
    ]
    assignment = assigned[assignment_columns].copy()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    au_table.to_csv(args.out_dir / "kc_au_table.csv", index=False)
    assignment.to_csv(args.out_dir / "kc_au_assignment.csv", index=False)

    manifest = {
        "source_vri": str(args.vri),
        "strata": int(forest["stratum_static"].nunique()),
        "selected_strata": selected,
        "strata_remapped": sorted(set(forest["stratum_static"]) - set(selected)),
        "si_level_quantiles": SI_LEVELQUANTS,
        "coverage_target": COVERAGE_TARGET,
        "selected_area_fraction": float(
            area_by_stratum.loc[selected].sum() / area_by_stratum.sum()
        ),
        "aus": len(au_table),
        "polygons": len(assignment),
        "area_ha": float(assignment["area_ha"].sum()),
        "caveats": [
            "BEC is the variant-level code (zone + subzone + variant).",
            "Sparse leading-species strata are remapped to the dominant same-BEC stratum.",
            "The 5-35 / 35-65 / 65-95 bands are the FEMIC 30-point SI quantile policy.",
            "This is an AU definition, not a yield calibration.",
        ],
    }
    (args.out_dir / "kc_au_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
