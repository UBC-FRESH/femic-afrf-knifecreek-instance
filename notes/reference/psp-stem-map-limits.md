# PSP stem-map limits for large-tree clumps

## Question

Can the public FAIB IDF Cariboo PSPs estimate the clump size and spacing of
large trees, so the retention policy can be calibrated to observed clumps?

**No, not with the plots that are usable for the stem-list analog.** The PSP
tree detail has `AZIMUTH` and `DISTANCE`, but most of the 45 stable first
measurements are not fully stem-mapped, and almost none have more than one
mapped tree at or above 50 cm DBH.

## Scan

Input: the 45 `CLSTR_ID` values in
`data/psp/idf_cariboo_psp_plot_weibull_fits.csv`, joined to the live tree detail
(`LV_D=L`, `DBH>=9.1`). A tree is mapped when both `AZIMUTH` and `DISTANCE` are
present. The full inventory is
`data/psp/idf_cariboo_psp_stem_map_inventory.csv`.

| Item | Count |
| --- | ---: |
| Stable first measurements | 45 |
| Fully mapped plots | 11 |
| Plots with at least one mapped tree >=50 cm | 3 |
| Plots with more than one mapped tree >=50 cm | 1 |

The one usable large-tree case is `4024835-PSP1`:

- 57 mapped live trees >=9.1 cm in the scan; 56 have a positive tree expansion
  factor in the derived case file, on a 0.099982 ha plot;
- 4 trees >=50 cm: 80.5, 71.2, 56.5 and 54.2 cm DBH;
- all four are sawlog / dominant crown class;
- pairwise distances (m): 7.93, 14.47, 22.06, 25.84, 29.98, 32.66.

Only one pair is within 10 m. At a 15 m linkage distance there are two pairs,
not a 3-5 tree clump. At a 10 m linkage distance there is one 2-tree pair. This
single 0.1 ha plot cannot estimate a clump-size distribution, and it does not
show the 2-5 tree clumps the retention objective describes.

`4024293-PSP1` is fully mapped and has one tree >=50 cm (52.0 cm). The other
large-tree plot, `4024460-PSP1`, has only 2 mapped trees out of 134, one of them
>=50 cm; it cannot support a clump analysis.

The derived positions are in
`data/psp/idf_cariboo_psp_stem_map_cases.csv` for the two fully mapped cases.
The raw FAIB tree detail is not committed.

## Implication

The public PSP analog can supply diameter distributions and stand-level
structure, but it cannot supply empirical large-tree clump size, clump spacing,
or within-clump canopy closure. Do not present the 2-5 tree clump geometry as
PSP-derived.

Use two tracks instead:

1. **Explicit geometry scenarios.** `runbooks/build_clump_scenarios.py` places
   the policy-pilot large-tree TPH into 2-5 tree clumps at 3, 5 or 7 m clump
   radius and reports within-clump crown closure and total cover. These are
   scenario axes, not observations.
2. **KC-specific data.** When the AFRF CFI/tree lists or stem-mapped UWR
   monitoring plots arrive, replace the geometry scenarios with observed clump
   sizes, spacing and crown dimensions. The approved UWR order and 2003
   transition strategy should define the legal clump target.

## Caveat

The PSP plots are 0.1 ha. Even a fully mapped plot has few large trees, so
clump counts per hectare have wide uncertainty. The one large-tree case is an
illustration of the data limit, not a benchmark for KC.
