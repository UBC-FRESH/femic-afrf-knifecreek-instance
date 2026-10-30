AFRF Knife Creek PSP Data
=========================

Status: **field-data candidate**, pending publication clearance. It is not a
formal CFI and it is not a public dataset.

What the dataset is
-------------------

The AFRF Knife Creek permanent-sample-plot workbook contains 24 plots in three
blocks (B/C/D), measured in 1993, 1997, 2004, 2008 and 2013. It has tree-level
species, stem-map position, DBH, total height, crown dimensions, live-crown base
and vigor.

The design and measurement definitions are in:

- Marshall, P.L. 1996. *Response of uneven-aged Douglas-fir to alternative
  spacing regimes.* FRDA Report 242.
- Acquah, S.B. and Marshall, P.L. 2020. *Assessing Differences in Competitive
  Effects Among Tree Species in Interior Douglas-fir Forests.* Forests 11:167,
  doi:10.3390/f11020167.

FRDA 242 confirms:

- 24 plots, eight per block;
- each plot **0.05 ha**, rectangular **15.81 × 31.62 m**;
- pre-spacing measurements in 1989/1990; post-spacing 1993/1994; later
  remeasurements in 1997, 2004, 2008 and 2013;
- all living trees >1.3 m inside the plot tagged;
- all trees >10 cm DBH within a **5 m buffer outside** tagged;
- buffer-tree numbers carried a `B` suffix; this is the workbook `P = B`
  population;
- tree position recorded by bearing and distance from a plot stake;
- DBH, total height, live-crown base in four quarters, two perpendicular crown
  diameters, vigor, lean and bark thickness measured;
- vigor classes: 0 dead, 1 low, 2 moderate, 3 good.

The raw workbook is not committed. SHA-256:
``6d958ca93364e424ad41380da87c5f6da1e5ce5ce4fbd762226286d748a82ded``.
The full assumption audit is ``notes/reference/kc-afrf-psp-dataset.md``.

Plot mapping
------------

FRDA 242 Table 1 gives:

.. list-table::
   :header-rows: 1

   * - Block
     - Plots
     - Treatment
   * - B
     - 1, 2
     - C1
   * - B
     - 3, 4
     - U
   * - B
     - 5, 6
     - C2
   * - B
     - 7, 8
     - S
   * - D
     - 9, 10
     - S
   * - D
     - 11, 12
     - C1
   * - D
     - 13, 14
     - C2
   * - D
     - 15, 16
     - U
   * - C
     - 17, 18
     - C2
   * - C
     - 19, 20
     - U
   * - C
     - 21, 22
     - C1
   * - C
     - 23, 24
     - S

`S` = standard spacing, `C1` = 3 m clump spacing, `C2` = 5 m clump spacing,
`U` = control.

Column interpretation
---------------------

.. list-table::
   :header-rows: 1
   :widths: 20 46 34

   * - Field
     - Best interpretation
     - Status
   * - ``P``
     - ``I`` = plot tree, ``B`` = 5 m buffer/border tree
     - Confirmed by FRDA 242
   * - ``Plot``
     - Plot 1–24; block/treatment mapping above
     - Confirmed
   * - ``SP``
     - FD, SX, PL, EP/Ep, AT/At, W
     - Mostly confirmed; species authority for W/case variants still open
   * - ``X``, ``Y``
     - Tree position in **metres from plot centre**
     - Confirmed by P. Marshall, 2026-10-29
   * - ``V-YY``
     - Vigor 0 dead, 1 low, 2 moderate, 3 good
     - Confirmed by FRDA 242
   * - ``D-YY``
     - DBH in cm
     - Confirmed
   * - ``HT-YY``
     - Total height in m
     - Confirmed
   * - ``CW1-YY``, ``CW2-YY``
     - Two perpendicular crown diameters in m
     - Confirmed
   * - ``LC1-YY``…``LC4-YY``
     - Heights to live-crown base in four quarters, m
     - Confirmed
   * - ``TS``, ``TC``
     - 2013 Ministry of Forests status/class codes; unresolved
     - Not used
   * - ``D1``, ``D2``, ``DA``, ``DS``, ``WTA``
     - Unknown auxiliary measurements
     - Not documented; do not use
   * - ``HT13``
     - 2013 tree height in m
     - Confirmed
   * - ``CW1-93.1``
     - Typo for the first 1993 crown-width column
     - Confirmed; drop duplicate

