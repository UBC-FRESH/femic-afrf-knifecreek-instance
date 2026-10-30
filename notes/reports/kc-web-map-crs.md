# KC web map CRS fix

Status: fixed and verified in the live UI.

## Symptom

The MapLibre layer drew block polygons as long triangular strips. The same
polygons rendered correctly in the GeoJSON patch layer and in a standalone
matplotlib plot.

## Cause

The web service was started with the default source CRS, EPSG:4326, while the
MVT tile builder applies its simplification tolerance in metres. At zoom 12 the
15 m tolerance was therefore applied as 15 degrees against the WGS84 geometry,
collapsing blocks into thin triangles.

## Fix

- Export `kc_blocks.geojson` in EPSG:3005, the source inventory projection.
- Start `ws4 serve` with `--crs EPSG:3005`.
- Keep the UI's `format=wgs84` transform for MapLibre display.
- The pipeline now rejects a map geometry that is not EPSG:3005.

## Verification

`ws4/evidence/kc_v1/kc_web_map.png` shows the block fills and boundaries
correctly in the MapLibre view. The light-green diagonal feature is a long,
thin VRI block, not a rendering artifact.
