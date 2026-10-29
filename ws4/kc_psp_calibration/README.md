# AFRF Knife Creek PSP FVS-BC calibration v1

Status: **converged**, with residual diagnostics. There is no external
acceptance threshold; the earlier 1.0 m²/ha, 100 TPH and 0.5 cm limits were
local placeholders and are not used as a gate.

The calibration matches the non-pine species groups and total TPH, but it does
not reproduce the lodgepole-pine collapse or the observed QMD.

## Method

- 24 PSP plots, initialised from the 1993 interior trees with 20× expansion.
- Intervals 4, 7, 4 and 5 years; no cutting.
- Fixed-point update of FVS `BAIMULT` and `MORTMULT` by species group:
  FD, SE, PL and HW (EP + AT + OH).
- Target: 2013 species-group BA and TPH.
- Damped update: 0.6 per iteration.
- Bounds: `BAIMULT` 0.25–4.0; `MORTMULT` 0.25–8.0.
- Convergence: maximum relative parameter change < 0.02 and loss change
  < 1e-4, or 30 iterations.
- Stand age 64 and site index 14.5 m are VRI-derived stand-level priors from
  `data/inventory/vri_2025_kc_age_site_summary.json`. They are not plot-level
  joins. FVS-BC prints `SITE INDEX IS NOT USED IN THIS VARIANT`; changing
  age from 64 to 91 also did not change the backtest.

## Convergence

Converged at iteration **28** with maximum parameter change **0.0009** and loss
change **3.6×10⁻⁵**.

| Parameter | FD | SE | PL | HW |
| --- | ---: | ---: | ---: | ---: |
| `BAIMULT` | 1.6213 | 1.3948 | 1.0000 | 1.0000 |
| `MORTMULT` | 1.7593 | 3.8261 | 8.0000 | 1.2012 |

`PL` sits at the mortality bound. It is acting as a proxy for mountain pine
beetle, not as a fitted biological mortality rate.

## 2013 diagnostics

| Metric | Observed | Predicted | Bias |
| --- | ---: | ---: | ---: |
| BA (m²/ha) | 35.38 | 36.38 | +1.00 |
| QMD (cm) | 14.98 | 15.76 | +0.77 |
| TPH | 2,291 | 2,313 | +22.5 |

Species-group totals at 2013:

| Group | Obs BA | Pred BA | Obs TPH | Pred TPH |
| --- | ---: | ---: | ---: | ---: |
| FD | 744.91 | 744.69 | 48,780 | 48,854 |
| SE | 67.83 | 67.83 | 3,360 | 3,359 |
| HW | 29.35 | 30.52 | 2,220 | 2,220 |
| PL | 6.98 | 40.38 | 620 | 1,100 |

FD, SE and HW are close. PL is not: FVS cannot remove enough lodgepole pine
with the available mortality controls, and the BC build has no active MPB
module.

Trajectory diagnostics:

| Year | Obs BA | Pred BA | BA bias | Obs QMD | Pred QMD | Obs TPH | Pred TPH |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1997 | 29.66 | 28.42 | -1.24 | 12.38 | 12.46 | 3,010 | 2,906 |
| 2004 | 33.14 | 32.00 | -1.14 | 13.47 | 13.92 | 2,768 | 2,620 |
| 2008 | 33.20 | 33.92 | +0.72 | 13.86 | 14.74 | 2,577 | 2,478 |
| 2013 | 35.38 | 36.38 | +1.00 | 14.98 | 15.76 | 2,291 | 2,313 |

## Interpretation

- The calibrated model is usable as a **background growth/mortality engine**
  for FD/SE/HW, not as a complete KC stand model.
- Do not use `MORTMULT PL = 8` as a biological estimate; it is a bounded proxy.
- Do not use this run for legal compliance, whole-block inventory or a
  no-disturbance claim.
- QMD and PL residuals remain. More multiplier tuning would be false
  convergence; the next change is an explicit MPB/lodgepole removal scenario
  and size-specific mortality or ingrowth.

## Files

- `calibration_history.csv` — iteration, loss, parameter changes, parameters.
- `calibration_parameters.json` — final fitted parameters.
- `group_comparison.csv` — 2013 species-group targets vs predictions.
- `validation.csv`, `validation_summary.csv`, `fvs_predictions.csv`.
- `manifest.json` — convergence status, diagnostics, run hashes, caveats.
- Generator: `runbooks/fvs_calibrate_afrf_kc_psp.py`.
- VRI prior: `data/inventory/vri_2025_kc_age_site_summary.json`.
