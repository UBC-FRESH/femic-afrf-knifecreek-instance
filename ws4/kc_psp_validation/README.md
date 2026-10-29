# AFRF Knife Creek PSP FVS-BC backtest v0

Status: **structural backtest**, not a calibrated KC model.

## Method

- Initial state: 1993 interior trees (`P = I`) from the 24 AFRF PSP plots.
- Each tree is expanded by 20 (0.05 ha plot).
- FVS-BC runs without cutting to 1997, 2004, 2008 and 2013.
- Tree age 100 and site index FD 60 are placeholders.
- Height is filled from DBH when 1993 height is missing.
- Species mapped to BC codes: FD, SE (SX), PL, EP, AT, OH (W).

## Result

| Year | n | Obs BA | Pred BA | BA bias | BA MAE | Obs QMD | Pred QMD | Obs TPH | Pred TPH | TPH bias |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1993 | 24 | 26.66 | 26.17 | -0.49 | 0.50 | 11.60 | 11.60 | 3,091 | 3,090 | -0.4 |
| 1997 | 24 | 29.66 | 28.42 | -1.24 | 1.37 | 12.38 | 12.26 | 3,010 | 3,002 | -7.9 |
| 2004 | 24 | 33.14 | 30.50 | -2.64 | 3.34 | 13.47 | 12.88 | 2,768 | 2,921 | 153.7 |
| 2008 | 24 | 33.20 | 32.42 | -0.78 | 3.44 | 13.86 | 13.48 | 2,577 | 2,846 | 269.7 |
| 2013 | 24 | 35.38 | 34.50 | -0.88 | 3.83 | 14.98 | 14.05 | 2,291 | 2,777 | 486.6 |

By block (mean error over all years):

| Block | BA error | QMD error | TPH error |
| --- | ---: | ---: | ---: |
| B | -1.76 | -0.57 | +312 |
| C | -1.43 | -0.16 | +40 |
| D | -0.43 | -0.48 | +189 |

By treatment:

| Treatment | BA error | QMD error | TPH error |
| --- | ---: | ---: | ---: |
| C1 | -2.88 | -0.62 | +21.8 |
| C2 | -1.50 | -0.23 | -10.5 |
| S | -0.89 | -0.24 | +31.2 |
| U | +0.44 | -0.52 | +678.9 |

## Interpretation

- BA and QMD trajectories are broadly plausible: 2013 BA bias -0.88 m²/ha, QMD bias -0.93 cm.
- TPH is increasingly overpredicted: FVS retains too many stems because it does not reproduce the observed mortality, especially in the unthinned controls (+679 TPH average).
- The initial 1993 state matches observed BA/QMD/TPH almost exactly because it is the observed state.
- The largest BA underprediction is in C1 plots (-2.88 m²/ha average).
- This does not establish calibration. It identifies where calibration or measured transition curves are needed.

## Caveats

- Tree age and site index are placeholders.
- Height fill for missing 1993 heights is crude.
- Species are mapped to BC codes; `W` is mapped to `OH`.
- No cut is applied; this is a growth/mortality test, not a treatment test.
- The 24-plot thinning experiment is not a whole-block sample.
- The raw workbook is private; only derived validation tables are committed.

## Files

- `validation.csv` — observed vs predicted by plot/year.
- `validation_summary.csv` — year summary above.
- `fvs_predictions.csv` — FVS summaries.
- `manifest.json` — run hashes, placeholders, caveats.
- Generators: `runbooks/ingest_afrf_kc_psp.py`,
  `runbooks/fvs_validate_afrf_kc_psp.py`.
