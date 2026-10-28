Data Acquisition
================

Status
------

The legal boundary, inventory, BEC, site index, disturbance, mule-deer
habitat-class, site-unit classification and public management-plan inputs are
acquired. The 2007 GWM order text, the 2003 Knife Creek transition plan and the
Part 1a/1b scientific basis are acquired. The spatial UWR/HMZ layer, the
georeferenced site-series map and a stem list are still required.

Boundary acquired
-----------------

The legal Knife Creek block is Provincial Special Use Permit **S15382**:

- dataset: Forest Tenure Special Use Permit Polygon;
- WFS type: ``pub:WHSE_FOREST_TENURE.FTEN_SPEC_USE_PERMIT_POLY_SVW``;
- special use: code 30, "Research or Educational", ACTIVE;
- area: 3,533.1341 ha;
- CRS: EPSG:3005;
- licence: Open Government Licence - British Columbia;
- path: ``data/boundaries/knife_creek_sup_S15382.gpkg``; and
- SHA-256:
  ``e79189b10d5da590d0adae658fc59607ca63e242362c9ee8963c76bea731f480``.

The FADM_TSA layer confirms the block is in **Williams Lake TSA (TSA 29)**.
The TSA boundary is not the research-forest boundary; the SUP polygon is.

The AFRF Management and Working Plan #2 describes the block as 3,487 ha. The
SUP permit block area is 3,533.1341 ha, a 46.13 ha difference. The SUP polygon
is the legal gross boundary; the published figure may be a net or rounded area.
Use the SUP polygon for the legal boundary and the VRI join for the net forested
area.

The full provenance, the fetch command, and the area reconciliation are in
``metadata/boundary_source.yaml``.

Layers acquired
---------------

The public-data pass acquired the following layers. All are clipped to the SUP
boundary and stored in EPSG:3005. Source, WFS type, fetch or derivation, and
checksum for each are in ``metadata/layer_sources.yaml``.

VRI 2025 R1
~~~~~~~~~~~

- 183 polygons over 3,533.13 ha.
- Leading species: FDI 160, AT 7, SX 5, PLI 2.
- ``SITE_INDEX`` present on 174 of 183 polygons.
- Path: ``data/inventory/vri_2025_kc.gpkg``.

BEC map
~~~~~~~

- ``IDFdk3``: 3,051.80 ha.
- ``IDFxm``: 481.33 ha.
- The current map has no SBPSmk polygon inside the SUP.
- Path: ``data/inventory/bec_kc.gpkg``.

Historical fire perimeters
~~~~~~~~~~~~~~~~~~~~~~~~~~

- 2013 (`C20393`): 6.04 ha.
- 1938 (`59`): 62.11 ha.
- 1937 (`29`): 0.66 ha.
- Path: ``data/inventory/fire_perimeters_kc.gpkg``.

Harvest history
~~~~~~~~~~~~~~~

- 60 openings over 2,478.73 ha, harvest years 1956–2023.
- Derived table: ``data/inventory/harvest_history_kc.csv``.
- The raw cutblock polygons are not committed because the catalogue records
  the layer as ``Access Only``. The WFS fetch is reproducible.

Mule-deer stand structure habitat classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- High: 1,327.68 ha.
- Moderate: 1,135.66 ha.
- Low: 1,020.53 ha.
- Nil: 6.15 ha.
- Path: ``data/habitat/mule_deer_stand_structure_kc.gpkg``.
- This is the public habitat-class layer, not the legal UWR order.

Site index
~~~~~~~~~~

- VRI ``SITE_INDEX`` on 174 of 183 polygons.
- ``EST_SITE_INDEX`` and ``EST_SITE_INDEX_SPECIES_CD`` are also carried.
- The Provincial Site Productivity Layer is an alternative, but the catalogue
  marks it ``Access Only`` and its direct resource is a raster folder.
- The Klinka 2004 site-index tables are transcribed in
  ``data/site_index/klinka_2004_site_index.csv`` (Tables 8.2.1–8.2.4; 105
  rows; IDFxm, IDFdk3, SBSdw1 and ICHmk3). This is a direct table
  transcription, not a figure recovery.

