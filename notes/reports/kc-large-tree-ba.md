# KC large-tree BA extraction

Status: extracted for the AU no-cut and multi-entry curve sets, and wired into
the compiled stage graph.

## What was added

`data/psp/kc_au_200y/kc_au_yield_200y.csv` now carries:

- `large_ba_m2_ha` — live-tree BA for DBH >= 37.5 cm
- `large_tph` — live trees >= 37.5 cm

The values come from the FVS tree-list output, requested at each 10-year cycle.

## Result

- 6 AUs
- 126 curve rows
- 0–200 years
- large-tree BA at year 200: 46.5–64.5 m²/ha depending on AU

## Compiled model

`ws4/dataset_kc_au_stages_v1` now includes
`feature.habitat.large_tree_ba` for natural and managed stages.

- 115 tracks
- 115 feature rows for each feature label
- `ws4 validate` passes

## Reserve BA

Reserve BA is now added with the existing non-spatial clump-reserve proxy:

- group large trees into DBH-ranked chunks of six;
- reserve the largest three above the regime D target;
- follow those TreeIds through the post-entry tree lists.

`feature.habitat.reserve_ba` is present for all 115 stage tracks. This is a
structural proxy, not the legal spatial 4–10-tree clump rule.

No KC calibration or legal-compliance claim.
