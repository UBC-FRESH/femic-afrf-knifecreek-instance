# PSP-derived IDF Cariboo stem lists

## Why this exists

The Knife Creek CFI/tree list is still outstanding. The public FAIB ground-plot
compilation contains permanent sample plots in IDF stands in the Cariboo
region, so we can build a **PSP-derived regional IDF analog** now instead of
waiting. It is not Knife Creek data and it is not a substitute for the KC CFI,
but it is sufficient to exercise the FVS-BC selection pipeline and to benchmark
the stand-structure logic.

## Source

- Dataset: Forest Inventory Ground Plot Data and Interactive Map, BC Forest
  Analysis and Inventory Branch (FAIB).
- Catalogue: <https://catalogue.data.gov.bc.ca/dataset/forest-inventory-ground-plot-data-and-interactive-map>
- FTP: <https://www.for.gov.bc.ca/ftp/HTS/external/!publish/ground_plot_compilations/psp/>
- Licence: Open Government Licence - British Columbia.
- Retrieved: 2026-10-27.
- Data dictionary: `PSP_data_dictionary_2026Apr20.xlsx`.
- Fitting/sampling: `nemora` `2e8776c0ffce15cb4b18e2fbd70bdd4c1c4467d9`
  (`0.0.1-alpha`), grouped Weibull fit and inverse-CDF sampling. Nemora's
  current surface does not include a covariate regression for PDF parameters;
  the per-plot fits are retained for that next step. The generator uses the
  pooled PDF shape and calibrates each stand to its source plot's BA.

Raw files and SHA-256:

| File | Size | SHA-256 |
| --- | ---: | --- |
| `faib_header.csv` | 1.4 MB | `f029e21c149079036683ad65acf03b74975952d945926d1d3d607047079ea8b2` |
| `faib_sample_byvisit.csv` | 3.1 MB | `9b6db29182c4509d526ef16c06fb03f6cd9959ccf0125099af055e7e52fece60` |
| `faib_compiled_spcsmries_siteage.csv` | 6.3 MB | `15e81a9c777ff472805b8464f7582ac9099bd00ee6f7e1d34b72671f5c5a4ef5` |
| `faib_tree_detail.csv` | 706 MB | `d9f609cd42dd32d0d9e3cac19a6b654771ad2b1e2642c97452a6328143a4c910` |
| `PSP_data_dictionary_2026Apr20.xlsx` | 33 KB | `beda1c2a523a6495de92aad97b1b1a8f548548599c15d87fe0df07d4696ee6a1` |

The raw files are not committed. `runbooks/build_psp_stemlists.py` regenerates
the derived tables from a local raw-data directory.

## Selection

From the 7,341 FAIB sites, 973 are IDF. Restricting to first-measurement PSPs
in the Williams Lake and 100 Mile House TSAs gives 338 plots. The synthetic
library uses Douglas-fir-leading, mature IDF stands:

- first measurement, `PSP_G` or `PSP_R`;
- live trees at least 9.1 cm DBH;
- Douglas-fir leading by basal area;
- project age 80–180 years;
- basal area 20–40 m²/ha;
- QMD 15–25 cm.

That leaves 51 plots and 4,553 trees. The 45 plots whose per-plot Weibull fit
was stable (0.5 ≤ a ≤ 3.5, 3 ≤ β ≤ 30, KS < 0.15) feed the synthetic library.
The plot-level fits are retained in
`idf_cariboo_psp_plot_weibull_fits.csv`; the pooled fit is in
`idf_cariboo_psp_pooled_weibull.json`:

- Weibull `a = 1.0200`, `β = 7.8411`, lower bound 9.1 cm;
- pooled KS = 0.0109, RSS = 284,439;
- 45 plots, 4,553 trees.

The fit is on `DBH − 9.1` because the PSP sample is left-truncated at the
merchantable limit. The lower bound is added back when sampling.

## QMD/TPA regression

The per-plot Weibull fits were regressed on QMD and TPA. Using log QMD and
log TPA:

| Model | R² | Adj. R² | LOOCV RMSE | Coefficients |
| --- | ---: | ---: | ---: | --- |
| `log(beta) ~ log(QMD) + log(TPA)` | 0.480 | 0.455 | 0.314 | `-6.463 + 2.423 log QMD + 0.217 log TPA` |
| `log(beta) ~ log(QMD)` | 0.471 | 0.459 | 0.306 | `-3.863 + 2.049 log QMD` |
| `log(a) ~ log(QMD) + log(TPA)` | 0.096 | 0.053 | 0.362 | `-7.674 + 1.282 log QMD + 0.577 log TPA` |
| `log(a) ~ log(QMD)` | 0.012 | -0.011 | 0.367 | not used |

TPA is not significant after QMD in the scale model (`t = 0.86`; VIF = 2.71).
The QMD-only model is selected. The shape parameter `a` is not predictable
from QMD/TPA, so the pooled `a = 1.0200` is used.

Generalized gamma was also tested per plot. Five of 45 plots had lower AICc
with GG, but every one had degenerate parameters (`p` near 0 or 170, `beta`
near 1e-7). No stable GG fit beat Weibull, so the simpler Weibull is used.

The regression is a scale model, not a full growth model. QMD predicts the
Weibull scale; TPA sets density; the final stand is scale-calibrated to the
target QMD. The five conditional lists are:

| Stand | QMD | TPA | BA (m²/ha) |
| --- | ---: | ---: | ---: |
| PSP-REG-001 | 18 | 900 | 22.9 |
| PSP-REG-002 | 20 | 800 | 25.1 |
| PSP-REG-003 | 22 | 750 | 28.5 |
| PSP-REG-004 | 24 | 650 | 29.4 |
| PSP-REG-005 | 26 | 550 | 29.2 |

