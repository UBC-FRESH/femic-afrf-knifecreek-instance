# KC AU calibrated FVS sensitivity

Status: **calibrated sensitivity**. The uncalibrated AU stage model remains the
structural baseline. This run applies the v1 24-plot PSP calibration to the AU
FVS-BC curves; it is not independent-site validation and not a legal-compliance
claim.

## What changed

The AU no-cut and multi-entry FVS-BC runs now carry the v1 `BAIMULT` and
`MORTMULT` parameters:

| Group | BAIMULT | MORTMULT |
| --- | ---: | ---: |
| FD | 1.6213 | 1.7593 |
| SE | 1.3948 | 3.8261 |
| PL | 1.0000 | 8.0000 |
| HW | 1.0000 | 1.2012 |

The calibrated growth is more conservative. Mean no-cut AU BA:

| Year | Uncalibrated | Calibrated |
| ---: | ---: | ---: |
| 0 | 30.6 | 30.6 |
| 50 | 55.7 | 46.8 |
| 100 | 66.6 | 51.2 |
| 200 | 73.2 | 50.7 |

## Structural result

The HMZ-mixed legal-candidate run on the calibrated stage graph meets **51 of
55** structural targets after retuning the reserve cap and AU q targets:

- 1 above, 3 below.
- All reserve ceilings, BA floors, large-tree floors and max-DBH floors pass.
- Four q-factor misses remain: `KC_IDFdk3_FDI_H.L`,
  `KC_IDFdk3_FDI_H.M`, `KC_IDFdk3_FDI_M.M` and `KC_IDFxm_FDI_L.M`.
- The q targets could not close those four groups; further q-target tuning
  either saturated or moved the measured q the wrong way.

The uncalibrated legal-candidate run still meets **55 of 55** structural
targets. The difference shows that the q/reserve treatment targets are
growth-sensitive; some q misses need a treatment or small-tree-retention
change, not another q-target adjustment.

## Interpretation

- The v1 calibration is not a drop-in replacement for the uncalibrated AU
  curves. It changes long-run BA enough to move reserve and q across the legal
  thresholds.
- The calibrated model is useful as a sensitivity and as a check on how
  confident the structural pass is.
- The 2024 temporal holdout supports the TPH calibration, but there is still no
  independent-site or whole-block validation.
- Do not present either run as legal compliance.

## Files

- `data/psp/kc_au_200y_calibrated/`
- `data/kc_ws4_recipe_au_stages_calibrated/`
- `ws4/dataset_kc_au_stages_calibrated_v1/`
- `ws4/runtime/kc_au_stages_calibrated/`
- `ws4/evidence/kc_au_stages_calibrated/`
