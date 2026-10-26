Data Acquisition
================

Status
------

The legal boundary is acquired. The inventory, BEC, site index, disturbance,
mule-deer, and stem-list inputs are still required.

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
