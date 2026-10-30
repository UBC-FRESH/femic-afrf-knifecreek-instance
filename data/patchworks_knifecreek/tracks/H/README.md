# Knife Creek H matrix

Status: **scaffold with space-for-time feature curves; product curves remain 30 years.**

Generated from `ws4/dataset_kc_spatial_v3`, then feature curves were replaced by
nearest-neighbour IDF Cariboo space-for-time FVS-BC curves (87 site states).

## Tables

- 160 blocks
- 92 tracks
- 49 treatments
- 2,809 curve points
- 460 feature rows: 5 labels × 92 tracks
- 49 product rows
- 6 account rows
- space-for-time mapping: `space_for_time_mapping.csv`

Feature labels:

- `feature.habitat.basal_area`
- `feature.habitat.qmd`
- `feature.habitat.tph`
- `feature.habitat.canopy_ccf`
- `feature.yield.managed.total`

`ws4 ingest --matrix .../tracks/H --fragments .../fragments.csv` succeeds, and
`ws4 validate` passes.

## Horizon

- Feature curves: 0–50 years at 10-year steps.
- Product curves: existing 0–30 year GWM treatment runs.

The horizons differ. Do not present this as a 300-year matrix.

## Mapping

Each unique canonical track state is matched to one FAIB IDF space-for-time
site state by BA/QMD midpoint. The panel uses one first-measurement state per
site, not repeated visits. All HMZ variants of the same state share the same
feature curves. See `space_for_time_mapping.csv`.

## Limits

- Feature curves are regional space-for-time FVS-BC projections, not KC
  chronology and not a KC CFI.
- Product curves are still the original 30-year structural runs.
- No large-tree-BA feature is claimed from this panel.
- Accounts are minimal `_MANAGED_` rows; full product/feature account wiring is
  P3.4.
- No roads, patch accounts, pin or ForestModelXML.
- No clearcut treatment.
