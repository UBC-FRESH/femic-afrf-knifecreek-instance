# KC spatial dataset v5

Compiled from `ws4/state_library_v3/canonical` with the 160-block VRI/HMZ
crosswalk and LiDAR clump/reserve classes.

- 160 blocks / 3,481.77 ha
- 140 tracks (35 canonical states x 4 HMZ groups)
- 96 treatments
- 160 block assignments
- `ws4 validate --dataset ws4/dataset_kc_spatial_v5` passes

This is the first dataset in the instance whose HMZ-constrained canonical graph
contains a positive legal cycle. It still uses PSP-derived tree lists, a
DBH-ranked clump proxy and a nearest-class initial-state assignment. It is a
structural fixture, not a KC operating model or legal-compliance product.
