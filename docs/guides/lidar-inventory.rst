LiDAR Tree Inventory
====================

LidarBC coverage exists over Knife Creek. The pilot uses the provincial 1 m DEM
and DSM to build a canopy-tree inventory and a spatial clump summary.

What was downloaded
-------------------

- 2024 DEM and DSM for tile `093a001_2_4_3` (about 7 MB each);
- the 2024 point cloud for that tile was not downloaded for the pilot.

The AOI discovery found 134 point-cloud tiles, 76 DEM tiles and 72 DSM tiles
over the SUP.

Method
------

1. CHM = DSM − DEM, clipped to the SUP.
2. Smooth the CHM at sigma 0.7 m.
3. Detect local maxima with a 9-cell (about 4.5 m) minimum spacing and a 5 m
   height threshold.
4. Estimate crown radius from nearest-neighbour distance, capped at 8 m.
5. Estimate DBH from a PSP Douglas-fir height–DBH fit.
6. Build clumps by connecting trees within 5, 10 or 15 m.

Pilot result
------------

- 247.56 ha valid CHM;
- 20,513 canopy trees; 82.9 TPH;
- height mean 17.2 m, p95 25.5 m, max 36.3 m;
- estimated DBH mean 22.6 cm, max 51.2 cm;
- 4,747 trees at least 20 m tall.

Clumps for trees ≥20 m:

.. list-table::
   :header-rows: 1

   * - Linkage
     - Clumps
     - Mean size
     - 4–10-tree clumps
     - Singletons
     - Clumps/ha
   * - 5 m
     - 4,720
     - 1.01
     - 0
     - 4,693
     - 19.1
   * - 10 m
     - 2,177
     - 2.18
     - 207
     - 1,418
     - 8.8
   * - 15 m
     - 684
     - 6.94
     - 67
     - 437
     - 2.8

The 5 m linkage is too tight; 15 m merges most of the stand. The 10 m linkage
is the informative scale.

Limits
------

This is a **canopy-tree inventory**, not a CFI. It has no species, understory,
measured DBH, damage or mortality. DBH is height-allometry only and its BA
should not be used for calibration. The 1 m DSM can split broad crowns, and the
pilot is one tile, not the block. A point-cloud CHM and field plots are needed
before using it as a growth/yield input.

Files
-----

- ``data/lidar/pilot_093a001_2_4_3/trees.gpkg``
- ``data/lidar/pilot_093a001_2_4_3/trees.csv``
- ``data/lidar/pilot_093a001_2_4_3/summary.json``
- ``data/lidar/pilot_093a001_2_4_3/clump_analysis.csv``
- ``runbooks/lidar_tree_inventory.py``
- ``notes/reference/lidarbc-kc-pilot.md``

Full 2024 run
-------------

All 72 2024 DEM/DSM pairs were downloaded (940 MB). 28 tiles intersect the SUP
strongly enough to produce clipped trees. The merged inventory has:

- 278,318 canopy trees;
- 78.8 TPH over 3,533.13 ha;
- height mean 19.5 m, p95 28.6 m, max 46.9 m;
- estimated DBH mean 25.9 cm, max 67.9 cm;
- 117,297 trees at least 20 m tall.

Clumps for trees ≥20 m:

.. list-table::
   :header-rows: 1

   * - Linkage
     - Clumps
     - Mean size
     - 4–10-tree clumps
     - Singletons
   * - 5 m
     - 116,007
     - 1.01
     - 5
     - 114,752
   * - 10 m
     - 50,401
     - 2.33
     - 6,046
     - 30,214
   * - 15 m
     - 11,903
     - 9.85
     - 1,466
     - 6,803

The 10 m linkage is the useful scale. The full run is in
``data/lidar/kc_2024/``.

Next
----

Process all 2024 tiles or a stratified subset, use the point cloud/0.5 m CHM,
compare against VRI and field plots, and feed the observed clump geometry into
the ws4 spatial constraint. Keep DBH/BA labelled estimated until a CFI exists.
