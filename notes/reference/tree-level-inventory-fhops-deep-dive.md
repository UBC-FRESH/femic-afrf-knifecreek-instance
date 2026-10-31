# Tree-level inventory, FHOPS, and creative silviculture: deep dive

Date: 2026-10-31
Status: evidence and integration design

## Bottom line

- Knife Creek has a processed 2024 canopy tree inventory and calibrated 2013/2019
  LiDAR; Gavin Lake has only **partial 2013 LAS** coverage over about 339 ha of
  5,664 ha. The 2009 FUSION LIDARBIN is not readable by the current pipeline.
- The Gavin 2025 VRI starting layer is built, but the compiled legacy matrix
  still uses `AGE_2019`. The area-weighted 2025 VRI age is 125.3 years vs 99.4
  years for the legacy ages advanced to 2025. A real rebuild is required.
- FHOPS has a validated tree-inventory contract, reference stem/bucking, classic
  regression productivity and costing, single-machine tree simulation, and
  schedule-coupled tree replay. It does **not** contain a multi-machine 4D
  digital-twin package called "tree lab" in this checkout.
- The LiDAR canopy tree density is too low for the Lahrsen feller-buncher
  observed range (mean 78 TPH vs 205-3,044 TPH). LiDAR canopy trees are not
  total stems. Use VRI/PSP total density for classic productivity and LiDAR for
  piece-size/crown/clump structure.

## LiDAR coverage audit

`runbooks/audit_afrf_lidar_coverage.py` checked every standard LAS/LAZ and
GeoTIFF product in the OneDrive payload.

| Block | Readable files intersecting | Overlap (double-counted) | Coverage |
| --- | ---: | ---: | --- |
| Knife Creek | 56 | 19,023 ha | 2013 LAS, 2019 rasters, 2024 tiles |
| Gavin Lake | 11 | 448 ha | 2013 LAS only; about 339 ha after clipping |

The 2013 LAS files carry no CRS and are assumed EPSG:26910. The 2009 files are
FUSION LIDARBIN; the current LAS/raster pipeline cannot read them. There are no
2019 or 2024 Gavin tiles in the payload.

## Tree-level inventories

### Knife Creek

- `data/lidar/kc_2024/trees.parquet`: 278,318 canopy trees.
- 2013 LAS calibrated against the eight measured tree maps: mean F1 0.656.
- 2019 CHM calibration: mean F1 0.667.
- 211-block piece-size table:
  `data/lidar/kc_2024/block_piece_size.csv`.
- Mean block values: 78 TPH, 0.62 m3/stem, 48 m3/ha, QMD 27 cm.

A FHOPS pilot inventory for block 78 is
`data/lidar/kc_2024/fhops/kc_0078/`. `fhops tree inventory validate` accepts it
(245 trees, one species, valid contract).

### Gavin Lake

- `data/lidar/gavin_2013/trees.gpkg`: 166,188 canopy trees in 11 2013 tiles.
- 339 ha covered; partial block coverage only.
- 111 fragments have tree summaries:
  `data/lidar/gavin_2013/block_piece_size.csv`.
- Mean covered-fragment values: 464 TPH, 0.98 m3/stem, 400 m3/ha.
- A FHOPS pilot inventory for fragment 323 is
  `data/lidar/gavin_2013/fhops/gl_0323/`. `fhops tree inventory validate`
  accepts it (1,814 trees, one species, valid contract).
- The 464 TPH and 400 m3/ha values are high for a canopy-only detection; treat
  the partial inventory as screening evidence, not a CFI.

## Gavin 2025 VRI starting layer

`runbooks/build_gavin_vri_start.py` writes:

- `data/inventory/gavin_vri_2025_start.csv`
- `data/inventory/gavin_vri_2025_start.gpkg`
- `data/inventory/gavin_vri_2025_start_summary.json`

Area-weighted summary:

| Item | Value |
| --- | ---: |
| Fragments | 2,907 |
| Area | 5,663.7 ha |
| 2025 VRI age | 125.3 years |
| Legacy age advanced to 2025 | 99.4 years |
| Difference | +25.9 years |
| Fragments differing by more than 20 years | 1,606 |

Area-weighted species shares: FD 42.2%, SX 23.0%, FDI 8.7%, CW 7.5%, AT 5.9%,
BL 4.5%, PL 3.5%, EP 1.9%, PLI 1.5%, AC 1.1%, ACT 0.3%.

