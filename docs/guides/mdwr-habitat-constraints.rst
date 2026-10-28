Working with MDWR Habitat Constraints
=====================================

This guide explains how to use the mule-deer winter-range (MDWR) constraints in
the Knife Creek model. Read :doc:`../reference/mdwr-legal-basis` first; this
page is the operational checklist.

Default basis
-------------

The model defaults to **GWM 2007**. The AFRF MWP #3 Table 29 values are a named
alternative, not the legal curve.

.. list-table::
   :header-rows: 1
   :widths: 12 18 18 12 12 14

   * - Class
     - B (m²/ha)
     - BA >37.5 cm (m²/ha)
     - D (cm)
     - q
     - Reserve above D
   * - High
     - ≥29
     - ≥16
     - ≥70
     - 1.20–1.35
     - 0–2.9
   * - Moderate
     - ≥22
     - ≥11
     - ≥60
     - 1.25–1.35
     - 0–2.2
   * - Low
     - ≥16
     - ≥6
     - ≥50
     - 1.25–1.40
     - 0–1.6

The legal clump is 4–10 or more mature trees with interlocking crowns. The
maximum-diameter subgroup inside the clump is 2–5 trees. Do not use 2–5 as the
whole clump.

Default treatment: harvest surplus large trees
----------------------------------------------

The user decision is to harvest surplus large trees above the legal minimum.
The default GWM regime is a split cut:

1. ``THINABA`` removes surplus trees above 37.5 cm to the minimum large-tree
   basal area (16/11/6 m²/ha).
2. ``THINQFA`` thins the 0–37.5 cm component to ``B − large-tree BA`` with the
   legal q.

For High, the small-tree residual target is ``29 − 16 = 13`` m²/ha. In BC
``THINQFA`` units that is ``13 × 4.356 = 56.63`` ft²/ac. The ``THINABA`` target
is in m²/ha and its DBH fields are cm.

Example keyword sequence for High:

.. code-block:: text

   THINABA  2, 16.0, 1.0, 37.5, 999.0, 0.0, 999.0
   THINQFA  2, 0.0, 37.5, 0, 1.25, 5.0, 56.63

``THINQFA`` still writes its supplemental record (units 0 = basal area
ft²/ac). Cycle 2 with ``TIMEINT=,30`` applies the cut at year 30.

If the stand has less than the legal minimum large-tree BA, ``THINABA`` cannot
create trees. It cancels and the run must report the large-tree deficit. Do not
lower the target silently.

A retain-all-above-D variant is available as a sensitivity. It is not the
default because it forgoes the surplus large-tree harvest decision.

Clumps and canopy openings
--------------------------

FVS-BC is distance-independent. It cannot place 4–10-tree clumps or canopy
openings. The current workflow:

- carries large-tree TPH, BA, crown width and crown ratio from the
  after-treatment tree list;
- places retained large trees into 4, 6, 8 or 10-tree clumps at 3, 5 or 7 m
  radius in ``runbooks/build_clump_scenarios.py``;
- rasterizes within-clump crown closure at 0.25 m; and
- reports clump count, spacing, closure and total cover as **geometry
  scenarios**, not empirical clump statistics.

The public PSP stem maps are too sparse to estimate the real clump
distribution: of 45 stable plots, 11 are fully mapped, 3 have any mapped tree
≥50 cm, and only one has more than one (four trees). See
``notes/reference/psp-stem-map-limits.md``.

The canopy openings required by GWM 10 (0.3–1.0 tree heights, mean 0.5) are not
yet spatialized. A future ws4 spatial layer must check them together with the
4–10-tree clumps; a non-spatial FVS run cannot.

HMZ and the transition plan
---------------------------

Knife Creek is U-5-002 ``dwl_50``. The legal order Table 3 gives HMZ 1–5 as
``M, L, M, M, A``:

- HMZ 1: Low or Moderate only;
- HMZ 2: Low only;
- HMZ 3: Low or Moderate only;
- HMZ 4: Low or Moderate only;
- HMZ 5: all classes.

The HMZ is spatial. A stand-level BDq run cannot establish compliance. The HMZ
layer is acquired at ``data/habitat/mule_deer_hmz_kc.gpkg``: HMZ 1 M 738.29 ha,
2 L 1,217.15 ha, 3 M 320.51 ha, 4 M 1,213.33 ha, 5 A 0.00045 ha. The VRI × HMZ
crosswalk is ``data/habitat/kc_vri_hmz_overlay.csv``.

``ws4/dataset_kc_spatial_v1`` applies the matrix through track copies: M offers
Low/Moderate, L offers Low only, A offers all, U offers no treatment. It has
160 clipped VRI blocks, 92 tracks and 49 treatments, and ``ws4 validate``
passes. The current approved order and legal stand-structure map still need
verification.

The 2003 Knife Creek transition plan is acquired. Before 2026, GWM 13 requires
≥80% retention of pre-harvest merchantable Douglas-fir BA. The cutting cycle is
at least 30 years.

