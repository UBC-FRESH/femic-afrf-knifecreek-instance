# Reference documents

## Klinka et al. 2004 — AFRF site units

`AFRF-site-unit-report-2004.pdf` is the published site-unit report for the UBC
Alex Fraser Research Forest:

> Klinka, K., P. Varga, C. Trethewey, C. Koot, M. Rau, J. Macku, and T.
> Kusbach. 2004. *Site Units of the University of British Columbia Alex Fraser
> Research Forest.* UBC Alex Fraser Research Forest, Williams Lake, BC. 108 pp.

SHA-256:

```text
94459a7bc6002932bc9a2150deb6d81879fbd48d776b86e4666e75addc7f5705
```

The report is a UBC AFRF publication. It is not covered by this repository's MIT
license. Use it as a cited reference; do not relicense it.

The report contains:

- the zonal-unit context for IDFxm, IDFdk3, IDFdk3-SBPSmk, SBSdw1, and ICHmk3;
- the site-series tables and site-group classification;
- site-series descriptions, keys, edaphic grids, landscape profiles, and
  environmental summaries;
- vegetation, soil, and foliar data appendices; and
- folded site maps in the map pockets / CD-ROM (not in this PDF).

The last point matters. The PDF gives the classification and identification
tools, but the georeferenced site-series polygons are in the map pockets /
CD-ROM. The PDF is not a substitute for the spatial site map.

The extracted site-series catalog for the two IDF units is in
`../config/site_series.yaml`. The context note is
`../notes/reference/site-series-klinka-2004.md`.

## AFRF Management and Working Plan #3 (2007)

`AFRF-management-working-plan-3-2007.pdf` is the Alex Fraser Research Forest
Management and Working Plan #3, effective January 1, 2007:

> Alex Fraser Research Forest. 2007. *Management and Working Plan #3.*
> University of British Columbia, Williams Lake, BC. 168 pp.

SHA-256:

```text
9bfd8b8f0449f45fb97fcf529236640ace09b73ba74f77001f677eee7307ff6a
```

The plan is a UBC AFRF publication. It is not covered by this repository's MIT
license. Use it as a cited reference; do not relicense it.

The plan contains:

- the Knife Creek mule-deer winter-range management direction;
- Table 29 target stand structures (High 29 m²/ha, D 60 cm, q 1.25; Moderate
  22/55/1.25; Low 16/50/1.30; 30-year cycle);
- Table 35 area AAC (82.0 ha/year single-tree selection, 11.2 ha/year salvage);
- CCLUP compliance targets and the plan's 0% conventional / 95% modified / 5%
  no-harvest outcome;
- Appendix 9 compartment maps and the KC01–KC11 / RD05–RD07 area table; and
- harvest, road, research, and fire-history appendices.

The plan is public management direction, not the legal Ungulate Winter Range
order. The 2003 Knife Creek transition strategy and the approved UWR order are
still outstanding.

The extracted contract is `../config/mdwr_regimes.yaml`. The context note is
`../notes/reference/mwp3-kc-management-direction.md`. Figure 11 was recovered
with `figrecover`; see `../notes/reference/mwp3-figure11-recovery.md`.
