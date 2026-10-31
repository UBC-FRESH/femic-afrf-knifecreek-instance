# UBC Research Forests OneDrive inventory and AFMF fit

Status: acquired and profiled. The payload is in the private DataLad submodule
`external/ubc-research-forests-data`. It is not part of the public model
release.

## Acquisition result

- 589 files, 39.8 GB.
- Source: UBC Research Forests modelling dropbox, private OneDrive share.
- The aggregate folder download was truncated at 19 GB; the missing LiDAR
  package was recovered separately from `LiDAR/KC_2019/ubc_kc_2019.zip`.
- DataLad store: `UBC-FRESH/ubc-research-forests-data`.
- Submodule path: `external/ubc-research-forests-data`.
- DataLad commit: `4930d13` (526 annex keys, 39.83 GB in working tree).
- Inventory: `metadata/ubc-research-forests-inventory.csv`.
- Summary: `metadata/ubc-research-forests-summary.json`.

## What is in the payload

### `992 Marshal/`

- 8 tree-level plot shapefiles (`plot1.shp` … `plot8.shp`), EPSG:26910.
- 24 plot polygons (`plots_polys.shp`).
- Tree attributes include DBH, height, crown widths, live-crown heights,
  vigour, damage, bearing/distance and UTM coordinates.
- Tree counts range from 115 to 614 per mapped plot; DBH roughly 0–51 cm.
- `plot5` and `plot6` are byte-level duplicates of `plot2`; treat them as one
  source until the archive owner confirms otherwise.

### `KozakTaper_Version6/`

- R implementation of the Kozak (2004) taper and merchantable-volume system:
  `Kozak_Parameters.R`, `Diameter_Inside_Bark.R`, `ProjectHeight.R`,
  `LocateMerchHeight.R`, `LogVolume.R`, `Compute_Statistics.R`.
- Two reference PDFs.
- `vri_c_trees.csv`: 38,967 provincial VRI trees, 2,379 in BGC zone IDF.
  This is a coefficient/test sample, not a Knife Creek inventory.

### `LiDAR/`

| Product | Content | Size | Use |
| --- | --- | ---: | --- |
| `2009/` | 308 FUSION `LIDARBIN` tiles + `.lasx` + `AFRF_2009.lasd` | 15 GB | Legacy pre-treatment structure; needs conversion to LAS |
| `2013/` | 63 standard LAS tiles, 363.8M points | 9.5 GB | Pre-treatment canopy/structure and change detection |
| `KC_2019/` | 1 m BC DEM tiles, UBC canopy/forest-floor/hillshade grids, CHM ZIP | 8.9 GB | Current canopy, openings, clumps, terrain |
| `BC_LiDAR_Campbell_Rd/` | 2024 LAZ tile, 71.9M points | 404 MB | Adjacent-area check; verify overlap before use |

The 2019 `bc_093a001/002_xli1m...tif` files are 1 m **elevation/DEM**
surfaces, not canopy height. The ArcInfo `ubc_chm` grid is the canopy-height
product after masking its integer sentinel. `UBC_CHM.tif` has band description
`UBC_FF` and should not be treated as CHM without checking with the data owner.

## How it feeds the AFMF/ws4 pipeline

### 1. Plot data → calibration, validation and spatial structure

- The 2024 Excel remeasurement is already ingested and used for calibration,
  temporal validation and retention.
- The Marshal shapefiles add **tree positions and crown dimensions** for
  eight plots. Use them to:
  - calibrate LiDAR individual-tree/clump detection;
  - test 4–10-tree interlocking-crown clump geometry;
  - test canopy-opening sizes and crown closure;
  - validate reserve-tree selection.
- The 24 plot polygons give georeferenced footprints for joining to
  VRI/HMZ/AU and LiDAR.

### 2. LiDAR → spatial legal constraints

- 2019 CHM/DEM → canopy height, cover, gaps, clump candidates, opening sizes.
- 2013 LAS → pre-treatment structure and change; compare with 2019.
- 2009 legacy → historical structure if converted; not a blocker for the
  current model.
- Derive per-AU/HMZ:
  - 4–10-tree clump count and closure;
  - 2–5-tree max-diameter subgroup;
  - canopy opening size distribution, 0.3–1.0 tree heights, mean 0.5;
  - residual canopy cover and retention.

These become the spatial accounts currently missing from the stage graph.

### 3. Kozak taper → merchantable volume and AAC

- Port the R taper/height/merch-volume functions to Python.
- Compute species-specific merchantable volume and merchantable height from
  DBH/height.
- Replace or cross-check the generic volume coefficients in the AU curves.
- Use the provincial VRI tree list only to test the port; do not treat it as KC
  inventory.

### 4. Stage graph and estate model

