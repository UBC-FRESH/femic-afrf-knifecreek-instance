# KC AU layer

The AU layer follows the FEMIC stage-00/01a pattern:

- stratify VRI by BEC variant + leading species;
- keep the top-area strata covering 95% of the forested area;
- alias sparse leading-species strata to the dominant same-BEC stratum;
- split each selected stratum into L/M/H by the standard 30-point SI quantile
  bands (5–35, 35–65, 65–95).

Six AUs result:

| AU | Area ha | Stands |
| --- | ---: | ---: |
| KC_IDFdk3_FDI_H | 1,287.56 | 50 |
| KC_IDFdk3_FDI_M | 834.23 | 44 |
| KC_IDFdk3_FDI_L | 783.24 | 47 |
| KC_IDFxm_FDI_H | 264.49 | 12 |
| KC_IDFxm_FDI_M | 234.92 | 9 |
| KC_IDFxm_FDI_L | 77.80 | 11 |

`kc_au_assignment.csv` maps every VRI polygon to its static and matched stratum
and AU. `kc_au_manifest.json` records the selection and remap decisions.
