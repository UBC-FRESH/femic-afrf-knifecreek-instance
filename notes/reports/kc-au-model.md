# KC AU-aware ws4 model

Status: first compiled AU model. Structural, not calibrated and not a
legal-compliance product.

## Model

- Six AUs from `data/kc_au/kc_au_table.csv`.
- Two states per AU: natural and managed.
- One `GWM_MODERATE` selection treatment at age 30.
- Managed state is re-enterable.
- AU-specific no-cut and post-entry feature curves.
- Product curve is the cut yield from the AU selection run.

Files:

- `data/kc_ws4_recipe_au/forestmodel.xml`
- `data/kc_ws4_recipe_au/fragments.csv`
- `ws4/dataset_kc_au_v1`
- `runbooks/build_kc_au_recipe.py`

## Counts

- 160 fragments/blocks
- 12 tracks: six AUs × natural/managed
- 12 treatments
- 72 feature rows
- 12 product rows
- 6 AUs
- 200-year feature horizon

`ws4 validate` passes.

## 20-period probe

Using a full first-entry seed on the AU model:

- all 20 harvest-volume floors at 27,000 m3/period are met;
- final growing stock is met at 2,306,630 vs a 2,306,548 minimum;
- the ±5% even-flow band does not converge in 5,000 iterations.

This is a first-entry AU model, not a multi-entry BA/QMD state graph. The next
step is to add residual states per AU and solve the even-flow band.
