# AFRF Knife Creek PSP dataset: assumptions and caveats

## Status

Field-data candidate, not a confirmed formal CFI and not a published dataset.
The raw workbook is held in the workspace source set, not in git. Most of the
plot design and measurement metadata has now been resolved from the published
study; the remaining unresolved fields are listed below.

## Sources

- AFRF Knife Creek PSP workbook, 24 sheets, 5,388 tree rows.
  SHA-256: `6d958ca93364e424ad41380da87c5f6da1e5ce5ce4fbd762226286d748a82ded`.
- Marshall, P.L. 1996. *Response of uneven-aged Douglas-fir to alternative
  spacing regimes: analysis of the initial impacts of the spacing regimes.*
  FRDA Report 242. 34 pp. SHA-256:
  `b6d90bd82f76c5696a54a35fbb14110253c963bf130888855320e685a18573eb`.
- Acquah, S.B. and Marshall, P.L. 2020. *Assessing Differences in Competitive
  Effects Among Tree Species in Interior Douglas-fir Forests.* Forests
  11(2):167, doi:10.3390/f11020167. SHA-256:
  `36f60be81e14fa63d19247afa4a626e37b99eb59d4853694d68467f08fbcc9bb`.
- Marshall, P.L. and Wang, Y. 1996. *Growth of uneven-aged interior
  Douglas-fir stands as influenced by different stand structures.* FRDA Report
  267. This is a **different six-plot PSP study**, not the 24-plot spacing
  experiment. It is not the data dictionary for this workbook.

No public code repository, data repository, supplementary file or data
availability statement was found in the 2020 paper or the FRDA reports. The
paper cites FRDA 242/267 for the design and prior analyses.

## Confirmed from FRDA 242

- The study is AFRF Project 88-11: spacing regimes to develop mule-deer winter
  range habitat.
- 24 permanent plots in three blocks (B/C/D), eight plots per block.
- Each plot is **0.05 ha**, rectangular, **15.81 × 31.62 m**.
- Plot corners were surveyed and marked; plots were relocated after spacing.
- Pre-spacing measurements: Block B August 1989; Blocks C/D August 1990.
- Post-spacing measurements: 1993 and 1994; later remeasurements in 1997, 2004,
  2008 and 2013 (2020 paper).
- All living trees >1.3 m tall inside the plot were tagged and measured.
- All trees >10 cm DBH within a **5 m buffer strip outside** the plot were
  tagged. Their tree numbers were followed by `B`; the workbook `P` column
  carries `I`/`B`. So **`P = I` is the plot population and `P = B` is the
  buffer/border population**.
- Tree location was recorded as bearing and distance from the centre stake,
  using a corner stake when sight lines failed. Distance was measured with a
  cloth tape to the nearest 0.1 m.
- Measurements: species, DBH at 1.3 m to 0.1 cm, total height to 0.1 m, heights
  to the base of the live crown in four quarters, crown diameter in two
  perpendicular directions (parallel and at right angles to the strip), tree
  vigor, lean angle and distance, and bark thickness.
- Tree vigor classes: `0` dead; `1` alive with low future potential; `2`
  moderate potential; `3` good potential.
- Dead-tree DBH/height are retained in the repeated-measurement columns; the
  paper discusses mortality and ingrowth but does not provide the workbook’s
  `TS`/`TC` codes.

## Plot, block and treatment mapping

Confirmed from FRDA 242 Table 1:

| Block | Plots | Treatments |
| --- | --- | --- |
| B | 1, 2 | C1 |
| B | 3, 4 | U |
| B | 5, 6 | C2 |
| B | 7, 8 | S |
| D | 9, 10 | S |
| D | 11, 12 | C1 |
| D | 13, 14 | C2 |
| D | 15, 16 | U |
| C | 17, 18 | C2 |
| C | 19, 20 | U |
| C | 21, 22 | C1 |
| C | 23, 24 | S |

`S` = standard spacing; `C1` = 3 m clump spacing; `C2` = 5 m clump spacing;
`U` = control. The workbook sheets use plot numbers 1–24, so this mapping is
usable.

## Column assumptions after reading the sources

