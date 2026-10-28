# Knife Creek 2024 LidarBC canopy inventory

Status: **canopy-tree inventory**, not a CFI and not a growth/yield calibration.

## Coverage

- 28 of the 72 2024 DEM/DSM tiles intersect the SUP strongly enough to produce
  clipped trees; all 72 pairs were downloaded (940 MB).
- 278,318 canopy trees over the 3,533.13 ha SUP.
- 78.8 TPH; height mean 19.5 m, p95 28.6 m, max 46.9 m.
- Estimated DBH mean 25.9 cm, max 67.9 cm; 117,297 trees ≥20 m.

## Clumps

| Linkage | Clumps | Mean size | 4–10-tree clumps | Singletons |
| ---: | ---: | ---: | ---: | ---: |
| 5 m | 116,007 | 1.01 | 5 | 114,752 |
| 10 m | 50,401 | 2.33 | 6,046 | 30,214 |
| 15 m | 11,903 | 9.85 | 1,466 | 6,803 |

The 10 m linkage is the useful scale; 5 m is too tight and 15 m over-merges.

## Files

- `trees.parquet` — merged canopy tree points, committed.
- `summary.json`, `tile_summary.csv`, `clump_analysis.csv` — summary tables.
- `trees.gpkg`, `trees.csv` — ignored local copies (large).
- Generator: `runbooks/lidar_inventory_all_tiles.py`.

## Limits

No species, understory, measured DBH, damage or mortality. DBH is
height-allometry only; estimated BA is not a calibration target. 1 m DSM local
maxima can split crowns. The SUP denominator is legal area, not per-tile area;
tiles overlap at edges.

## Block features

`block_tree_summary.csv` joins the tree points to clipped VRI polygons. All 160
spatial blocks have LiDAR coverage: mean 77.2 TPH, 39.1 TPH ≥20 m, and 18.2
4–10-tree clumps/ha. `block_tree_summary.json` carries the summary.

## Spatial reserve scenario

`reserve_trees.parquet` assigns every large LiDAR tree to `reserve` or
`harvest`: 88,640 reserve trees and 28,191 harvest trees across 160 blocks.
`block_reserve_summary.csv` has per-block reserve/harvest TPH and BA estimates.
The FVS treatment reserve is still the DBH-ranked proxy; this is a spatial
canopy reserve scenario, not the FVS tree-level cut.