This is the rebuild input. It is not yet applied to `ws4/runtime/legacy_matrix`,
because the legacy matrix's tracks and curves are keyed to the old `AGE_2019`
states.

## FHOPS capability audit

### Classic regression productivity and costing

FHOPS exposes:

- `fhops dataset estimate-productivity` for Lahrsen feller-buncher, forwarder,
  CTL harvester, grapple skidder, grapple yarder, roadside processor, loader,
  shovel logger, and helicopter longline.
- `fhops dataset estimate-cost` for machine rates, utilisation, and $/m3.
- Published machine-rate, repair, and productivity reference tables.

This is the correct path for block-level classic productivity. It needs mean
stem size, volume/ha, stem density, and slope. For Knife Creek, LiDAR supplies
piece size and height; VRI/PSP must supply total stem density.

### Tree-scale simulation

FHOPS has:

- `fhops.tree.inventory.v1` contract, validation, pinning, and block mapping;
- reference stem volume and log bucking (`fhops tree stems`);
- single-machine spatial simulation (`fhops tree simulate`) with reach, travel,
  slope, obstacles, and nearest/strip/TSP patterns;
- schedule replay (`fhops tree replay`) and glTF/GLB tree-scene export.

These are deterministic reference execution layers, not a calibrated
multi-machine 4D process simulation.

### LiDAR operability

`fhops/scenario/lidar_operability.py` consumes FEMIC/WS4 terrain and canopy
support, classifies ground/cable/helicopter terrain, checks the current system,
and reports advisory move-in, landing, and road multipliers. It does not
silently rewrite systems or apply financial multipliers.

### The missing "tree lab" 4D layer

No `tree lab`, `treelab`, or digital-twin package was found in the workspace or
the UBC-FRESH GitHub organisation. The closest available tools are FHOPS
`tree simulate`, `tree replay`, and tree-scene export. If the new tree-lab
package exists on an unshared branch or private repository, it needs to be
provided before it can be integrated.

## Integration design

### 1. Producer layer

- Knife Creek: 2024 LiDAR trees + eight measured tree maps; species unknown;
  DBH height-allometry; crown radius available.
- Gavin Lake: partial 2013 LiDAR trees + 2025 VRI; species from VRI; total
  density from VRI/PSP.
- Both: FHOPS tree-inventory contract with review status `not_reviewed` until a
  field reviewer signs off.

### 2. Block-level classic productivity

For each block and candidate system:

- mean stem size from the tree list or LiDAR piece-size table;
- volume/ha from the growth model or LiDAR/PSP;
- stem density from VRI/PSP total stems, not canopy-only LiDAR;
- slope from the DEM;
- system from the harvest-system screen.

Then call FHOPS productivity/costing. Output a block/system $/m3 table and a
sensitivity range.

### 3. Bottom-up tree process

Pin the block tree inventory in a FHOPS scenario, then run:

- `fhops tree stems` for reference volume and bucking;
- `fhops tree simulate` for single-machine path/travel/processing time;
- `fhops tree replay` for a schedule-coupled tree consumption test;
- tree-scene export for a 3D review.

This is the maximum tree-level detail available today. The 4D multi-machine
layer is not present.

### 4. Fresh-FVSBC creative silviculture for Gavin Lake

The legacy Cosmin Man GL matrix is an 80-year clearcut model. To capture
commercial thinning, fuel mitigation, irregular selection, shelterwood, and
variable retention:

- build species-resolved tree lists for the GL AUs from the 2025 VRI plus a
  regional SBSdw1/ICHmk3 PSP analog;
- define treatment keys and cut lists for each prescription;
- run FVS-BC with post-treatment growth;
- compile the resulting curves and transitions into a new ws4 state graph;
- keep the legacy matrix as a benchmark, not the production basis.

This is a new state library, not an age-column edit.

## What can be done now

- KC classic productivity table from `block_piece_size.csv` and VRI density.
- KC FHOPS tree-inventory pilot (block 78 validated).
- Gavin partial FHOPS tree-inventory pilot (fragment 323 validated).
- Gavin 2025 VRI starting layer.
- FHOPS tree stems/simulate/replay pilots once a scenario pin is added.

## What needs new work or data

- Full Gavin LiDAR coverage (2019/2024 or readable 2009) for a complete tree
  inventory.
- A reviewed total-stem density source for both blocks.
- The tree-lab 4D package, if it is to be used.
- GL tree lists and FVS-BC treatment definitions for creative silviculture.
- A full GL state-library rebuild using 2025 VRI and 2025/2026 start time.