AFRF Management and Working Plan #3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The plan is acquired at
``reference/AFRF-management-working-plan-3-2007.pdf`` with SHA-256
``9bfd8b8f0449f45fb97fcf529236640ace09b73ba74f77001f677eee7307ff6a``.
It is a public UBC AFRF planning document, not an OGL dataset.

The plan gives the AFRF Table 29 interpretation:

- High 29 m²/ha, D 60 cm, q 1.25; Moderate 22/55/1.25; Low 16/50/1.30;
- 30-year cycle;
- AAC 82.0 ha/year single-tree selection + 11.2 ha/year salvage;
- plan outcome 0% conventional, 95% modified, 5% no harvest.

Table 29 is **not** the legal curve. The legal order uses BA >37.5 cm
≥16/11/6 m²/ha, Table 2 D ≥70/60/50, and a large-tree reserve. The AFRF plan's
2–5-tree groups are the maximum-diameter subgroup; the legal clump is 4–10 or
more mature trees with interlocking crowns.

Figure 11 (target stand structure by habitat class) was recovered with
``figrecover`` 0.1.0a1 and is reviewed at
``data/benchmarks/mwp3_figure11_target_stand_structure.csv``. The recovered
basal-area sums are 17.02/22.96/30.17 m²/ha for Low/Moderate/High; Table 29
remains the AFRF residual-shape target. The recovery method, calibration and
caveats are in ``notes/reference/mwp3-figure11-recovery.md``.

Appendix 9 (PDF page 162) gives the KC01–KC11 and RD05–RD07 compartment table,
transcribed at ``data/benchmarks/mwp3_kc_compartments.csv``. The map is
schematic and has no coordinate grid; it is a planning-map transcription, not a
georeferenced GIS layer.

2007 GWM order and 2003 Knife Creek transition plan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The legal source is the *Amended Order #U-5-001, U-5-002 and U-5-003 —
Ungulate Winter Ranges, Cariboo Chilcotin Land Use Plan, Shallow and Moderate
Snowpack* (signed February 2007). Knife Creek is U-5-002 ``dwl_50``.

The order text and the 2003 *Transition Period Harvest Opportunities: Knife
Creek* are acquired in the workspace source set:

- ``/srv/shared-data/gep/ws4/sources/afrf-mule-deer/gwm_order_shallow_moderate_2007.pdf``
- ``/srv/shared-data/gep/ws4/sources/afrf-mule-deer/part3_knife_creek.pdf``

Key requirements:

- clumps of 4–10 or more mature trees with interlocking crowns;
- canopy openings 0.3–1.0 tree heights, mean 0.5;
- legal stand targets: B 29/22/16; BA >37.5 ≥16/11/6; D ≥70/60/50;
- q 1.20–1.35 / 1.25–1.35 / 1.25–1.40;
- large-tree reserve 0–2.9 / 0–2.2 / 0–1.6 above D;
- HMZ 1–5 = ``M, L, M, M, A`` for Knife Creek;
- before 2026, retain ≥80% of pre-harvest merchantable Douglas-fir BA; and
- a potential north-facing >20% slope, >10 ha exemption in the Moderate
  Snowpack zone.

The spatial HMZ layer is acquired at
``data/habitat/mule_deer_hmz_kc.gpkg`` from the BC Map Hub/DataBC layer. Knife
Creek HMZ areas are 1 M 738.29 ha, 2 L 1,217.15 ha, 3 M 320.51 ha, 4 M
1,213.33 ha, 5 A 0.00045 ha; total 3,489.27 ha against the 3,533.13 ha SUP.
The VRI × HMZ crosswalk is ``data/habitat/kc_vri_hmz_overlay.csv``. The current
approved order and legal stand-structure map still need verification before a
compliance claim.

The extracted contract is ``config/mdwr_regimes.yaml`` and the FVS-BC templates
are ``config/fvsbc/regimes.yaml``. The default basis is GWM 2007; Table 29 is a
named alternative. See :doc:`../reference/mdwr-legal-basis`.

LidarBC canopy inventory
~~~~~~~~~~~~~~~~~~~~~~~~

LidarBC discovery over the SUP found 134 point-cloud tiles, 76 DEM tiles and
72 DSM tiles. A 2024 1 m DEM/DSM pilot tile produced 20,513 canopy trees over
247.56 ha, with 82.9 TPH and a spatial clump table. The tree inventory is
`data/lidar/pilot_093a001_2_4_3/trees.gpkg`.

