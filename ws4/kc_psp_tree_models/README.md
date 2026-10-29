# KC PSP tree-level models v1

Status: **exploratory empirical models; growth and survival are usable as
diagnostics, ingrowth is not transferable.**

These models are the alternative to forcing a sparse plot-level state matrix.
They use interval-start tree and stand attributes from the 1993–2013 PSP
remeasurements. No age or site index is assigned.

## Models

- **Diameter increment:** OLS on annual DBH increment, with start DBH, BAL,
  plot BA, crown ratio and species group.
- **Survival:** logistic interval survival, with start DBH, BAL, plot BA,
  crown ratio, species group and log interval length.
- **Ingrowth:** empirical plot-interval count distribution by block/treatment,
  with a treatment-level fallback for held-out blocks.

Validation is leave-one-block-out: fit on two blocks, test the third.

## Results

Diameter increment:

| Held-out | n tree-intervals | RMSE cm/yr | MAE cm/yr | Bias cm/yr |
| --- | ---: | ---: | ---: | ---: |
| B | 5,503 | 0.0868 | 0.0628 | -0.0037 |
| C | 4,162 | 0.0992 | 0.0692 | -0.0130 |
| D | 4,069 | 0.1017 | 0.0720 | +0.0135 |

Survival:

| Held-out | Brier | AUC | Mean predicted | Observed prevalence |
| --- | ---: | ---: | ---: | ---: |
| B | 0.060 | 0.896 | 0.924 | 0.918 |
| C | 0.071 | 0.829 | 0.925 | 0.917 |
| D | 0.067 | 0.805 | 0.919 | 0.919 |

Ingrowth:

| Held-out | Observed total | Predicted total | Observed mean | Predicted mean |
| --- | ---: | ---: | ---: | ---: |
| B | 1 | 81.0 | 0.03 | 2.53 |
| C | 127 | 18.0 | 3.97 | 0.56 |
| D | 35 | 64.0 | 1.09 | 2.00 |

The empirical block/treatment distribution still fails the held-out transfer
test. Ingrowth is strongly block-specific and is zero in most Block B plots.
It is usable only as a block-specific empirical distribution for known blocks,
not as a transferable model.

## Stand aggregate validation

The start-cohort experiment applies the fitted growth and survival models to the
1993 trees and compares BA/TPH/QMD at each interval end. It excludes ingrowth.

| Block | BA bias | BA MAE | TPH bias | TPH MAE | QMD bias | QMD MAE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B | -0.19 | 1.26 | +20.1 | 103.4 | +0.04 | 0.29 |
| C | +0.07 | 1.09 | +19.6 | 63.9 | -0.10 | 0.33 |
| D | +0.01 | 2.10 | -1.3 | 105.9 | -0.01 | 0.32 |

Overall BA bias is -0.04 m²/ha (MAE 1.49), TPH bias +12.8 (MAE 91.1) and QMD
bias -0.02 cm (MAE 0.31). The start-cohort aggregate is plausible; this is not a
test of ingrowth or future treatments.

## Interpretation

- Diameter and survival models are plausible as tree-level diagnostics.
- Survival is well calibrated in the mean and discriminates reasonably well.
- The start-cohort aggregate is plausible for BA and QMD; TPH remains noisier.
- Ingrowth needs a block-specific empirical distribution or explicit scenario;
  it is not a transferable model.
- Tree records within plots are correlated; block CV is a transfer test, not
  independent replication.

## Files

- `tree_models.json` — final coefficients and empirical ingrowth distributions.
- `tree_validation.csv` — held-out growth/survival metrics.
- `ingrowth_validation.csv` — held-out empirical ingrowth metrics.
- `stand_validation.csv` — start-cohort BA/TPH/QMD validation by plot/interval.
- `manifest.json` — data counts and caveats.
- Generator: `runbooks/fit_psp_tree_models.py`.

## Next

1. Treat ingrowth as a block-specific empirical scenario, or obtain more data;
   do not use it as a transferable equation.
2. Use the validated start-cohort growth/survival aggregate as the basis for a
   state-transition simulator.
3. Only then compare simulated states with the observed 96 transitions.
