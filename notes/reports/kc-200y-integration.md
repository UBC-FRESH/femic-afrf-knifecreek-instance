# KC 200-year FVS curve integration

Status: structural integration. Not calibrated growth and not a legal-compliance
product.

## What was integrated

`data/patchworks_knifecreek/tracks/H_200y` replaces the old feature curves with
the 24-plot KC PSP FVS-BC 200-year curves.

- 92 tracks
- 552 feature rows
- 98 product rows
- feature curves 0–200 years
- product curves unchanged point estimates

Each track state is assigned to the nearest KC PSP plot by initial BA and QMD.
This is an attribute match, not a spatial join.

## Compiled model

`ws4/dataset_kc_v1_200y` was compiled from:

- `data/kc_ws4_recipe_200y/forestmodel.xml`
- `data/kc_ws4_recipe_200y/fragments.csv`

`ws4 validate` passes.

## 20-period probe

With the 20 × 10-year target file and the current GWM moderate seed:

- final-period growing stock at 90% of initial is met
  (2,306,630 vs 2,306,548 minimum);
- the 27,000 m3/period floor is below in most periods;
- the ±5% even-flow band is not converged.

The old 27,000 floor was tested against the old curves. It is not a maximum for
the 200-year curve set. A fresh floor search is required.

## Limits

- Track-to-plot assignment by BA/QMD is a structural proxy.
- No-cut FVS curves, not observed 200-year growth.
- Tree age 60 and site index 60 are placeholders.
- Product curves remain point estimates from the source H matrix.
- No KC calibration or legal-compliance claim.

## Next

Search the maximum even-flow floor against `dataset_kc_v1_200y`, then run the
full scenario to convergence.
