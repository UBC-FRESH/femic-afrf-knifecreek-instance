# KC spatial dataset v4

Compiled from `ws4/state_library_v2/canonical` with the 160-block VRI/HMZ
crosswalk and LiDAR clump/reserve classes. It is the first KC spatial dataset
in this instance whose canonical graph contains repeated states and cycles.

- 160 blocks / 3,481.77 ha
- 128 tracks (32 canonical states x 4 HMZ groups)
- 79 treatments
- 160 block assignments
- `ws4 validate --dataset ws4/dataset_kc_spatial_v4` passes

## Boundary

This is a structural spatial fixture. Tree lists are PSP-derived, not KC CFI.
Clump reserve is the FVS DBH-ranked proxy. The HMZ offers enforce the matrix
structurally, not as a legal-compliance determination. The canonical state
assignment is a nearest-class assignment, not a measured state.

## Reproduction

```bash
PYTHONPATH=/path/to/ws4 \
  python runbooks/compile_kc_spatial_dataset.py \
  --canonical ws4/state_library_v2/canonical \
  --vri data/inventory/vri_2025_kc.gpkg \
  --sup data/boundaries/knife_creek_sup_S15382.gpkg \
  --hmz-crosswalk data/habitat/kc_vri_hmz_overlay.csv \
  --lidar-block-summary data/lidar/kc_2024/block_tree_summary.csv \
  --lidar-reserve-summary data/lidar/kc_2024/block_reserve_summary.csv \
  --out-dir ws4/dataset_kc_spatial_v4
```
