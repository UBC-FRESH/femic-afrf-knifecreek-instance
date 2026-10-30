# KC AU-aware ws4 model

Status: AU model with corrected treatment logic and residual growth. Structural,
not calibrated and not a legal-compliance product.

## Model

- Six AUs from `data/kc_au/kc_au_table.csv`.
- States: AU x HMZ x natural/managed_low/managed_moderate.
- HMZ eligibility:
  - M/A: GWM_LOW or GWM_MODERATE;
  - L: GWM_LOW only;
  - U: no treatment.
- One selection entry at age 30; managed states are re-enterable.
- Natural curves are AU no-cut curves.
- Managed curves start at the **post-treatment residual** stand
  (`ATBA`, `ATQMD`, `ATCCF`, residual TPH and residual volume), not the pre-cut
  stand.
- Product curves are the cut yields from the AU selection runs.

Files:

- `data/kc_ws4_recipe_au/forestmodel.xml`
- `data/kc_ws4_recipe_au/fragments.csv`
- `ws4/dataset_kc_au_v1`
- `runbooks/build_kc_au_managed_200y.py`
- `runbooks/build_kc_au_recipe.py`

## Counts

- 160 fragments/blocks
- 30 tracks
- 34 treatments: 22 GWM_LOW, 12 GWM_MODERATE
- 180 feature rows
- 46 product rows
- 6 AUs
- 200-year feature horizon

`ws4 validate` passes.

## Not done yet

- Even-flow convergence tuning is intentionally not part of this step.
- The model still has two managed states per AU/HMZ, not a full BA/QMD
  multi-entry residual-state graph.
