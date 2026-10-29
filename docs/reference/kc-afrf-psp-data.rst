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
     - Tree position, probably **feet from plot centre**
     - Strong inference; not a workbook label
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
     - Tree status / tree class, codes unresolved
     - Not documented
   * - ``D1``, ``D2``, ``DA``, ``DS``, ``WTA``
     - Unknown auxiliary measurements
     - Not documented; do not use
   * - ``HT13``, ``CW1-93.1``
     - Duplicate/renamed 2013 or repeated columns
     - Unknown; drop duplicates after checking values

Why X/Y are probably feet
-------------------------

The plot is 15.81 × 31.62 m, with half-width 7.9 m and half-length 15.8 m, plus
a 5 m buffer. Observed X/Y ranges are roughly −24 to 40 and −23 to 39. In
metres they exceed the plot and buffer; in feet, 40 ft = 12.2 m and 39 ft =
11.9 m, which fits the buffer around the rectangle. The source says distances
were measured to 0.1 m, so the spreadsheet probably converted to feet. This is
an inference, not a header definition.

Working rules and caveats
-------------------------

- Use 0.05 ha and expansion factor 20 for ``P = I``.
- Use ``P = B`` only for border/competition context.
- No absolute plot centres are present; do not join to VRI, HMZ or LiDAR.
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

1. Exact `TS` and `TC` codes.
2. Meaning of `D1`, `D2`, `DA`, `DS`, `WTA`, `HT13` and duplicate columns.
3. Final confirmation of the X/Y unit conversion and origin.
4. Dead-tree DBH/height handling and ingrowth rules.
5. Species authority for `W` and case variants.
6. Absolute plot centres, block polygons and treatment polygons.
7. Publication clearance for the raw workbook.

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
TPH +126). The remaining BA error needs growth/species calibration. Stand age
64 and site index 14.5 m come from the VRI stand-level summary; FVS-BC reports
that site index is not used in this variant, and age 64 versus 91 produced the
same backtest. This is a structural backtest, not a calibration claim.

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

Stand age 64 and site index 14.5 m come from the VRI stand-level summary
(``data/inventory/vri_2025_kc_age_site_summary.json``), not a plot-level join.
FVS-BC prints that site index is not used in this variant; age 64 versus 91
also produced the same backtest.

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
