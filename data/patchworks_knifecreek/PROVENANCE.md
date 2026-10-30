# Provenance

P3.2/P3.3/P3.4/P3.5 derived package, generated 2026-10-30.

## Sources

- VRI 2025 R1: `data/inventory/vri_2025_kc.gpkg`
- SUP S15382: `data/boundaries/knife_creek_sup_S15382.gpkg`
- Structural ws4 dataset: `ws4/dataset_kc_spatial_v3`
- FAIB IDF PSPs: public FAIB ground-plot compilation
- Roads: BC Forest Tenure Road Section Lines, WFS type
  `pub:WHSE_FOREST_TENURE.FTEN_ROAD_SECTION_LINES_SVW`, Open Government
  Licence - British Columbia

## Transformations

1. Clip VRI to SUP; keep area ≥0.1 ha, BA>0 and live stems>0.
2. Assign `BLOCK`/`TRACK` in `dataset_kc_spatial_v3` order.
3. Build block topology at 100 m search distance; record shortest polygon
   distance and shared boundary length.
4. Fetch and clip BC Forest Tenure road sections to the SUP.
5. Build H matrix from `dataset_kc_spatial_v3`.
6. Replace feature curves with nearest BA/QMD space-for-time FAIB site curves.
7. Add area curves and `_MANAGED_` accounts.

## Checks

- 160 blocks / 3,481.77 ha
- 500 topology pairs, 352 touching pairs
- 44 road sections, 59,637.8 m; stored as GeoPackage to keep the text scanner out of the DBF
- `ws4 ingest` succeeds
- `ws4 validate` passes

## Limits

- OSM was tried first and had no highway inside the SUP; the BC Forest Tenure
  layer is the road source.
- No route configuration or legal access claim.
- No raw PSP tree records or private workbook in this package.
