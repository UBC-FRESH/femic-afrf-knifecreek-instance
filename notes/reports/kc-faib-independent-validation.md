# KC FAIB independent-site validation

Status: **independent-site growth validation**. The FAIB sites are independent
of the 24 Marshall plots. This is still not a whole-block inventory validation
and not a legal-compliance claim.

## Data

The FAIB archive has 544 IDFdk/IDFxm sites, of which 403 have repeated
measurements. After requiring:

- at least two measurements,
- at least 10 years between first and last measurement,
- at least 50% Douglas-fir basal area at the first measurement,

the validation panel is **92 sites**. Each site contributes one first-to-last
interval. The 24 Marshall plots are excluded.

The validation compares trees present at both measurements. This deliberately
excludes the FAIB small-tree ingrowth pulse, which FVS-BC does not reproduce;
total end-of-period TPH would otherwise confound recruitment with model error.

## Models compared

- **Uncalibrated** FVS-BC.
- **v1 local calibration** fitted to the 24 Marshall plots (2013 target).
- **v2c regional calibration** fitted to the 92 FAIB sites: FD `BAIMULT` 1.2,
  FD `MORTMULT` 2.8; other species groups as v1.

## FAIB result, 92 sites

| Model | BA bias | BA MAE | QMD bias | QMD MAE | TPH bias | TPH MAE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Uncalibrated | +5.16 | 6.62 | −0.42 | 1.64 | +380 | 400 |
| v1 Marshall | +4.93 | 5.78 | +1.38 | 2.09 | +134 | 257 |
| v2c FAIB | **−0.21** | **3.81** | **+0.37** | **1.77** | **−6** | **245** |

v2c removes the regional BA and TPH bias. It is the best regional model.

## Marshall 2024 result, 24 sites

| Model | BA bias | BA MAE | QMD bias | QMD MAE | TPH bias | TPH MAE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Uncalibrated | +0.83 | 1.85 | −0.08 | 0.86 | +201 | 341 |
| v1 Marshall | +1.33 | 1.80 | +0.78 | 1.10 | **+24** | **270** |
| v2c FAIB | −2.59 | 2.85 | **+0.31** | **0.90** | −71 | 248 |

The two calibrations trade local and regional fit. v1 is closer to KC on BA and
TPH; v2c is closer on QMD and is unbiased regionally.

## Decision

Use an **ensemble** for production planning:

- **v1 Marshall** — local KC calibration, model of record for KC volume/TPH.
- **v2c FAIB** — regional calibration, conservative alternative and
  regional-transfer check.
- **Uncalibrated** — structural baseline and lower bound on calibration
  influence.

The AAC should be reported as a range across these three models, not a single
number. If one model must be selected for KC volume, v1 is closest on the 2024
Marshall BA/TPH test; its regional bias means the AAC should be checked against
v2c.

## Limits

- FAIB plot designs and expansion factors vary.
- The interval is first-to-last, not every consecutive remeasurement.
- No cutting is simulated.
- The FAIB panel is not a random whole-block sample.
- FVS-BC does not reproduce the FAIB ingrowth pulse.
- No independent-site validation of the spatial clump/opening model exists yet.

## Files

- `runbooks/fvs_validate_faib_idf.py`
- `ws4/kc_faib_validation/`
- `ws4/kc_faib_validation_v2c/`
- `ws4/kc_psp_validation_2024_v2c/`
- `ws4/kc_psp_calibration/calibration_parameters_faib_v2c.json`