This is **not a CFI**: it has no species, understory or measured DBH. DBH is a
height-allometry estimate; the estimated BA is much lower than VRI BA. See
:doc:`lidar-inventory` and `notes/reference/lidarbc-kc-pilot.md`.

PSP-derived IDF Cariboo stem lists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The FAIB Forest Inventory Ground Plot Data is public under the Open Government
Licence. The PSP compilation contains 338 first-measurement IDF plots in the
Williams Lake and 100 Mile House TSAs. A subset of 51 Douglas-fir-leading,
mature plots (80-180 years, 20-40 m²/ha, QMD 15-25 cm) yielded 4,553 live trees
at least 9.1 cm DBH. Forty-five per-plot Weibull fits were stable; the pooled
fit is Weibull a=1.0200, beta=7.8411, lower bound 9.1 cm.

`runbooks/build_psp_stemlists.py` turns that into 24 synthetic one-hectare stem
lists (22,178 trees) by inverse-CDF sampling, calibrated to each source plot's
basal area. Files are in `data/psp/`. Three stands ran through FVS-BC with the
corrected cycle-2 THINQFA; residual BA was 30-34 m²/ha against the 29 m²/ha
target.

This is a regional IDF analog, not Knife Creek data. The raw PSP files are not
committed. See `notes/reference/psp-idf-cariboo-stemlists.md` for source hashes,
selection, fitting and caveats.

Inventory
---------

Required inventory attributes:

- polygon identifier and area;
- species composition and leading species;
- age or estimated age;
- site index and site index species;
- height, diameter, and density where available;
- BEC zone, subzone, and variant;
- site series or ecosystem unit;
- disturbance and harvest history; and
- mule-deer winter-range designation.

The VRI is a polygon-level inventory. It does not contain a tree list. A tree
list must come from measured plots, a reviewed reconstruction, or `nemora`.
The source and method must travel with every stem list.

Site series (Klinka et al. 2004)
--------------------------------

The AFRF site-unit report is acquired:

- citation: Klinka et al. 2004, *Site Units of the UBC Alex Fraser Research
  Forest*;
- path: ``reference/AFRF-site-unit-report-2004.pdf``;
- SHA-256:
  ``94459a7bc6002932bc9a2150deb6d81879fbd48d776b86e4666e75addc7f5705``; and
- extracted catalog: ``config/site_series.yaml``.

The report gives nine site groups and the IDFxm 01-09 and IDFdk3 01-10 site
series, with BCFS codes, names, keys, edatopic grids, and descriptions. The
Knife Creek block is in the IDFxm / IDFdk3 / IDFdk3-SBPSmk transition set.

The **georeferenced site-series map is not in the PDF**. The report's site maps
are folded map pockets and a CD-ROM. The spatial map is still P1.2a. Do not
infer site series from BEC zone/subzone alone.

BEC and site index
------------------

The AFRF Management and Working Plan describes Knife Creek as predominantly
IDFdk3, with a small IDFxm component and an eastern transition to SBPSmk. The
site-series map and the current BEC mapping are the authority for the model;
the management-plan description is context, not a substitute for the spatial
layer.

The 2013 wildfire is a material disturbance. The burn perimeter, severity, and
salvage history must be resolved before the current state is assigned.

Mule-deer constraints
---------------------

Almost the whole block is under mule-deer winter-range objectives. The model
needs the spatial designation and the applicable constraints, which may
include:

- retained basal area or canopy cover floors;
- large-tree retention;
- limits on even-aged openings;
- selection-entry timing; and
- winter-range suitability classes.

Do not invent a constraint value. Record the source, the review status, and the
spatial mapping. A constraint that cannot be mapped is a documented gap, not a
default.

Data-quality audit
------------------

The Phase 1 audit must report:

- the boundary area and the sum of joined polygon areas;
- the area with no inventory match;
- the area with no BEC match;
- the area with no site index;
- the area inside and outside the 2013 burn;
- the area in each mule-deer class;
- the age and species distributions; and
- every unresolved or conflicting source.

Acceptance is not "the layers load". It is "the joins and the gaps are known".
