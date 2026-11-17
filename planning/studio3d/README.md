# Knife Creek full-estate 3D scene

`knife_scene.json` is the WS4 studio-3D scene pack for Knife Creek.

- 183 VRI block polygons
- SRTM 1 arc-second terrain
- VRI live-stems/ha density and LiDAR mean heights
- approximately 3.0M nominal stems
- no full-estate CHM; canopy is labelled synthetic
- synthetic stem positions inside blocks, not a measured stem map

Build command:

```bash
python scripts/build_afrf_studio3d.py \
  --blocks data/inventory/vri_2025_kc.gpkg \
  --metrics /tmp/knife_scene_metrics.csv \
  --id-field POLYGON_ID \
  --density-field density \
  --height-field height_m \
  --srtm-dir /path/to/srtm \
  --label "Knife Creek · full-estate 3D scene" \
  --out planning/studio3d/knife_scene.json
```