X/Y units
---------

X/Y are **metres from the plot centre**, confirmed by P. Marshall on
2026-10-29. No conversion is applied. Observed ranges of about −24 to 40 and
−23 to 39 are metres relative to the centre; border trees can extend beyond the
rectangular plot.

Working rules and caveats
-------------------------

- Use 0.05 ha and expansion factor 20 for ``P = I``.
- Use ``P = B`` only for border/competition context.
- X/Y are metres from the plot centre, but absolute plot centres are not in the
  workbook. GPS coordinates should be available from AFRF.
- Do not carry a missing DBH forward silently.
- Do not use ``TS``/``TC``/``D1``/``D2``/``DA``/``DS``/``WTA`` until defined.
- Use live-crown ratio only after checking `LC` values against height.
- Growth intervals are 4, 7, 4 and 5 years, not annual.
- The study is a thinning experiment in dense patches, not a random sample of
  the whole Knife Creek block; the 2020 paper uses 16 Block C/D plots.
- Mountain pine beetle mortality affects lodgepole pine over 2004–2013.
- Raw tree-level data remain private until AFRF/PSP custodians clear release.

The published paper and FRDA reports contain no public data/code repository,
supplementary file or data-availability statement. FRDA 267 is a different
six-plot PSP study, not this workbook.

Remaining QC questions
----------------------

1. `TS` and `TC` code tables; both are 2013 MoF codes and are not used here.
2. Meaning of `D1`, `D2`, `DA`, `DS` and `WTA`.
3. GPS plot centres and block/treatment maps from AFRF.
4. Acquisition of the 2024 remeasurement.
5. Species authority for `W` and case variants; `W` is willow.
6. Publication clearance for the raw workbook.

First FVS-BC backtest
---------------------

``ws4/kc_psp_validation`` initialises FVS-BC from the 1993 interior trees,
expands each tree by 20 (0.05 ha), and grows without cutting with intervals of
4, 7, 4 and 5 years. The summary years are 1993, 1997, 2004, 2008 and 2013.
Version v1 corrects the cycle-year alignment in v0; do not reuse v0's
intermediate-year table.

.. list-table::
   :header-rows: 1

   * - Year
     - Obs BA
     - Pred BA
     - BA bias
     - Obs QMD
     - Pred QMD
     - Obs TPH
     - Pred TPH
   * - 2004
     - 33.14
     - 32.08
     - -1.06
     - 13.47
     - 13.34
     - 2,768
     - 2,865
   * - 2008
     - 33.20
     - 34.08
     - +0.88
     - 13.86
     - 13.92
     - 2,577
     - 2,795
   * - 2013
     - 35.38
     - 36.42
     - +1.04
     - 14.98
     - 14.61
     - 2,291
     - 2,713

BA and QMD are broadly plausible. TPH is overpredicted by 2013 (+422), driven
by the unthinned controls: +5.0 m²/ha BA and +1,504 TPH at 2013. C1 plots have
the largest BA underprediction (-2.3 m²/ha at 2013). Observed annual mortality
rises from 1.0% to 2.4% over the four intervals.

``MORTMULT`` sensitivity at 2013:

