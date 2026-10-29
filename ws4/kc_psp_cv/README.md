# AFRF Knife Creek PSP FVS-BC cross-validation v1

Status: **calibration not validated out of sample**.

This directory tests whether the species-group calibration transfers to a block
it was not fitted on. It is the check the in-sample calibration cannot provide.

## Method

- Leave one block out: fit on two blocks, evaluate the third.
- Folds: B held out, C held out, D held out.
- 8 plots per held-out block.
- Target: 2013 species-group BA and TPH.
- Baseline: the uncalibrated backtest in `ws4/kc_psp_validation`.
- No stand age or site index is assigned.

## Held-out 2013 results

| Held-out block | Baseline BA bias | Calibrated BA bias | Baseline QMD bias | Calibrated QMD bias | Baseline TPH bias | Calibrated TPH bias |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B | -0.33 | +2.05 | -0.78 | -0.07 | +723 | +596 |
| C | +0.62 | +1.74 | +0.16 | +2.12 | +135 | -338 |
| D | +2.83 | +2.45 | -0.52 | +0.27 | +408 | +155 |

Mean absolute BA error improves in every fold, but the bias and QMD results do
not transfer consistently. Calibration makes BA worse in B and C, QMD worse in
C and D, and TPH worse in C.

## Fold stability

| Held-out | Converged | Iterations | FD BAI | SE BAI | FD mort | SE mort | HW mort |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B | yes | 18 | 1.443 | 1.385 | 1.106 | 3.871 | 1.162 |
| C | yes | 23 | 1.799 | 1.415 | 2.048 | 4.012 | 1.441 |
| D | no | 30 | 1.586 | 1.188 | 1.862 | 0.523 | 1.150 |

The fitted parameters are not stable across folds. In particular, SE mortality
ranges from 0.52 to 4.01, and FD mortality from 1.11 to 2.05. That instability
is more important than the in-sample improvement.

## Conclusion

The calibrated FVS-BC parameters are **not validated**. They should not be used
to generate ws4 transition curves as if they were a KC-calibrated model.

Defensible uses now:

- uncalibrated FVS-BC as a structural gap-filler, with its biases reported;
- observed PSP transitions where the data support them;
- explicit treatment/disturbance scenarios, not hidden multiplier tuning.

The calibration remains useful as a diagnostic, not as a production parameter
set.

## Files

- `heldout_summary.csv` — fold-level 2013 comparison.
- `heldout_validation.csv` — plot/year observed, baseline and calibrated values.
- `fold_parameters.csv` — parameters fitted in each fold.
- `manifest.json` — fold design, tolerance, caveats.
- Generator: `runbooks/fvs_cross_validate_afrf_kc_psp.py`.
