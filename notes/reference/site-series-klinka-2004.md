# Klinka et al. 2004: AFRF site units

Date recorded: 2026-10-26
Source: Klinka, K., P. Varga, C. Trethewey, C. Koot, M. Rau, J. Macku, and T.
Kusbach. 2004. *Site Units of the University of British Columbia Alex Fraser
Research Forest.* UBC Alex Fraser Research Forest, Williams Lake, BC. 108 pp.

The report is at `reference/AFRF-site-unit-report-2004.pdf`; SHA-256
`94459a7bc6002932bc9a2150deb6d81879fbd48d776b86e4666e75addc7f5705`. It is a UBC
AFRF publication, not MIT-licensed. Cite it; do not relicense it.

## What the report gives

- The zonal-unit context for IDFxm, IDFdk3, IDFdk3-SBPSmk, SBSdw1, and ICHmk3.
- Nine site groups and the site-series classification (Tables 6.3.1 and 6.3.2).
- IDFxm site series 01-09 and IDFdk3 site series 01-10, with BCFS codes, full
  names, and the project's abbreviated names.
- Site-series descriptions, keys, edaphic grids, landscape profiles, and
  environmental summaries.
- Vegetation, soil, and foliar data appendices.
- Folded site maps in the map pockets and an interactive CD-ROM.

The extracted IDF catalog is `config/site_series.yaml`.

## Knife Creek facts from the report

- The Knife Creek block is **3,484 ha** near 150 Mile House.
- Elevation ranges from **720 to 1,020 m**.
- The block is on gentle terrain adjacent to the San Jose Valley.
- The whole block is under a summer-dry, cool temperate climate.
- The driest and warmest sites are low-elevation sites (<800 m) in the
  southwestern part; slightly wetter and cooler sites occupy the plateau.
- Douglas-fir is the predominant species, occupying about **3,000 ha (87%)**.
- Frequent historical wildfire created uneven-aged stands; harvesting dates
  back to the mid-1940s.
- The site-series column for Knife Creek is the IDFxm / IDFdk3 /
  IDFdk3-SBPSmk transition set.

## What the PDF does not give

The **georeferenced site-series polygons are not in the PDF**. The report says
the site maps are folded in the map pockets and that the CD-ROM contains the
interactive maps and polygon attribute tables. The PDF is the report text and
figures, not the GIS layer.

That distinction matters:

- We can use the classification and keys to define site-series classes and
  site groups.
- We cannot map those classes to VRI polygons without the site map, the
  CD-ROM GIS data, or a reviewed rule-based assignment.
- A BEC zone/subzone is not a site series. Using BEC alone would fold the
  within-zone moisture/nutrient gradient into one class, and the report exists
  precisely because that gradient matters.

## Cross-check against the 2025 VRI

The VRI clipped to SUP S15382 differs from the 2004 report in ways that are
expected from different vintages and boundaries:

| Item | Klinka 2004 | VRI 2025 |
| --- | --- | --- |
| Block area | 3,484 ha | 3,533.13 ha (SUP) |
| Douglas-fir-leading area | ~3,000 ha (87%) | 3,416.8 ha (96.7%) |
| BEC | IDFxm / IDFdk3 / transition | IDFdk3 2,955.9 ha; IDFxm 577.2 ha (VRI field) |
| Site index | report interpretation maps | `SITE_INDEX` on 174/183 polygons, 5.2-20.0 |

Do not force these to agree. The report is a 2004 ecological mapping product;
the VRI is a 2025 forest inventory. The differences are a reason to keep the
source and vintage attached to every derived class.

## What remains

P1.2a (#15): acquire the AFRF site-series map / CD-ROM GIS layer and the
approved UWR boundary plus legal mule-deer objectives.

Until the site map is available, a provisional rule-based site-series
assignment from VRI BEC, species, site index, and the report keys is possible,
but it must be labelled provisional and must not be presented as the AFRF site
map.