.. list-table::
   :header-rows: 1

   * - Multiplier
     - Pred BA
     - BA bias
     - Pred TPH
     - TPH bias
   * - 1.0
     - 36.42
     - +1.04
     - 2,713
     - +422
   * - 2.0
     - 33.38
     - -2.00
     - 2,417
     - +126
   * - 2.5
     - 32.13
     - -3.25
     - 2,290
     - -0.5
   * - 3.0
     - 31.04
     - -4.34
     - 2,176
     - -115
   * - 4.0
     - 28.71
     - -6.67
     - 1,955
     - -336

No global multiplier fits both TPH and BA. Multiplier 2.5 nearly matches TPH
but leaves BA low by 3.25 m²/ha; multiplier 2.0 is a compromise (BA -2.00,
TPH +126). The remaining BA error needs growth/species calibration. No stand
age or site index is assigned: the plots are uneven-aged and VRI age is not a
plot age. FVS-BC reports that site index is not used in this variant. This is a
structural backtest, not a calibration claim.

Calibration v1
--------------

``ws4/kc_psp_calibration`` is a species-group fixed-point calibration of
``BAIMULT`` and ``MORTMULT`` against 2013 BA and TPH. It converged at
iteration 28.

.. list-table::
   :header-rows: 1

   * - Parameter
     - FD
     - SE
     - PL
     - HW
   * - ``BAIMULT``
     - 1.6213
     - 1.3948
     - 1.0000
     - 1.0000
   * - ``MORTMULT``
     - 1.7593
     - 3.8261
     - 8.0000
     - 1.2012

2013 diagnostics:

.. list-table::
   :header-rows: 1

   * - Metric
     - Observed
     - Predicted
     - Bias
   * - BA (m²/ha)
     - 35.38
     - 36.38
     - +1.00
   * - QMD (cm)
     - 14.98
     - 15.76
     - +0.77
   * - TPH
     - 2,291
     - 2,313
     - +22.5

FD, SE and HW groups match closely; PL does not (observed 6.98 m²/ha and 620
TPH; predicted 40.38 and 1,100). The BC build has no active MPB module, and
``MORTMULT PL = 8`` is a bounded proxy, not a biological estimate.

The 1.0 m²/ha, 100 TPH and 0.5 cm limits used earlier were local placeholders,
not an external validation standard, and are no longer used as a pass/fail
gate. QMD and PL residuals remain.

Leave-one-block-out cross-validation is in ``ws4/kc_psp_cv``. The calibrated
parameters do not transfer consistently: BA bias worsens when B or C is held
out, QMD bias worsens when C or D is held out, and the fitted parameters vary
substantially between folds. The calibration is therefore diagnostic only; do
not use it to generate production transition curves.

No stand age or site index is assigned. The plots are uneven-aged and VRI age
is polygon-level context, not a plot age; the VRI summary is not backdated to
1993. FVS-BC also reports that site index is not used in this variant.

Observed transitions
--------------------

``data/psp/kc_afrf_psp_transitions.csv`` is the first directly observed
transition table: 24 plots × 4 intervals = 96 rows. It carries start/end BA,
TPH, QMD, mean height, large-tree BA/TPH, mortality, ingrowth and a Block C/D
flag. Species-group start/end BA/TPH are in
``kc_afrf_psp_transitions_species.csv``.

The working live-tree indicator is DBH presence because the `TS`/`TC` codes
remain unresolved. A tree whose first DBH appears after the interval start is
ingrowth; a start-live tree without an end DBH is mortality. No age or site
index is assigned. The table is derived data; raw tree records remain private.

State-support audit
-------------------

``data/psp/kc_afrf_psp_state_support.csv`` maps the 96 transitions to the
existing ws4 BA/QMD/large-tree bins and to a species-mix class. Support counts
are in ``kc_afrf_psp_state_support_summary.csv``.

Results:

- canonical bins: 9 start states, 18 start/end pairs, 12 repeated pairs,
  median 4 transitions per pair, maximum 16;
- species-mix bins: 20 start states, 36 pairs, 17 repeated, 19 one-off,
  median 1 transition per pair.