| Column | Best interpretation | Status |
| --- | --- | --- |
| `Plot` | Plot number 1–24; block/treatment mapping above | Confirmed |
| `P` | `I` = plot tree; `B` = 5 m buffer/border tree | Confirmed by FRDA 242 p. 4 |
| `T` | Tree number; buffer numbers followed by B in field, numeric here | Confirmed |
| `SP` | Species code: FD, SX, PL, EP/Ep, AT/At, W | Mostly confirmed; `W` likely willow; confirm authority list |
| `X`, `Y` | Tree position, probably **feet from plot centre** | Strong inference, not a workbook label |
| `TS` | Tree status; `1` likely live, `3` likely dead | Not documented; verify |
| `V-YY` | Vigor 0–3 | Confirmed by FRDA 242 p. 5 |
| `TC` | Tree/crown class 0–8 | Not documented; verify |
| `D1`, `D2`, `DA`, `DS`, `WTA` | Unknown auxiliary measurements | Not documented; do not use |
| `D-YY` | DBH in cm by year | Confirmed by methods and values |
| `HT-YY` | Total height in m by year | Confirmed by methods |
| `CW1-YY`, `CW2-YY` | Two perpendicular crown diameters in m | Confirmed by methods |
| `LC1-YY`…`LC4-YY` | Heights to live-crown base in four quarters, m | Confirmed by methods |
| `HT13`, `CW1-93.1` | Duplicate/renamed 2013 or repeated column | Unknown; drop duplicates after checking values |

### Why X/Y are probably feet

The plot is 15.81 × 31.62 m (half-width 7.9 m, half-length 15.8 m) with a 5 m
buffer. The observed X/Y ranges are roughly −24 to 40 and −23 to 39. If metres,
they exceed the plot and buffer dimensions. If feet, 40 ft = 12.2 m and 39 ft =
11.9 m, which fits within the 5 m buffer around the rectangle. The source says
distances were measured to 0.1 m, so the spreadsheet likely converted to feet.
This is still an inference, not a header definition.

## Working assumptions

1. Plot area is 0.05 ha; expansion is 20 per tree for `P = I`.
2. Use `P = I` for density/BA; use `P = B` only for border/competition context.
3. Plot population is all living trees >1.3 m tall; LiDAR does not see these
   understory stems, so LiDAR cannot replace this dataset.
4. DBH is cm; height and crown dimensions are m.
5. `X/Y` are relative to plot centre, probably feet; no absolute coordinates.
6. `TS = 3` is treated as dead only after confirmation.
7. `V = 0` is dead; `V = 1/2/3` is low/moderate/good vigor.
8. `LC1–4` are live-crown base heights in four quarters; crown ratio is
   `(HT − mean(LC)) / HT` after a range check.
9. `CW1/CW2` are perpendicular crown diameters; crown radius is mean/2.
10. 2013 is post-growing-season; earlier measurements are pre-growing-season.
    Growth intervals are 4, 7, 4 and 5 years.
11. The study is a thinning experiment in dense patches, not a random sample of
    the whole Knife Creek block. The 2020 paper uses 16 Block C/D plots.
12. The raw workbook remains private until AFRF/PSP custodians clear release.

## Remaining caveats

- The workbook has no formal data dictionary for `TS`, `TC`, `D1`, `D2`, `DA`,
  `DS`, `WTA`, `HT13` or duplicate columns.
- X/Y units and origin are a strong inference, not a documented header.
- Plot 1 and other treated plots have post-spacing populations; pre-spacing
  Table 1 values should not be compared directly with 1993 tree counts.
- The 5 m buffer population is essential for competition but must not be used
  for plot density or BA.
- No absolute plot centres, block polygons or treatment polygons are in the
  workbook.
- Small 0.05 ha plots, edge effects and thinning-experiment selection limit
  extrapolation to the whole block.
- Mountain pine beetle mortality affected lodgepole pine over 2004–2013.
- Raw tree-level publication status is unresolved.

## Remaining QC questions (only the genuinely unresolved ones)

1. What are the exact `TS` and `TC` codes?
2. What are `D1`, `D2`, `DA`, `DS`, `WTA`, `HT13` and `CW1-93.1`?
3. Are `X/Y` feet from plot centre, and can the coordinate conversion be
   documented?
4. Are dead-tree DBH/height retained in all year columns, and how should
   mortality/ingrowth be handled?
5. Which species authority should be used for `W` and case variants?
6. Can absolute plot centres, block polygons and treatment polygons be supplied?
7. Is the raw workbook cleared for publication?

## What this unblocks

- real KC species, DBH, height, crown and stem-map records;
- repeated-measurement growth, mortality and ingrowth;
- spatial clumps, openings and reserve-tree selection from actual stems;
- replacement of the regional IDF Cariboo PSP analog for the plots’ stand
  types.

## What it does not unblock

- whole-block KC inventory;
- a legal-compliance determination;
- absolute spatial joins to VRI/HMZ/LiDAR;
- public release of raw field data.

## First FVS-BC backtest

`ws4/kc_psp_validation/` initialises FVS-BC from the 1993 interior-tree
measurements, expands each tree by 20, and grows without cutting to 1997, 2004,
2008 and 2013. Results:

- 2013 BA 36.42 predicted vs 35.38 observed (+1.04 m²/ha);
- 2013 QMD 14.61 vs 14.98 cm (-0.38 cm);
- 2013 TPH 2,713 vs 2,291 (+422), so FVS under-reproduces mortality;
- controls have the largest 2013 error (+5.0 m²/ha BA, +1,504 TPH); C1 has
  the largest BA underprediction (-2.3 m²/ha at 2013).

