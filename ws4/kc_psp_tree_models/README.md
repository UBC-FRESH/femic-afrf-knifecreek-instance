# KC PSP tree-level models v1

Status: **exploratory empirical models; growth and survival are usable as
diagnostics, ingrowth is not yet usable.**

These models are the alternative to forcing a sparse plot-level state matrix.
They use interval-start tree and stand attributes from the 1993–2013 PSP
remeasurements. No age or site index is assigned.

## Models

- **Diameter increment:** OLS on annual DBH increment, with start DBH, BAL,
  plot BA, crown ratio and species group.
- **Survival:** logistic interval survival, with start DBH, BAL, plot BA,
  crown ratio, species group and log interval length.
- **Ingrowth:** Poisson plot-interval count with start BA/TPH and treatment.

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
| B | 1 | 88.2 | 0.03 | 2.76 |
| C | 127 | 22.8 | 3.97 | 0.71 |
| D | 35 | 57.3 | 1.09 | 1.79 |

The ingrowth model fails the transfer test. Ingrowth is strongly block- and
treatment-specific and is zero in most Block B plots. Do not use the Poisson
ingrowth model as a production component.

## Interpretation

- Diameter and survival models are plausible as tree-level diagnostics.
- Survival is well calibrated in the mean and discriminates reasonably well.
- The growth model has modest error but is not enough on its own to claim a
  validated stand model.
- Ingrowth needs an empirical block/treatment distribution or a zero-inflated
  model; the current Poisson form is rejected.
- Tree records within plots are correlated; block CV is a transfer test, not
  independent replication.

## Files

- `tree_models.json` — final coefficients and transformations.
- `tree_validation.csv` — held-out growth/survival metrics.
- `ingrowth_validation.csv` — held-out ingrowth metrics.
- `manifest.json` — data counts and caveats.
- Generator: `runbooks/fit_psp_tree_models.py`.

## Next

1. Replace the Poisson ingrowth model with an empirical block/treatment
   distribution or a zero-inflated model.
2. Validate the growth/survival models at the **stand aggregate** level, not
   only at the tree level.
3. Only then use the models to simulate ws4 transitions.
