Data Acquisition
================

Status
------

The legal boundary, inventory, BEC, site index, disturbance, mule-deer
habitat-class, site-unit classification and public management-plan inputs are
acquired. The legal UWR order, the 2003 Knife Creek transition strategy, the
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

The Knife Creek management contract is extracted in
``config/mdwr_regimes.yaml``:

- Table 29: High 29 m²/ha, D 60 cm, q 1.25; Moderate 22/55/1.25; Low
  16/50/1.30; 30-year cycle.
- Table 35: 82.0 ha/year single-tree selection and 11.2 ha/year salvage.
- Plan outcome: 0% conventional harvest, 95% modified harvest, 5% no harvest.
- Single-tree selection with small groups of 2–5 trees at maximum diameter.

Figure 11 (target stand structure by habitat class) was recovered with
``figrecover`` 0.1.0a1 and is reviewed at
``data/benchmarks/mwp3_figure11_target_stand_structure.csv``. The recovered
basal-area sums are 17.02/22.96/30.17 m²/ha for Low/Moderate/High; Table 29
remains the residual target. The recovery method, calibration and caveats are in
``notes/reference/mwp3-figure11-recovery.md``.

Appendix 9 (PDF page 162) gives the KC01–KC11 and RD05–RD07 compartment table,
transcribed at ``data/benchmarks/mwp3_kc_compartments.csv``. The map is
schematic and has no coordinate grid; it is a planning-map transcription, not a
georeferenced GIS layer.

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