Version v1 corrects the v0 cycle-year alignment; v0 intermediate years are
superseded.

Observed annual mortality rises from 1.0% (1993–97) to 2.4% (2008–13). FVS
`MORTMULT` sensitivity shows the trade-off: at 2013, multiplier 1 gives BA
+1.04 and TPH +422; multiplier 2.5 gives BA -3.25 and TPH -0.5; multiplier 3
gives BA -4.34 and TPH -115. No global multiplier fits both. A site-index 80
vs 60 test produced no change. No stand age is assigned: the plots are
uneven-aged and VRI age is not a plot age. FVS-BC does not use site index. See
`ws4/kc_psp_validation/README.md`.

## Calibration v1

`ws4/kc_psp_calibration/` fits species-group `BAIMULT` and `MORTMULT` to
2013 BA/TPH with a damped fixed-point update. It converged at iteration 28.
Final parameters: FD BAI 1.6213 / mort 1.7593; SE 1.3948 / 3.8261; PL 1.0 /
8.0; HW 1.0 / 1.2012. 2013 totals: BA 36.38 vs 35.38 (+1.00), QMD 15.76 vs
14.98 (+0.77), TPH 2,313 vs 2,291 (+22.5). FD/SE/HW match; PL is unmodelled
MPB (40.38 vs 6.98 BA; 1,100 vs 620 TPH). The earlier 0.5 cm QMD threshold was
ad hoc and is no longer a gate. No stand age is assigned: the plots are
uneven-aged and VRI age is not a plot age. FVS-BC does not use site index.
See `ws4/kc_psp_calibration/README.md` and
`data/inventory/vri_2025_kc_age_site_summary.json` (context only).

## Cross-validation

`ws4/kc_psp_cv/` fits on two blocks and evaluates the third. The calibrated
parameters do not transfer consistently: BA bias worsens when B or C is held
out, QMD bias worsens when C or D is held out, and SE mortality ranges from
0.52 to 4.01 across folds. The calibration is diagnostic only; the uncalibrated
backtest is the defensible structural baseline.

## Observed transition table

`data/psp/kc_afrf_psp_transitions.csv` has 96 plot-interval rows (24 plots × 4
intervals) with start/end BA, TPH, QMD, height, large-tree metrics, mortality,
ingrowth and a Block C/D flag. Species-group BA/TPH are in
`kc_afrf_psp_transitions_species.csv`. DBH presence is the working live-tree
indicator because `TS`/`TC` remain unresolved. A tree first measured after the
interval start is ingrowth; a start-live tree with no end DBH is mortality.
No age or site index is assigned. This is the primary observed evidence for
the next state library; its support is sparse (24 plots, four intervals) and
it is not a whole-block sample.

## State-support audit

`data/psp/kc_afrf_psp_state_support.csv` maps the 96 transitions to the
existing canonical BA/QMD/large-tree bins and to a species-mix class.
Canonical bins: 9 start states, 18 pairs, 12 repeated, median 4 transitions,
max 16. Species-mix bins: 20 start states, 36 pairs, 17 repeated, 19 one-off,
median 1. The canonical bins support only a coarse graph; species-resolved
states are too sparse for an empirical ws4 matrix. All observed QMD values are
below 20 cm. No acceptance threshold is applied.

## Tree-level models

`ws4/kc_psp_tree_models/` fits diameter increment, survival and ingrowth from
the tagged trees and validates leave-one-block-out. Diameter RMSE is
0.087–0.102 cm/yr; survival Brier is 0.060–0.071 with AUC 0.805–0.896. The empirical
block/treatment ingrowth distribution still fails transfer (held-out
observed/predicted totals: B 1/81, C 127/18, D 35/64). Growth and survival are
diagnostics; ingrowth must be block-specific scenario data. Start-cohort stand
aggregate (no ingrowth): BA bias -0.04 m²/ha (MAE 1.49), TPH +12.8 (MAE 91.1),
QMD -0.02 cm (MAE 0.31).

## State reconstruction

`ws4/kc_psp_simulation/` applies leave-one-block-out growth/survival models
to the 96 transitions. Cohort (no ingrowth): BA bias -0.04 (MAE 1.49), TPH
-21.2 (MAE 109.3), QMD +0.11 (MAE 0.34). Conditional (observed recruits): BA
-0.04 (MAE 1.49), TPH +12.4 (MAE 91.5), QMD -0.02 (MAE 0.31). BA/QMD
reconstruct well; TPH is noisier. Conditional ingrowth is not an ingrowth
forecast. Simulated end states match the observed canonical BA/QMD/large-tree
state on 75/96 transitions (78.1%); the bins are coarse and this is mainly a
BA-class match.
