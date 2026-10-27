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
