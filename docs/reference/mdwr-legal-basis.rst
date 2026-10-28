MDWR Legal Basis
================

This page is the user-facing contract for mule-deer winter-range (MDWR)
constraints on the Knife Creek block. It records what the legal order requires,
how that differs from the AFRF Management and Working Plan #3 (MWP #3), and
what the model may and may not claim.

The default policy basis is **GWM 2007**. The AFRF Table 29 interpretation is a
named alternative, not the legal curve.

Decision record: ``notes/adr/0005-mdwr-legal-basis.md``.
Detailed source review: ``notes/reference/mdwr-canopy-clump-requirements.md``.
Source URLs and checksums: ``notes/reference/mdwr-source-index.md``.

Sources
-------

- **GWM order**: *Amended Order #U-5-001, U-5-002 and U-5-003 — Ungulate
  Winter Ranges, Cariboo Chilcotin Land Use Plan, Shallow and Moderate
  Snowpack* (signed February 2007). Knife Creek is U-5-002 ``dwl_50``.
- **Part 1a**: Dawson et al. 2007, LMH 60, *Management Plan for Shallow and
  Moderate Snowpack Zones*.
- **Part 1b**: Dawson et al. 2006, LMH 59, *Management Plan for Transition and
  Deep Snowpack Zones*. Included for contrast; it does not apply to Knife
  Creek.
- **Part 3**: CCLUP Mule Deer Strategy Committee 2003, *Transition Period
  Harvest Opportunities: Knife Creek*.
- **Extension Note 25A**: Dawson and Armleder 2000, *Structural Definitions for
  Management of Mule Deer Winter Range Habitat in the Interior Douglas-fir
  Zone*.
- **LMH 13**: Armleder, Dawson and Thomson 1986, *Handbook for Timber and Mule
  Deer Management Co-ordination on Winter Ranges in the Cariboo Forest
  Region*.
- **MWP #3**: AFRF *Management and Working Plan #3*, January 1, 2007.
- **FSP 2007**: AFRF *Forest Stewardship Plan 2007–2012*.

The PDFs are kept in the workspace source set, not in git:
``/srv/shared-data/gep/ws4/sources/afrf-mule-deer/``. The repository notes carry
the citations and extracted requirements.

Legal clump and canopy-opening requirement
------------------------------------------

GWM 10, Schedule 1, page 5:

   A clumpy distribution of Douglas-fir trees, with clumps containing 4–10 or
   more mature trees with interlocking crowns.

The same measure requires:

- small canopy openings 0.3–1.0 times the height of mature trees in diameter,
  with an average of 0.5 times mature tree height;
- a minimum 30-year cutting cycle;
- no material adverse damage to residual trees; and
- skid trails covering no more than 10% of the net harvested area in high or
  moderate stands.

The 2–5 figure in MWP #3 is **not** the whole clump. MWP #3 page 87 says the
maximum-diameter class is distributed in groups of 2–5 trees. That is a
subgroup inside the legal 4–10-tree mature clump.

.. warning::

   The earlier ``policy_pilot_v0`` used 2–5-tree clumps. That was a misreading
   of the maximum-diameter subgroup. The current clump scenarios use 4, 6, 8
   and 10 trees.

Stand-level legal targets
-------------------------

GWM 10, Tables 1–2, pages 6–7, for IDFdk3/IDFdw:

.. list-table::
   :header-rows: 1
   :widths: 16 20 20 12 18 18

   * - Habitat class
     - Total BA ≥12.5 cm
     - BA in stems ≥37.5 cm
     - Table 2 D
     - q (5 cm classes)
     - Large-tree reserve above D
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

The IDFxm/xw high class has a lower total-B and D (≥27 m²/ha, ≥65 cm); Knife
Creek is IDFdk3/IDFdw, so the table above is the relevant row.

Consequences:

- the large-tree threshold is **37.5 cm DBH**, not 50 cm;
- High and Moderate Table 2 D are 70 and 60 cm, not 60 and 55 cm;
- a large-tree reserve above D is allowed; and
- crown closure is not the stand-level defining attribute.

Crown closure is regional and landscape-scale
---------------------------------------------

LMH 13 pages 24–25 defines crown-closure classes using trees taller than
10.4 m and older age classes:

.. list-table::
   :header-rows: 1

   * - Habitat class
     - Crown closure
   * - Low
     - 16–35%
   * - Moderate
     - 36–65%
   * - High
     - >65%

LMH 13 page 31 gives approximate winter-range composition:

.. list-table::
   :header-rows: 1

   * - Snowpack zone
     - Low
     - Moderate
     - High
   * - Shallow
     - ~40%
     - ~40%
     - ~20%
   * - Moderate
     - ~33%
     - ~33%
     - ~33%
   * - Deep
     - ~33%
     - 0%
     - ~66%

Extension Note 25A page 2 states that crown closure is **not** a stand-level
defining attribute. At the stand scale the legal test is basal area, BA >37.5
cm, percent Douglas-fir, and the BDq curve. Do not turn “high habitat” into a
single 65% canopy-cover target at the stand scale; the legal stand-level
surrogate is the BA table plus the 4–10-tree clump and canopy-opening pattern.

Table 29 is the AFRF alternative
--------------------------------

MWP #3 Table 29 uses:

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

The total-B values match the legal minima, but the D values do not: the legal
order Table 2 values are 70/60/50 cm. Table 29 also omits the legal large-tree
BA targets (16/11/6 m²/ha above 37.5 cm) and the reserve above D.

