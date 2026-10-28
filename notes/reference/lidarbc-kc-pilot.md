# LidarBC tree-inventory pilot at Knife Creek

## Coverage

`femic lidar discover` over the SUP S15382 bbox found:

- 134 point-cloud tiles (62 from 2019, 72 from 2024);
- 76 DEM tiles;
- 72 DSM tiles;
- 282 total tiles over the AOI.

The 2024 tiles are the higher-density collection (`point_density_ppm2: 8`).

## Pilot tile

Tile `093a001_2_4_3`, 2024 acquisition, 1 m DEM and DSM. The tile covers the
central Knife Creek block. Only the DEM and DSM were downloaded for the pilot;
the 311 MB point cloud was not needed for the canopy inventory.

Derived files:

- `data/lidar/pilot_093a001_2_4_3/trees.gpkg`
- `data/lidar/pilot_093a001_2_4_3/trees.csv`
- `data/lidar/pilot_093a001_2_4_3/summary.json`
- `data/lidar/pilot_093a001_2_4_3/clump_analysis.csv`
- `data/lidar/pilot_093a001_2_4_3/femic_summary/tree_product_summary.json`

Reproducer: `runbooks/lidar_tree_inventory.py`.

## Method

1. CHM = DSM − DEM, clipped to the SUP boundary.
2. Smooth the CHM at sigma 0.7 m.
3. Detect local maxima with a 9-cell (about 4.5 m) minimum spacing and a 5 m
   height threshold.
4. Estimate crown radius as half the nearest-neighbour distance, capped at
   8 m.
5. Estimate DBH with `log(DBH) = -0.01593 + 1.10047 log(height)` fitted to the
   PSP conditional Douglas-fir trees.
6. Build spatial clumps by connecting trees within 5, 10 or 15 m.

## Result

- 247.56 ha valid CHM inside the boundary.
- **20,513 canopy trees**; 82.9 TPH.
- Height: mean 17.2 m, median 16.7 m, p95 25.5 m, max 36.3 m.
- Crown radius: mean 3.86 m, median 3.64 m, max 8 m.
- Estimated DBH: mean 22.6 cm, median 21.8 cm, max 51.2 cm.
- Trees ≥20 m: 4,747.

Clump summary for trees ≥20 m:

| Linkage | Clumps | Mean size | Max size | 2–5 tree clumps | 4–10 tree clumps | Singletons | Clumps/ha |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 m | 4,720 | 1.01 | 2 | 27 | 0 | 4,693 | 19.1 |
| 10 m | 2,177 | 2.18 | 65 | 621 | 207 | 1,418 | 8.8 |
| 15 m | 684 | 6.94 | 2,713 | 195 | 67 | 437 | 2.8 |

At 5 m the canopy is almost all singletons. At 15 m the whole stand merges into
a giant component. The 10 m linkage is the informative scale: it finds 207
4–10-tree clumps, but also many singletons.

## Limits

- This is a **canopy-tree inventory**, not a CFI. It has no species, understory,
  measured DBH, damage, or mortality.
- The DBH values are height-allometry estimates and should not be used to
  calibrate stand BA. The estimated BA is much lower than VRI BA.
- The 1 m DSM local maxima can split a broad crown into several trees.
  Minimum spacing reduces but does not remove over-segmentation.
- One 1.8 × 1.5 km tile is not the whole block.
- The 2024 point cloud is not downloaded; a 0.5–1 m point-cloud CHM may improve
  crown segmentation.
- No ground-truth comparison against KC CFI yet.

## Spatial reserve scenario

`runbooks/lidar_reserve_scenario.py` assigns a reserve inside each block:

- mature trees are height ≥20 m;
- connect at 10 m;
- 4–10-tree clumps reserve the three largest trees;
- components over 10 trees are split into 10-tree height-ranked chunks;
- components under four trees are left intact.

Across 160 blocks: 116,831 large trees, 54,307 clumps, 88,640 reserve trees,
28,191 harvest trees. Mean reserve 30.0 TPH and harvest 9.15 TPH. The reserve
BA estimate is 2.76 m²/ha. This is a spatial canopy scenario, not a legal D-floor
check.

## What it changes

- It proves LidarBC coverage exists over Knife Creek and can produce a
  tree-position/crown inventory.
- It provides a real spatial clump signal for the 4–10-tree rule, replacing the
  purely DBH-ranked proxy as a **validation/scenario input**.
- It does **not** replace the CFI: species, DBH, understory and growth still
  need field data.

## Next

1. Process all 2024 tiles (72) or a stratified subset, not just one tile.
2. Use the point cloud and a 0.5 m CHM to reduce over-segmentation.
3. Compare LiDAR crowns/height to VRI and any available field plots.
4. Use LiDAR clumps to calibrate the spatial clump rule in `ws4`.
5. Keep the DBH/BA fields labelled estimated until a CFI calibration exists.

## Multi-tile 2024 run

All 72 2024 DEM/DSM pairs were downloaded (940 MB). 28 tiles intersect the SUP
strongly enough to produce trees after clipping. The merged inventory is in
`data/lidar/kc_2024/`.

- 278,318 canopy trees;
- 78.8 TPH over the 3,533.13 ha SUP;
- height mean 19.5 m, p95 28.6 m, max 46.9 m;
- estimated DBH mean 25.9 cm, max 67.9 cm;
- 117,297 trees ≥20 m.

Clumps for trees ≥20 m:

| Linkage | Clumps | Mean size | 4–10-tree clumps | Singletons | Clumps/ha |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 5 m | 116,007 | 1.01 | 5 | 114,752 | 32.8 |
| 10 m | 50,401 | 2.33 | 6,046 | 30,214 | 14.3 |
| 15 m | 11,903 | 9.85 | 1,466 | 6,803 | 3.4 |

At block scale this is still a canopy inventory: no species, understory or
measured DBH. The 10 m linkage finds thousands of 4–10-tree groups, but also
many singletons; 15 m over-merges. The inventory is now broad enough to compare
against VRI and to derive block-level clump features, not yet a CFI replacement.

Note: 28 tiles processed, not all 72, because many 2024 tiles do not intersect
the SUP after clipping. The 3,533.13 ha denominator is the legal SUP area, not
the sum of per-tile areas; per-tile areas overlap at edges.