The canonical bins have enough repeated support for a coarse graph, but the
species-resolved bins do not. All observed QMD values fall below 20 cm and the
large-tree BA classes are concentrated below 6 m²/ha. No acceptance threshold
is applied; one-off pairs are retained.

Tree-level models
-----------------

``ws4/kc_psp_tree_models`` fits interval-start tree models to the 3,700+
tagged trees and validates them leave-one-block-out.

- Diameter increment RMSE: 0.087–0.102 cm/yr; bias -0.013 to +0.014 cm/yr.
- Survival Brier: 0.060–0.071; AUC: 0.805–0.896; mean predicted survival
  matches observed prevalence.
- Empirical block/treatment ingrowth still fails transfer: held-out
  observed/predicted totals are B 1/81, C 127/18 and D 35/64.

Start-cohort stand aggregate (no ingrowth): BA bias -0.04 m²/ha (MAE 1.49),
TPH bias +12.8 (MAE 91.1), QMD bias -0.02 cm (MAE 0.31). Growth and survival
are useful diagnostics. Ingrowth is strongly block-specific and must be
block-specific scenario data, not a transferable equation. The models do not
assign age or site index and are not yet a complete stand model.

State reconstruction
--------------------

``ws4/kc_psp_simulation`` applies the leave-one-block-out growth and survival
models to all 96 observed transitions.

| Mode | BA bias | BA MAE | TPH bias | TPH MAE | QMD bias | QMD MAE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cohort | -0.04 | 1.49 | -21.2 | 109.3 | +0.11 | 0.34 |
| conditional | -0.04 | 1.49 | +12.4 | 91.5 | -0.02 | 0.31 |

Cohort mode excludes ingrowth. Conditional mode uses the recruits actually
observed in the interval, so it is a reconstruction, not an ingrowth forecast.
BA and QMD reconstruct well; TPH is noisier. Ingrowth remains block-specific
scenario data.

The simulated end state matches the observed canonical BA/QMD/large-tree state
on **75 of 96 transitions (78.1%)**: B 26/32, C 26/32, D 23/32. The bins are
coarse — all QMD is below 20 cm and large-tree BA is concentrated below
6 m²/ha — so this is mainly a BA-class match, not a fine structural model.

Partial ws4 generator
---------------------

``ws4/kc_psp_generator`` starts from the 24 1993 plots, applies the tree-level
growth/survival models for 30 years in five-year steps, and adds an explicit
block/treatment ingrowth scenario.

It produces BA, TPH, QMD and large-tree BA curves only. It does not generate
volume, canopy cover, treatment response or a compiled ws4 dataset. The 30-year
projection is an extrapolation; no 30-year observed validation exists.

Regional space-for-time panel
-----------------------------

``data/psp/idf_cariboo_space_for_time_plots.csv`` and
``idf_cariboo_space_for_time_curves.csv`` hold 132 stratified IDF site states
from the Williams Lake and 100 Mile House TSAs. They span projected ages
44–248 years and 5.5–52.1 m²/ha BA, with 100-year no-cut FVS-BC curves at
10-year steps.

The 697 visits belong to 338 stable sites; repeated visits are time-for-time
data, not independent space-for-time states. This panel uses one first-
measurement state per site. It is not a growth chronology, and the curves are
not observed 50-year growth. The experimental BA-asymptote table is in
``idf_cariboo_ba_for_time.csv``; even 100 years is too short to trust its
asymptote as a carrying capacity.

What it unblocks
----------------

- real KC tree lists and stem maps;
- repeated-measurement growth, mortality and ingrowth;
- spatial clumps, openings and reserve-tree selection from actual stems;
- replacement of the regional IDF Cariboo PSP analog for the plots’ stand
  types.

What it does not unblock
------------------------

- whole-block inventory;
- legal-compliance determination;
- absolute spatial joins without plot centres;
- public release of raw field data.
