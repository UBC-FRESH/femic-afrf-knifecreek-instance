# KC AU-aware ws4 model

Status: AU/HMZ multi-entry stage graph compiled. Structural, not calibrated and
not a legal-compliance product.

## Model

- Six AUs from `data/kc_au/kc_au_table.csv`.
- States: AU x HMZ x SILV.
- SILV: natural plus six managed entry stages (`M1`–`M6`).
- Two regimes: `GWM_LOW`, `GWM_MODERATE`.
- HMZ eligibility:
  - M/A: both regimes;
  - L: low only;
  - U: no treatment.
- Entry years: 30, 60, 90, 120, 150, 180.
- Each managed stage transitions to the next stage; the final stage is terminal.
- Managed x=0 is the post-entry residual from FVS `ATBA`, `ATQMD`, `ATCCF`,
  pre-cut minus removed TPH and pre-cut minus removed volume.
- The entry is a three-part cut: large trees 37.5 cm to D, surplus above D to
  the reserve ceiling, then small trees 2.5–37.5 cm.
- Product curves are the cut yields at the next entry.

Files:

- `data/kc_ws4_recipe_au_stages/forestmodel.xml`
- `data/kc_ws4_recipe_au_stages/fragments.csv`
- `ws4/dataset_kc_au_stages_v1`
- `runbooks/build_kc_au_multientry_200y.py`
- `runbooks/build_kc_au_stage_recipe.py`

## Counts

- 160 fragments/blocks
- 115 tracks
- 102 treatments
- 2,300 feature rows
- 182 feature labels including max DBH and q
- HMZ-specific large-tree/reserve/yield/area accounts
- 102 product rows
- 6 AUs
- 200-year feature horizon

`ws4 validate` passes.

## Limits

- Stage states are entry-sequence states, not a continuous BA/QMD state space.
- Six entries only; the final stage is terminal.
- No even-flow convergence tuning in this step.
- No calibration or legal-compliance claim.
