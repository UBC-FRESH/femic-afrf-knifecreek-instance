# KC PSP 200-year FVS-BC curves

Status: derived curve set. Not calibrated growth and not a legal-compliance
product.

## What ran

- Source: KC PSP first-measurement live interior trees (`position == "I"`).
- Plots: 24.
- FVS-BC: `fresh-fvsbc 0.20.0`, FVS source `ef5fa847`.
- Horizon: 200 years.
- Step: 10 years.
- Tree age: 60 years (structural placeholder).
- Site index: 60 (structural placeholder).
- Treatment: no cut.

## Output

`data/psp/kc_afrf_psp_fvs_200y_curves.csv`

- 24 plots
- 504 rows
- years 0–200 in 10-year steps
- columns: BA, TPH, QMD, total cubic volume, canopy CCF

`data/psp/kc_afrf_psp_fvs_200y_curves.manifest.json` records the runs and case
IDs.

The interior-tree initial BA matches the plot summary for the checked plots.
Raw tree tallies remain private; only the derived plot curves and run manifest
are published.

## Limits

- These are no-cut projections, not observed 200-year growth.
- Tree age and site index are placeholders.
- FVS-BC emits a forest-code warning because the structural stand setup uses a
  default location code.
- These curves are not yet wired into `ws4/dataset_kc_v1`; the current dataset
  still carries the earlier structural curves.
- No KC calibration or legal-compliance claim follows from these curves.