Therefore:

- **GWM_2007** is the default model basis;
- **AFRF_MWP3_TABLE29** is a named alternative for comparison with the AFRF
  management plan;
- a Table 29 run must be labelled an AFRF interpretation, not compliance; and
- the two bases must not be mixed in one state graph or optimization run.

Knife Creek transition and HMZ
------------------------------

The 2003 Knife Creek transition plan is the CCLUP transition-period document.
It refers to Part 1a for stand-level objectives. The legal order Table 3 gives
the Knife Creek row for U-5-002 ``dwl_50``:

.. list-table::
   :header-rows: 1

   * - Habitat management zone
     - 1
     - 2
     - 3
     - 4
     - 5
   * - Knife Creek ``dwl_50``
     - M
     - L
     - M
     - M
     - A

Codes: ``L`` = potential harvest only in Low areas; ``M`` = Low or Moderate;
``A`` = all areas, managed to the designated High/Moderate/Low objective;
``X`` = no harvest; ``P`` = park/protected.

The order also states, at page 2 paragraph 5, that the GWMs do not apply to
primary forest activities over >10 ha in the Moderate Snowpack zone where ≥70%
of the area is north-facing (315°–60°) with slope >20%, in listed UWRs
including Knife Creek. This is a potential exemption, not a default. It needs
the spatial UWR/HMZ layer and an explicit area test.

Transition-period limits:

- GWM 13 requires at least **80% of pre-harvest merchantable Douglas-fir basal
  area** to be retained before 2026.
- Part 1a Table 1 repeats the 80% rule and the minimum 30-year cutting cycle.
- The 2007 FSP adds the AFRF operational interpretation: single-tree selection
  removes ≤20% of pre-harvest BA and leave trees are clumped.

Default model contract
----------------------

The model uses GWM 2007 by default:

- ``basis: GWM_2007``;
- legal B 29/22/16; BA >37.5 ≥16/11/6; Table 2 D ≥70/60/50;
- q 1.20–1.35 / 1.25–1.35 / 1.25–1.40;
- reserve 0–2.9 / 0–2.2 / 0–1.6 m²/ha above D;
- clumps of 4–10 or more mature trees with interlocking crowns;
- maximum-diameter subgroup of 2–5 trees inside the clump;
- canopy openings 0.3–1.0 tree heights, mean 0.5;
- cutting cycle at least 30 years; and
- before 2026, retain at least 80% of pre-harvest merchantable Douglas-fir BA.

**Surplus large trees above the minimum are harvestable.** The default
treatment is a split cut: ``THINABA`` above 37.5 cm to the minimum large-tree
BA, then ``THINQFA`` on 0–37.5 cm to ``B − large-tree BA``. A retain-all-above-D
variant is available as a sensitivity, not the default.

The legacy ``ws4/state_library_v0`` was built on Table 29 and is not the default
basis. ``ws4/state_library_v1`` is the provisional GWM 2007 clump-reserve
library: 48 transitions, 33/48 stand-structure checks pass, graph not closed,
and the clump rule uses a non-spatial DBH-ranked proxy. It is not a
legal-compliance product.

First GWM pilot
---------------

``ws4/gwm_pilot_v0`` is the first stand-structure feasibility test: five
PSP-derived conditional stands × three GWM classes × two methods. It passes
17/30 checks. Retain-above-D passes 13/15; the D-protected split passes 4/15.
The split preserves max DBH but leaves the >D reserve, so q is too high in most
High and Moderate cases. A full-range split meets q but strips the largest
trees and leaves max DBH below D.

The selected rule is therefore a post-FVS clump reserve: run the retain-above-D
BDq cut, group mature trees into 4–10-tree clumps, reserve the largest 2–5 trees
above D per clump, and harvest the rest above D. With a DBH-ranked six-tree
proxy, this passes **13/15** cases (High 3/5, Moderate 5/5, Low 5/5) and
harvests 1.07/2.64/5.12 m²/ha of large BA on average. The two High failures are
the low-large-tree starting stands. This is a retrospective marking scenario,
not a new FVS growth run, and not a compliance result.

What is not established
-----------------------

- The legal UWR boundary, stand-structure classes and HMZ spatial GIS layer are
  not yet in the repo. The order text and HMZ matrix are not enough for a
  compliance claim.
- The KC CFI or released tree list is still missing.
- No KC-calibrated FVS-BC case exists.
- Canopy-opening layout and the 4–10-tree clump pattern are post-processing
  constraints; FVS-BC is distance-independent.
- The PSP-derived IDF Cariboo stands are a regional analog, not KC data.

Related files
-------------

- ``config/mdwr_regimes.yaml`` — default basis, legal targets, Table 29
  alternative, HMZ matrix.
- ``config/fvsbc/regimes.yaml`` — GWM split regimes and Table 29 alternatives.
- ``data/benchmarks/mdwr_gwm2007_targets.csv``
- ``data/benchmarks/mdwr_gwm2007_clump.csv``
- ``data/benchmarks/mdwr_gwm2007_knife_creek_hmz.csv``
- ``ws4/policy_pilot_v0/`` — structural policy pilot; not the legal default.
- ``notes/adr/0005-mdwr-legal-basis.md``
- ``notes/reference/mdwr-canopy-clump-requirements.md``
- ``notes/reference/mdwr-source-index.md``
