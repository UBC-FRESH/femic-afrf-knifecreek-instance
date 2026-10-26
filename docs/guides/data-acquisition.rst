Data Acquisition
================

Status
------

No source data is committed yet. This page is the acquisition and acceptance
checklist for Phase 1.

Boundary
--------

The legal boundary is the first requirement. It must:

- identify the Knife Creek block, not the whole AFRF;
- carry a CRS that can be transformed to EPSG:3005;
- join cleanly to the VRI and BEC layers; and
- be stored with a checksum and a provenance note.

The public location reference is UTM zone 10U, NAD83, approximately
575165 E, 5767955 N. The block is described in the AFRF Management and Working
Plan as 3,487 ha, located near the San Jose Valley, south-east of Williams Lake.
The gross area is not the net operable area; do not use the published figure as
a model area without the boundary.

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
