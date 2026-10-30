# Knife Creek Patchworks-compatible package

Status: **fragment layer complete; H matrix has 50-year space-for-time feature curves; product accounts, roads, pin and ForestModelXML pending.**

P3.2 builds the spatial fragment layer that the later `tracks/H` matrix will join to.

## Contents

| File | Purpose |
| --- | --- |
| `spatial/fragments.shp` | 160 VRI blocks clipped to SUP S15382, EPSG:3005 |
| `fragments.csv` | Derived fragment attributes for matrix ingestion |
| `fragments_manifest.json` | Counts, source paths and caveats |

## Keys

- `RES_KEY` / `BLOCK` — stable block id, 1–160.
- `TRACK` — initial ws4 state track from `dataset_kc_spatial_v3`.
- `POLY_ID` — VRI polygon id.

## Attributes

- `AREA_HA`
- `F_AGE`
- `BEC`
- `CONTCLAS`
- `HMZ`
- `CLUMP`
- `RESERVE`

`F_AGE` is the VRI projected age, not a measured stand age. The PSP plots are
uneven-aged; do not treat `F_AGE` as a plot age.

## Built

- `tracks/H/` matrix: 160 blocks, 92 tracks, 49 treatments, 2,809 curve points
  and 460 feature rows; `ws4 ingest` and `ws4 validate` pass. Feature curves
  are 50-year regional space-for-time runs; product curves remain 30-year.

## Not built yet

- 300-year curves (features are 0–50 years; products 0–30 years)
- product and feature accounts
- topology
- roads
- `KC_H.pin`
- `ForestModelXML`
- ws4 ingest and validation

## Limits

- No absolute PSP plot centres or treatment polygons are included.
- Block order is inherited from `dataset_kc_spatial_v3`.
- ForestModelXML is blocked pending a valid schema/compiler; see
  `../../notes/reference/patchworks-forestmodelxml-format-spike.md`.
- No legal-compliance claim.
