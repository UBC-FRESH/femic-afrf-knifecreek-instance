# Knife Creek full-estate 3D scene

`knife_scene.json` is the WS4 studio-3D scene pack for Knife Creek.

- 183 VRI block polygons
- 2024 LidarBC 5 m DEM/CHM terrain and canopy
- VRI live-stems/ha density, VRI projected heights and LiDAR-derived mean heights
- VRI species composition by block, not a single estate-wide species mix
- approximately 3.0M synthetic stem positions inside blocks, not a measured stem map
- the scene starts on a central production block and opens at a stand-scale camera so trunks are visible; wheel out for the full estate view
- CHM coverage is effectively complete within the VRI blocks; terrain no-data gaps use SRTM

Current area-weighted VRI composition in the scene:

| Species | Share |
| --- | ---: |
| FDI / FD (Douglas-fir) | 87.4% |
| PLI / PL (lodgepole pine) | 5.3% |
| AT (trembling aspen) | 4.1% |
| SX / SS (spruce) | 2.7% |
| EP (paper birch) | 0.5% |

Build metrics with `planning/studio3d/knife_scene_metrics.csv`, which carries the
VRI species string for every `POLYGON_ID`.

Build command:

```bash
python scripts/build_afrf_studio3d.py \
  --blocks data/inventory/vri_2025_kc.gpkg \
  --metrics planning/studio3d/knife_scene_metrics.csv \
  --id-field POLYGON_ID \
  --density-field density \
  --height-field height_m \
  --species-field species \
  --dem data/lidar/kc_2024/dem_5m.tif \
  --chm data/lidar/kc_2024/chm_5m.tif \
  --srtm-dir /path/to/srtm \
  --label "Knife Creek · full-estate 3D scene" \
  --source-note "LidarBC 2024 5 m DEM/CHM; VRI live stems/ha, heights and species composition; synthetic stem positions." \
  --out planning/studio3d/knife_scene.json
```
