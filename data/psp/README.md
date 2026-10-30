# PSP-derived IDF Cariboo stem lists

## AFRF Knife Creek PSP field data

The AFRF KC PSP workbook is the primary field-data candidate, not the regional
analog below. The raw workbook is private and not committed. Public derived
files:

| File | Purpose |
| --- | --- |
| `kc_afrf_psp_plot_summary.csv` | 24 plots × 5 years, interior-tree TPH/BA/QMD/height/large-tree metrics. |
| `kc_afrf_psp_schema.csv` | Tidy long-table column schema. |
| `kc_afrf_psp_metadata.json` | Source hash, counts, assumptions. |
| `kc_afrf_psp_dynamics.csv` | Mortality/ingrowth by interval, block, treatment and size class. |
| `kc_afrf_psp_dynamics_summary.csv` | Mortality/ingrowth summary by block/treatment. |
| `kc_afrf_psp_mortality_by_plot.csv` | Plot-level mortality and recruitment. |
| `kc_afrf_psp_transitions.csv` | 96 observed plot-interval transitions. |
| `kc_afrf_psp_transitions_species.csv` | Species-group BA/TPH for those transitions. |
| `kc_afrf_psp_transitions_metadata.json` | Transition provenance, assumptions and caveats. |
| `kc_afrf_psp_state_support.csv` | Transitions annotated with canonical and species-mix state IDs. |
| `kc_afrf_psp_state_support_summary.csv` | Support counts by start/end state. |
| `kc_afrf_psp_state_support_metadata.json` | State-bin definitions and support summary. |

Mortality/ingrowth use DBH presence at each measurement as the working
live/dead indicator. `TS`/`TC` and the dead-tree column semantics remain
unresolved, so these summaries are not a substitute for the field codes.

See `../notes/reference/kc-afrf-psp-dataset.md`,
`../ws4/kc_psp_validation/README.md` and
`../ws4/kc_psp_calibration/README.md`. The 1993–2013 FVS backtest is a
structural test with placeholder age/site index, not a calibration claim. Its
v1 tables correct the cycle-year alignment in the earlier v0 run.

# Regional IDF Cariboo analog

Public FAIB permanent-sample-plot data, filtered to Douglas-fir-leading,
first-measurement IDF stands in the Williams Lake and 100 Mile House TSAs.
These are regional IDF analogs for the Knife Creek model, not KC data.

| File | Purpose |
| --- | --- |
| `idf_cariboo_psp_plots.csv` | Selected PSP plots and their expanded TPA, BA, QMD, age, BEC and TSA. |
| `idf_cariboo_space_for_time_plots.csv` | 132 stratified IDF site states spanning 44–248 projected years and 5.5–52 m²/ha BA, by BEC and leading species. |
| `idf_cariboo_space_for_time_curves.csv` | 100-year no-cut FVS-BC curves for those site states. |
| `kc_afrf_psp_fvs_200y_curves.csv` | 200-year no-cut FVS-BC curves for 24 KC PSP plots. |
| `kc_au_200y/` | AU-stratified 200-year FAIB PSP/FVS curves and plot matches. |
| `kc_au_200y/kc_au_yield_200y.csv` | AU no-cut curves with large-tree BA/TPH. |
| `idf_cariboo_ba_for_time.csv` | Experimental BA-asymptote and BA-for-time coordinates. |
| `idf_cariboo_space_for_time_manifest.json` | Selection, design and caveats. |
| `idf_cariboo_psp_plot_weibull_fits.csv` | Stable per-plot shifted-Weibull DBH fits. |
| `idf_cariboo_psp_pooled_weibull.json` | Pooled fitted DBH PDF used for sampling. |
| `idf_cariboo_psp_stemlist_sample.csv` | 24 synthetic one-hectare stem lists (22,178 trees) with source-plot provenance. |
| `idf_cariboo_psp_stemlist_population.json` | FVS-BC-ready population records (`stand_id`, `dbh_cm`, `height_m`, `crown_ratio`). |
| `idf_cariboo_psp_fvs_pilot.csv` | Three-stand FVS-BC structural pilot under cycle-2 THINQFA. |
| `idf_cariboo_psp_weibull_regression.json` | QMD/TPA regression diagnostics and selected model. |
| `idf_cariboo_psp_weibull_regression_predictions.csv` | Observed vs predicted per-plot Weibull parameters. |
| `idf_cariboo_psp_conditional_stemlists.csv` | Five conditional stem lists at target QMD/TPA. |
| `idf_cariboo_psp_conditional_stemlists_population.json` | FVS-ready conditional populations. |
| `idf_cariboo_psp_regression_fvs_pilot.csv` | Two-stand FVS-BC pilot on the conditional lists. |
| `idf_cariboo_psp_stem_map_inventory.csv` | Mapping completeness for the 45 stable plots. |
| `idf_cariboo_psp_stem_map_cases.csv` | Mapped trees from the two fully mapped plots with large trees. |

Source: FAIB Forest Inventory Ground Plot Data, Open Government Licence -
British Columbia. The raw 706 MB tree detail is not committed; see
`../../notes/reference/psp-idf-cariboo-stemlists.md` for retrieval, hashes,
selection, fitting and caveats.

The synthetic lists are not a substitute for the KC CFI. They are a public
regional analog for exercising the FVS-BC selection pipeline now.
