# KC PSP state reconstruction v1

Status: **conditional reconstruction, not a forecast**. Growth and survival are
applied leave-one-block-out; ingrowth is taken from the observed interval.

This directory tests whether the tree-level growth/survival models reproduce
the observed 96 transitions at stand level.

## Modes

- **cohort** — start trees only, no ingrowth. Tests growth and survival.
- **conditional** — start trees plus the recruits actually observed in that
  interval. Tests growth and survival on a complete stand, but it does not test
  the ingrowth model.

## Results

Overall, across 96 transitions:

| Mode | BA bias | BA MAE | TPH bias | TPH MAE | QMD bias | QMD MAE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cohort | -0.04 | 1.49 | -21.2 | 109.3 | +0.11 | 0.34 |
| conditional | -0.04 | 1.49 | +12.4 | 91.5 | -0.02 | 0.31 |

By block:

| Block | Cohort BA bias/MAE | Conditional BA bias/MAE | Cohort TPH bias | Conditional TPH bias | Cohort QMD bias | Conditional QMD bias |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B | -0.19 / 1.26 | -0.19 / 1.26 | +19.5 | +20.1 | +0.04 | +0.04 |
| C | +0.06 / 1.09 | +0.07 / 1.09 | -59.8 | +18.3 | +0.23 | -0.09 |
| D | +0.01 / 2.10 | +0.01 / 2.10 | -23.2 | -1.3 | +0.07 | -0.01 |

## Interpretation

- BA and QMD reconstruct well at stand level.
- TPH is noisier; conditional observed ingrowth removes the negative bias but
  does not make TPH precise.
- The conditional result is **not** an ingrowth validation. Ingrowth remains a
  block-specific empirical scenario; held-out transfer failed in
  `ws4/kc_psp_tree_models/ingrowth_validation.csv`.
- The weak point is TPH and ingrowth, not BA/QMD.

## Files

- `simulation_validation.csv` — one row per transition and mode.
- `simulation_summary.csv` — block × interval summary.
- `manifest.json` — overall metrics and caveats.
- Generator: `runbooks/simulate_psp_states.py`.

## Next

Use the conditional reconstruction as the baseline for a ws4 transition
simulator, with block-specific ingrowth scenarios explicitly separated from
the growth/survival model. Do not claim ingrowth prediction.
