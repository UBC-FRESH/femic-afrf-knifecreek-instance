# KC model of record

Status: **frozen model candidate**. Not a legal-compliance determination.

## Model of record

- Dataset: `ws4/dataset_kc_au_stages_split_volume_v1`
- Compiled at: `8742221` (split/volume layer; update if the dataset commit changes)
- 211 split blocks, maximum block 39.94 ha, 3,481.77 ha total
- 115 tracks, 102 treatments, six entry stages per AU/HMZ
- Product curves use the Kozak merchantable/FVS total-stem ratio by AU
  (0.7595–0.8274)
- Topology: `ws4/topology_split.csv`
- Watcher preset: `MODEL=split_volume`

The unadjusted split-block dataset
(`ws4/dataset_kc_au_stages_split_v1`) remains the volume-basis comparison.

## Growth basis

No single calibrated model is adopted as universal truth.

- **Uncalibrated FVS-BC** — structural baseline.
- **v1 Marshall calibration** — local KC calibration, fitted to 2013.
- **v2c FAIB calibration** — regional IDF calibration.

Validation evidence:

| Test | Uncalibrated | v1 Marshall | v2c FAIB |
| --- | ---: | ---: | ---: |
| FAIB 92-site BA bias | +5.16 | +4.93 | −0.21 |
| FAIB 92-site TPH bias | +380 | +134 | −6 |
| Marshall 2024 BA bias | +0.83 | +1.33 | −2.59 |
| Marshall 2024 TPH bias | +201 | +24 | −71 |

The production uncertainty envelope is the spread across these three growth
bases. The uncalibrated model is the structural default; v1 and v2c are the
local and regional sensitivities.

## Volume basis

- Kozak 2004 taper/merchantable-volume package, applied to the initial FVS AU
  tree lists.
- Merchantable/FVS total-stem ratio: **0.7595–0.8274** by AU.
- Whole-stem/FVS ratio: **1.0149–1.0495**.
- Applied to the split-block product curves in the model of record.

## Structural basis

- Empirical clump baseline: eight Marshal tree maps, 3 m spacing, DBH ≥10 cm.
  Legal 4–10-tree group counts: 6, 5, 1, 2, 5, 5, 3 and 4 by plot.
- 2019 CHM canopy/cover/gap metrics for all 24 plots.
- 2013 LAS and 2019 CHM tree detection both plateau at F1 ≈0.66–0.67 against
  DBH ≥15 cm trees. LiDAR is not used as the legal clump arbiter.
- The eight tree maps cover only `KC_IDFdk3_FDI_L / L`; other AU/HMZ groups are
  LiDAR-only and flagged in `kc_au_structure.csv`.

## Validation and structural targets

- Uncalibrated legal-candidate structural targets: **55/55**.
- v1 calibrated sensitivity: **51/55**; remaining misses are q-factor.
- No spatial clump/opening or pre-2026 retention claim is made.
- The AAC runs are diagnostics; scenario tuning belongs downstream.

## Legal status

- GWM 2007, Knife Creek U-5-002 `dwl_50`.
- HMZ matrix: 1 M, 2 L, 3 M, 4 M, 5 A.
- Public HMZ layer verified from the BC Map Hub source and clipped to SUP
  S15382.
- **Current approved order and legal stand-structure map still require
  external verification.** Do not claim legal compliance.

## Uncertainty and limits

- FVS-BC is not KC-calibrated for all species/structures; the ensemble is
  diagnostic.
- The v1/v2c calibrations are same-plot/regional, not independent-site
  validation.
- The spatial clump/opening layer is hybrid and incomplete; LiDAR detection is
  weak.
- Kozak volume is applied by AU-level ratio, not tree-by-tree in the model.
- The split-block geometry is a grid split of large VRI polygons, not a surveyed
  harvest-unit layout.
- The model is not a statutory AAC.

## Freeze rule

Any change to growth, volume basis, block geometry, spatial structure, or legal
inputs requires a new dataset version and a new validation record. Do not
silently replace the model of record.

## Reproduce

```bash
# build split blocks
python runbooks/split_kc_large_blocks.py \
  --fragments data/patchworks_knifecreek/spatial/fragments.shp \
  --out-dir data/patchworks_knifecreek/spatial_split \
  --max-ha 40 \
  --schedule-in ws4/runtime/kc_au_stages/selection_gwm_legal.csv \
  --schedule-out data/kc_ws4_recipe_au_stages_split/selection_gwm_legal.csv

# topology
python runbooks/build_kc_topology.py \
  --fragments data/patchworks_knifecreek/spatial_split/fragments.shp \
  --out-dir data/patchworks_knifecreek/spatial_split \
  --ws4-out ws4/topology_split.csv --search-distance 100

# volume-adjusted recipe and dataset
python runbooks/build_kc_au_stage_recipe.py \
  --au-table data/kc_au/kc_au_table.csv \
  --assignment data/kc_au/kc_au_assignment.csv \
  --fragments data/patchworks_knifecreek/spatial_split/fragments.csv \
  --no-cut data/psp/kc_au_200y/kc_au_yield_200y.csv \
  --multi-low data/psp/kc_au_200y/kc_au_multientry_low_200y.csv \
  --multi-moderate data/psp/kc_au_200y/kc_au_multientry_moderate_200y.csv \
  --volume-basis external/ubc-research-forests-data/processed/kc_spatial/kc_volume_basis_au.csv \
  --out-dir data/kc_ws4_recipe_au_stages_split_volume

ws4 build \
  --xml data/kc_ws4_recipe_au_stages_split_volume/forestmodel.xml \
  --fragments data/kc_ws4_recipe_au_stages_split_volume/fragments.csv \
  --out ws4/dataset_kc_au_stages_split_volume_v1
```
