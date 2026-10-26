Knife Creek Context
===================

This page records the facts that shape the model. Treat it as context, not as a
substitute for the source layers.

Location and area
-----------------

- The Knife Creek block is the southern block of the UBC Alex Fraser Research
  Forest, near the San Jose Valley, south-east of Williams Lake, British
  Columbia.
- The AFRF Management and Working Plan #2 describes the block as 3,487 ha.
- A public location reference is UTM zone 10U, NAD83, approximately
  575165 E, 5767955 N.
- The gross area is not the net operable area. Use the legal boundary and the
  inventory join for the model area.

Biogeoclimatic setting
----------------------

- The block is predominantly IDFdk3, the Fraser dry cool variant of the
  Interior Douglas-fir zone.
- It has a small IDFxm component and an eastern transition to SBPSmk.
- Interior Douglas-fir dominates; the management plan describes the block as
  dry-belt Douglas-fir with a mule-deer winter-range objective.

Why the silviculture is uneven-aged
-----------------------------------

- Interior Douglas-fir is relatively shade tolerant in this part of its range.
- Almost the whole block is under mule-deer winter-range constraints.
- Even-aged clearcutting is therefore largely unavailable.
- The model must represent repeated selection entries, residual structure, and
  post-cut growth.

Disturbance
-----------

- A 2013 wildfire burned part of the Knife Creek block.
- The burn perimeter, severity, and salvage history must be resolved before the
  current state is assigned.
- Harvest history also shapes the current structure; the block has logging
  records going back to the 1940s.

Model implications
------------------

- A stand-level average growth curve is not sufficient.
- A tree list and an individual-tree growth model are required.
- FVS-BC through `fresh-fvsbc` is the selected engine.
- ws4 receives a state-transition library, not an age-class yield table.

Sources
-------

- AFRF Management and Working Plan #2, public PDF on the AFRF site.
- AFRF block-location page, public.
- AFRF site-units and history reports, public.
- The 2013 wildfire report, public.
- The exact source list and retrieval dates belong in the Phase 1 provenance
  ledger.
