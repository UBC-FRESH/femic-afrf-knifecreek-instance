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
- The legal boundary is Special Use Permit **S15382**, "Research or
  Educational", ACTIVE, 3,533.1341 ha, in the public Forest Tenure Special Use
  Permit Polygon layer. It is in Williams Lake TSA (TSA 29).

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

Management direction
--------------------

The default Knife Creek model basis is the **2007 GWM order** (Amended Order
#U-5-001/U-5-002/U-5-003, Shallow and Moderate Snowpack). Knife Creek is
U-5-002 ``dwl_50``. The AFRF MWP #3 Table 29 values are a named alternative,
not the legal curve. See :doc:`mdwr-legal-basis`.

Legal stand-level targets for IDFdk3/IDFdw:

.. list-table::
   :header-rows: 1

   * - Habitat class
     - Total BA ≥12.5 cm
     - BA ≥37.5 cm
     - Table 2 D
     - q
     - Reserve above D
   * - High
     - ≥29 m²/ha
     - ≥16 m²/ha
     - ≥70 cm
     - 1.20–1.35
     - 0–2.9 m²/ha
   * - Moderate
     - ≥22 m²/ha
     - ≥11 m²/ha
     - ≥60 cm
     - 1.25–1.35
     - 0–2.2 m²/ha
   * - Low
     - ≥16 m²/ha
     - ≥6 m²/ha
     - ≥50 cm
     - 1.25–1.40
     - 0–1.6 m²/ha

GWM 10 requires clumps of **4–10 or more mature trees with interlocking
crowns**, small canopy openings 0.3–1.0 tree heights (mean 0.5), and a minimum
30-year cutting cycle. MWP #3's 2–5-tree groups are only the maximum-diameter
subgroup inside the clump.

The AFRF MWP #3 Table 29 alternative is:

.. list-table::
   :header-rows: 1

   * - Habitat class
     - Residual B
     - Maximum DBH
     - q
     - Cutting cycle
   * - High
     - 29 m²/ha
     - 60 cm
     - 1.25
     - 30 years
   * - Moderate
     - 22 m²/ha
     - 55 cm
     - 1.25
     - 30 years
   * - Low
     - 16 m²/ha
     - 50 cm
     - 1.30
     - 30 years

Table 29 matches the legal total-B values but uses lower D (60/55/50 vs
70/60/50) and omits the legal BA >37.5 targets and reserve. Label any Table 29
run as an AFRF interpretation, not compliance.

The legal Knife Creek HMZ row is HMZ 1–5 = ``M, L, M, M, A``: HMZ 2 is Low-only;
HMZ 1/3/4 are Low or Moderate; HMZ 5 is all classes. The 2003 transition plan
and the order text are acquired; the spatial UWR/HMZ layer is still required.

Table 35 gives the Knife Creek AAC as 82.0 ha/year of single-tree selection plus
11.2 ha/year of salvage. The 2001–2005 actual was 44.3 ha/year partial cut plus
31.2 ha/year salvage, against 93.2 ha/year total AAC. The plan's CCLUP outcome
is 0% conventional harvest, 95% modified harvest and 5% no harvest, compared
with the CCLUP target of 45/50/5.

These are public management-plan values; the legal order is the default
constraint. The full contract is in ``config/mdwr_regimes.yaml`` and the
context note is ``notes/reference/mwp3-kc-management-direction.md``.

Figure 11 on the same page gives the relative diameter distribution by 5 cm
class. It was recovered with ``figrecover``; the reviewed table is
``data/benchmarks/mwp3_figure11_target_stand_structure.csv``. Its basal-area
sums are 17.02/22.96/30.17 m²/ha for Low/Moderate/High, slightly above the Table
29 targets. The recovered density distribution implies q 1.306/1.254/1.253,
close to the Table 29 values 1.30/1.25/1.25. Use Table 29 for the AFRF shape
comparison and the GWM tables for the legal basis.

Disturbance
-----------

- A 2013 wildfire burned part of the Knife Creek block.
- The burn perimeter, severity, and salvage history must be resolved before the
  current state is assigned.
- Harvest history also shapes the current structure; the block has logging
  records going back to the 1940s.

Site series
-----------

- Klinka et al. 2004 maps nine site groups and the IDFxm 01-09 and IDFdk3
  01-10 site series for the AFRF.
- The Knife Creek block is in the IDFxm / IDFdk3 / IDFdk3-SBPSmk transition
  set.
- The report gives the block as 3,484 ha, Douglas-fir ~3,000 ha (87%), and
  elevation 720-1,020 m.
- The classification and keys are in `config/site_series.yaml` and
  `reference/AFRF-site-unit-report-2004.pdf`.
- Site index by site series and species is transcribed in
  `data/site_index/klinka_2004_site_index.csv` from Tables 8.2.1–8.2.4.
- The georeferenced site-series polygons are in the report's map pockets /
  CD-ROM, not the PDF. The spatial map is still required.
- Do not infer site series from BEC zone/subzone alone.

Public PSP analog
-----------------

The FAIB PSP compilation is public. A regional IDF Cariboo analog was built
from 51 first-measurement, Douglas-fir-leading, mature IDF PSPs in the Williams
Lake and 100 Mile House TSAs: 4,553 live trees at least 9.1 cm DBH, 45 stable
Weibull fits, and 24 synthetic one-hectare stem lists. Three stands ran through
FVS-BC with the corrected cycle-2 THINQFA; residual BA was 30–34 m²/ha against
the 29 m²/ha target.

This is **not** Knife Creek data. It is an interim analog for the FVS-BC
structural pilot and does not replace the KC CFI. See
`notes/reference/psp-idf-cariboo-stemlists.md`.

Current inventory snapshot
--------------------------

- VRI 2025 R1: 183 polygons over 3,533.13 ha; 160 polygons are FDI-leading;
  174 of 183 carry a site index.
- BEC map: IDFdk3 3,051.80 ha and IDFxm 481.33 ha. The current map does not
  show an SBPSmk polygon inside the SUP, despite the management-plan context.
- Harvest history: 60 openings over 2,478.73 ha, 1956-2023. The block has been
  heavily harvested for decades.
- Fire history: 2013 C20393 intersects 6.04 ha; the 1938 fire intersects
  62.11 ha; the 1937 fire 0.66 ha.
- Mule-deer habitat classes: High 1,327.68 ha, Moderate 1,135.66 ha, Low
  1,020.53 ha, Nil 6.15 ha. Almost the whole block is in a winter-range class.
- The legal UWR order text and the 2003 transition plan are acquired; the
  spatial UWR/HMZ layer and the AFRF site-series map are still required.

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