`runbooks/fit_psp_weibull_regression.py` writes the model diagnostics and the
conditional lists. The three-stand FVS-BC pilot results are in
`idf_cariboo_psp_fvs_pilot.csv`; the two conditional regression stands are in
`idf_cariboo_psp_regression_fvs_pilot.csv`:

| Stand | Target QMD | Year 30 pre | Year 30 post | Removed TPH |
| --- | ---: | ---: | ---: | ---: |
| PSP-REG-003 | 22 | 41 | 35 | 197 |
| PSP-REG-004 | 24 | 41 | 38 | 91 |

Again the residual is above the 29 m²/ha target because of the q deficit in the
grown stand.

## Synthetic stem lists

`runbooks/build_psp_stemlists.py` generates one-hectare stems by:

1. drawing a source plot (without replacement for a 24-stand library);
2. drawing the tree count from a Poisson around the plot's expanded TPA,
   capped at FVS-BC's 999-tree plot limit;
3. drawing DBH from the pooled PSP Weibull by inverse CDF;
4. scaling the draw to the source plot's observed basal area, so the PDF
   supplies the shape and the plot supplies the level;
5. assigning species by the observed species-by-DBH composition;
6. assigning height from a species-specific log–log height–DBH fit, crown
   ratio from the observed crown class, and age from the plot's projected age.

The 24-stand sample is `idf_cariboo_psp_stemlist_sample.csv` with 22,178 trees.
The FVS-ready population is `idf_cariboo_psp_stemlist_population.json`.
Stands span 586–999 trees, 20.8–38.8 m²/ha BA, 16.8–23.9 cm QMD and
12.8–16.5 m mean height.

## FVS-BC structural pilot

Three stands were run through the built `FVSbc` with the corrected BC THINQFA
units (`0.0`, `60.0`, `5.0` cm), target 126.32 ft²/ac (29 m²/ha), q 1.25,
`TIMEINT=,30`, `NUMCYCLE=2`, cycle 2.

| Stand | Source BA | Age | Year 0 BA | Year 30 pre-cut | Year 30 post-cut | Removed TPH | Removed m³/ha |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| PSP-IDF-004 | 28.78 | 129 | 28 | 45 | 31 | 407 | 106 |
| PSP-IDF-008 | 38.54 | 84 | 38 | 53 | 34 | 429 | 151 |
| PSP-IDF-015 | 20.82 | 178 | 20 | 34 | 30 | 130 | 28 |

The target is 29 m²/ha; the residual is 30–34 m²/ha. The residual exceeds the
target because the grown diameter distributions have q deficits that
`THINQFA` cannot fix without leaving more basal area than the target. This is
the same behaviour seen in the earlier synthetic pilot and is recorded as a
structural caveat, not a calibration result.

## What this does and does not establish

Establishes:

- A public, reproducible IDF Cariboo PSP stem-list analog.
- A fitted DBH PDF and inverse-CDF sampling path that can generate more stems
  or stands on demand.
- FVS-BC can ingest the stems and execute the corrected cycle-2 `THINQFA`
  treatment.

Does not establish:

- Knife Creek-specific structure, growth, or mortality.
- That the residual target is always attained.
- That the synthetic species/height/crown assignments are a substitute for
  measured KC tree lists.
- Independent information beyond the 45 PSP plots and 4,553 trees. Monte Carlo
  can generate arbitrarily many trees or stands, but it cannot create new
  plots; the fitted PDF and its uncertainty remain finite.

## Reproduction

```bash
python -m venv /tmp/nemora-venv
. /tmp/nemora-venv/bin/activate
python -m pip install -e /path/to/nemora

python runbooks/build_psp_stemlists.py \
  --raw-dir /path/to/faib_psp_csvs \
  --out-dir data/psp \
  --stands 24
```

The raw-data directory needs `faib_header.csv`, `faib_sample_byvisit.csv`,
`faib_compiled_spcsmries_siteage.csv` and `faib_tree_detail.csv` from the FAIB
PSP FTP directory.

## Stem-map limit

Most of the 45 stable PSP plots are not fully stem-mapped, and only one has more
than one mapped tree ≥50 cm. The public PSP analog cannot estimate large-tree
clump size or spacing. See `psp-stem-map-limits.md`.

## Space-for-time panel

To stop waiting for a perfect KC chronology, we built a public IDF Cariboo
space-for-time panel from all live-tree visits, not only first measurements.

- 338 IDF plots, 697 visits in the Williams Lake and 100 Mile House TSAs.
- 590 visit states pass the data screen: live trees ≥9.1 cm DBH, BA 5–60,
  QMD 5–50, TPH 100–5000, projected age 20–250.
- 92 states are stratified across age and BA bins for FVS-BC runs.
- The selected states span projected ages 44–239 and BA 5.3–52.5 m²/ha.
- Each state has a 50-year no-cut FVS-BC curve at 10-year steps.

This is a **space-for-time substitution**: each visit is a state, not a growth
chronology. The repeated visits are not independent plots. The curves are not
observed 50-year growth and do not replace the KC CFI.

Files:

- `data/psp/idf_cariboo_space_for_time_plots.csv`
- `data/psp/idf_cariboo_space_for_time_curves.csv`
- `data/psp/idf_cariboo_space_for_time_manifest.json`
- Generator: `runbooks/build_psp_space_for_time.py`