First GWM 2007 pilot
--------------------

The first GWM pilot is in ``ws4/gwm_pilot_v0``: five PSP-derived conditional
stands × three GWM classes × two methods = 30 transitions.

The default D-protected split removes surplus in the 37.5–D range and leaves
trees above D as the reserve. The retain-above-D method is the sensitivity.

The pilot passes 17 of 30 stand-structure checks:

- retain above D: 13/15;
- split 37.5–D: 4/15.

The split preserves the legal D floor but leaves the >D reserve, which makes q
too high in most High and Moderate cases (mean q 1.38 and 1.44 against the
1.35 upper limit). A full-range split can meet q and B but strips the largest
trees and leaves max DBH below D. High ``PSP-REG-001`` cannot meet the High
large-tree or D targets from its starting structure at all.

This is the key limitation: FVS can preserve D or harvest surplus large trees,
but it cannot selectively retain a small >D reserve while harvesting the rest.
That needs a tree-level reserve/marking rule or a pre-cut reserve assignment.

Selected clump-reserve rule
---------------------------

The selected rule is **option 1**. Start from the retain-above-D FVS result, then
apply a clump-reserve marking rule to the after-treatment tree list:

- group mature trees ≥37.5 cm into 4–10-tree clumps;
- reserve the largest 2–5 trees above D in each clump;
- harvest the remaining trees above D outside the reserve.

Until KC stem maps exist, the clump proxy is a DBH-ranked chunk of six trees,
and the reserve is the largest three above D. It is not spatial.

The retrospective marking result is **13/15 pass** (High 3/5, Moderate 5/5,
Low 5/5). Mean removed large BA is 1.07/2.64/5.12 m²/ha, with a >D reserve of
1.55/3.11/5.55 m²/ha. The two High failures are the low-large-tree starting
stands (`PSP-REG-001` and `PSP-REG-002`); they cannot meet the High large-tree
target or D floor from their initial structure.

This is a marking scenario, not a new FVS growth run. Do not compile it as
legal-compliant. See ``ws4/gwm_pilot_v0/clump_reserve.csv`` and
``clump_reserve_summary.csv``.

Status of the model
-------------------

``ws4/state_library_v0`` is a **legacy Table 29** library. It uses D 60/55/50
and a 50 cm policy threshold in places. It is useful as a structural pilot but
is not the default legal basis.

``ws4/state_library_v1`` is the provisional **GWM 2007 clump-reserve** library:
8 stands × 3 classes × 2 entries, 48 transitions, 192 curves. It passes 33/48
stand-structure checks (High 10/16, Moderate 11/16, Low 12/16). The clump proxy
is a DBH-ranked six-tree chunk, not spatial; the state IDs are per chain and the
graph is not closed. It is not a legal-compliance product.

The v1 graph is canonicalized to 23 states, 25 transitions and 6 terminal
states, with no cycles. A synthetic ws4 dataset (4 one-hectare blocks) compiles
and passes ``ws4 validate``; it is a structural fixture, not a KC operating
dataset. The next steps are to replace the proxy with a spatial clump rule,
join the acquired HMZ layer to the block/AU geometry, and replace the synthetic
dataset with a KC-calibrated compile.

The policy pilot in ``ws4/policy_pilot_v0/`` is also a Table 29 structural
scenario. It shows the trade-off between large-tree retention and total BA, but
it is not a legal-compliance run.

Acceptance checks
-----------------

Every GWM run report should include:

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Check
     - Failure message
   * - Total BA ≥ B minimum
     - “total BA below legal minimum for habitat class”
   * - BA >37.5 cm ≥ 16/11/6
     - “large-tree BA below legal minimum; THINABA may have canceled”
   * - Maximum DBH ≥ D or a documented reserve
     - “maximum DBH below Table 2 D”
   * - q in the legal range
     - “q outside legal range”
   * - clump post-processing uses 4–10 trees
     - “clump size outside legal range”
   * - HMZ class allows the objective
     - “objective not allowed in HMZ” or “HMZ layer missing”
   * - pre-2026 BA retention ≥80%
     - “transition retention below 80%”
   * - no clearcut / even-aged treatment
     - “even-aged treatment in KC”

If a check cannot be run, the report must say **not tested**; do not report it
as met.

Data still required
-------------------

- Legal UWR boundary, stand-structure habitat classes and HMZ GIS layer.
- KC CFI or released tree list.
- Georeferenced AFRF site-series map.
- FVS-BC calibration for KC, if available.
- The current approved UWR order at the time of a compliance claim.

Related pages
-------------

- :doc:`../reference/mdwr-legal-basis`
- :doc:`state-transition-design`
- :doc:`data-acquisition`
- ``notes/adr/0005-mdwr-legal-basis.md``
- ``notes/reference/mdwr-canopy-clump-requirements.md``
- ``notes/reference/psp-stem-map-limits.md``
