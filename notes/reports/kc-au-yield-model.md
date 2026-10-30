# KC AU-stratified yield model

Status: AU definitions and 200-year FAIB PSP/FVS curves. Not yet the compiled
selection-state model.

## AU construction

Followed the FEMIC stage-00/01a pattern:

- BEC variant + leading species strata;
- top-area coverage target 95%;
- sparse leading-species strata remapped to the dominant same-BEC stratum;
- standard 30-point SI quantile bands: L 5–35, M 35–65, H 65–95.

The selected strata are `IDFdk3__FDI` and `IDFxm__FDI`, covering 97.8% of the
forested area. The resulting six AUs are recorded in
`data/kc_au/kc_au_table.csv` and `data/kc_au/kc_au_assignment.csv`.

## FAIB matching and FVS

For each AU, matched public FAIB PSP plots in the same BEC variant and leading
species, preferring plots inside the AU SI band, then nearest SI.

- 28 plots matched
- 5 plots per AU except `KC_IDFxm_FDI_M` (3)
- 200-year no-cut FVS-BC runs
- AU curves averaged across matched plots

Outputs:

- `data/psp/kc_au_200y/kc_au_plot_matches.csv`
- `data/psp/kc_au_200y/kc_au_yield_200y.csv`
- `data/psp/kc_au_200y/manifest.json`

## Limits

- These are no-cut yield curves.
- The selection-state/managed curves are not yet rebuilt from these AUs.
- Site index is the FAIB leading-species SI, and tree age is the FAIB projected
  age; neither is a KC calibration.
- No legal-compliance claim.

## Next

Run the selection-cut state-transition build per AU, then compile the ws4
dataset with an AU dimension and rerun the 20-period even-flow scenario.
