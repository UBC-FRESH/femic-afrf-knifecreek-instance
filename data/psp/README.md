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