- Add LiDAR-derived spatial features to the AU/HMZ stage graph.
- Add Kozak-based product curves for sawlog/pulp/merchantable volume.
- Keep the existing structural targets and the v1/v2c growth ensemble.
- Optimize 20 periods for even-flow volume/AAC subject to:
  - 90% final stock;
  - legal BA, large-tree BA, max DBH, q, reserve;
  - retention;
  - spatial clump/opening feasibility.

## Pipeline start: normalized spatial products

The first pipeline step is built in the private store under
`processed/kc_spatial/`:

- `kc_marshal_trees.gpkg` / `.parquet` — 2,032 tree records from eight source
  plots. Plot5 and plot6 are flagged as duplicates of plot2 based on identical
  tree attributes; the source plot identity is retained.
- `kc_marshal_plots.gpkg` / `.csv` — 24 plot polygons with area, centroid and
  bounds.
- `kc_marshal_tree_summary.csv` — per-source-plot tree summaries.
- `kc_marshal_lidar_structure.csv` — 2019 canopy metrics inside the 24 plots:
  mean height 6.5–11.9 m, cover ≥2 m 72–94%, gap fraction <2 m 6–28%.

This confirms the LiDAR and plot datasets line up spatially and gives the first
AU/plot structural table. It is not yet a legal clump/opening classification.

The Kozak taper package is now wired to the normalized tree table. Merchantable
volume across the eight mapped plots is about **100.9 m³/ha** (range 52.8–121.9),
with whole-stem volume about 125 m³/ha. These are plot-map volumes, not an
inventory estimate.

The first 2019-CHM clump proxy detects 28–55 tree tops per plot and mostly
1–3-tree groups; it does not reproduce 4–10-tree interlocking-crown clumps. This
is a calibration signal, not a finding that the stand fails the legal rule.

The empirical tree-map baseline is stronger: at 3 m spacing and DBH >=10 cm,
the eight mapped plots contain 6, 5, 1, 2, 5, 5, 3 and 4 legal 4–10-tree groups,
plus larger merged groups. Legal clumps do exist in the measured stands; the
LiDAR proxy needs calibration, not rejection.

The 2019 CHM local-maxima calibration against DBH >=15 cm trees reaches a mean
F1 of 0.67 (window 3, minimum height 3 m, NMS 1.5 m; 69 detected tops vs 56.5
observed). The 2013 LAS calibration reaches F1 0.656 (63.75 detected tops vs
56.5 observed). Neither LiDAR layer reproduces the tree-map clump counts well
enough to be a legal clump detector. The eight tree maps remain the empirical
clump baseline; LiDAR is the canopy/cover/gap layer, not the legal clump
arbiter.

## AU/HMZ structure and volume basis

The plot-to-AU map shows that all eight tree-map plots fall in
`KC_IDFdk3_FDI_L / L`. The 24 LiDAR plots cover only four groups:

- `KC_IDFdk3_FDI_H / M`
- `KC_IDFdk3_FDI_L / L` (tree-map group)
- `KC_IDFdk3_FDI_L / M`
- `KC_IDFdk3_FDI_M / M`

The structure table is therefore explicitly hybrid: tree-map clumps for the
L/L group, LiDAR cover/gap for all four groups, and LiDAR-only flags elsewhere.

Kozak volume on the initial FVS AU tree lists gives merchantable/total-stem
ratios of **0.76–0.83** and whole-stem/total-stem ratios of **1.01–1.05** by AU.
Those factors are now applied to the split-block product curves:

- recipe: `data/kc_ws4_recipe_au_stages_split_volume/`
- dataset: `ws4/dataset_kc_au_stages_split_volume_v1/`
- factors: 0.7595–0.8274 by AU

The volume-adjusted dataset builds and validates. It is the production model
candidate; the unadjusted split model remains the comparison.

## Immediate next steps

1. Calibrate 2019 LiDAR tree detection against the eight Marshal tree maps and
   2013 LAS; replace the naive CHM local-maxima clump proxy.
2. Build the spatial clump/opening accounts from the calibrated LiDAR layer.
3. Add those accounts to the stage graph.
4. Rerun the AAC/estate model with Kozak volumes and the v1/v2c ensemble.

## Caveats

- The 2009 `.las` files are FUSION `LIDARBIN`, not standard LAS.
- `UBC_CHM.tif` naming/semantics are ambiguous.
- Only eight tree-level plot shapefiles are present; the 24 Excel plots are the
  measurement network.
- The Kozak VRI sample is provincial, not KC-specific.
- The 2024 Campbell Road LAZ tile may be outside the KC block.
- The raw payload remains private; derived tables and metadata only may be
  published.

## Related

- Login procedure:
  `https://github.com/UBC-FRESH/lab-knowledge/wiki/UBC-OneDrive-login-from-Linux`
- DataLad pattern:
  `https://github.com/UBC-FRESH/lab-knowledge/wiki/Managing-research-datasets-with-DataLad`
