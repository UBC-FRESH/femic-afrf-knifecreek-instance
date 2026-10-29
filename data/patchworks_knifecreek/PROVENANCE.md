# Provenance

P3.2 fragment layer, generated 2026-10-29.

## Sources

| Source | SHA-256 |
| --- | --- |
| `data/inventory/vri_2025_kc.gpkg` | `9d05220b18c073902c47755088adfa532fe288e312b4d0418e7bb67a073837b5` |
| `data/boundaries/knife_creek_sup_S15382.gpkg` | `e79189b10d5da590d0adae658fc59607ca63e242362c9ee8963c76bea731f480` |
| `ws4/dataset_kc_spatial_v3/manifest.json` | `b0587ba1c016a52117baa741c4e70e611a9bc5447658879e6797d8ce6b1b82c2` |
| `data/patchworks_knifecreek/spatial/fragments.shp` | `4907020a71c2075c97b4a780b88d327329e00177f3c7f76c5c73a252ab17a23d` |

## Transformation

1. Read VRI 2025 and SUP S15382 in EPSG:3005.
2. Intersect VRI with the SUP.
3. Keep polygons with area ≥ 0.1 ha, positive basal area and positive live stems.
4. Assign `BLOCK` and `TRACK` in the exact order used by `dataset_kc_spatial_v3`.
5. Carry BEC, HMZ, clump and reserve classes and VRI projected age.
6. Write the shapefile and derived CSV.

## Checks

- 160 blocks, one-to-one with `dataset_kc_spatial_v3`.
- Total area 3,481.77 ha.
- EPSG:3005.
- `BLOCK`, `TRACK`, `AREA_HA` and `F_AGE` match the compiled dataset.

## Limits

- The source VRI and SUP are public; the PSP tree records remain private.
- No absolute plot centres or treatment polygons.
- No Patchworks recipe or matrix is validated yet.
