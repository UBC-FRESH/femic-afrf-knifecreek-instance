# AFRF roads, log sorts, and mills: source audit

Date: 2026-10-31
Phase: P7.1
Status: audit complete; source data incomplete

## Purpose

This note records what the 2007 AFRF management plan, the legacy Patchworks
archive, and the private OneDrive payload actually contain about roads, access,
harvest systems, log grades, mills, and costs. It separates:

- what can be used now;
- what is only a planning assumption;
- what is missing; and
- what must be requested from AFRF.

The extracted tables are under `data/roads/`. The reproducible extractor is
`runbooks/build_mwp3_roads_audit.py`.

## Primary source

**Alex Fraser Research Forest, Management and Working Plan #3**, effective
1 January 2007 to 31 December 2012.

- Repository copy: `reference/AFRF-management-working-plan-3-2007.pdf`
- SHA-256: `9bfd8b8f0449f45fb97fcf529236640ace09b73ba74f77001f677eee7307ff6a`
- Pages: 168
- Publisher: UBC Alex Fraser Research Forest
- Licence: public UBC AFRF planning document; UBC copyright, not OGL
- Relevant material: section 8.1, section 8.2, Tables 37-39, Appendix 11,
  and Figure 7.

The extractor verifies the hash and page count, renders the two Appendix 11
access maps, and writes:

- `data/roads/mwp3_table37_roads.csv`
- `data/roads/mwp3_table38_specs.csv`
- `data/roads/mwp3_table39_landings.csv`
- `data/roads/mwp3_harvest_systems.csv`
- `data/roads/mwp3_access_assumptions.csv`
- `data/roads/gap_register.csv`
- `data/roads/source_manifest.json`
- `data/roads/context/mwp3_gavin_access.jpg`
- `data/roads/context/mwp3_knife_creek_access.jpg`

## What the plan provides

### Road length and area

Table 37, printed page 110, gives the reconciliation targets:

| Measure | Gavin Lake | Knife Creek | Total |
| --- | ---: | ---: | ---: |
| Net area (ha) | 4,922 | 3,117 | 8,040 |
| Existing road length (km) | 112.2 | 86.2 | 198.4 |
| Existing right-of-way area (ha) | 168.3 | 129.3 | 297.6 |
| Existing density (km/km2) | 2.28 | 2.76 | 2.47 |
| Existing area share | 3.4% | 4.1% | 3.7% |
| Planned road length (km) | 136.1 | 77.2 | 213.3 |
| Planned right-of-way area (ha) | 204.1 | 115.9 | 320.0 |
| Planned density (km/km2) | 2.77 | 2.48 | 2.65 |
| Planned area share | 4.1% | 3.7% | 4.0% |
| Planned change (km) | +23.9 | -9.0 | +14.9 |
| Planned change in R/W area (ha) | +35.8 | -13.4 | +22.4 |

The plan states that the planned change is a "total chance" road plan, not a
committed construction schedule.

### Road specifications

Table 38, printed page 110, gives the design envelope:

| Surface width (m) | Design speed (km/h) | Min. sight distance (m) | Min. curve radius (m) | Favourable sustained | Favourable short pitch | Adverse sustained | Adverse short pitch | Switchbacks |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 20 | 40 | 15 | 16% | 18% | 9% | 12% | 8% |
| 5-6 | 30 | 65 | 35 | 12% | 14% | 8% | 10% | 8% |
| 5-6 (continued) | 40 | 95 | 65 | 12% | 14% | 8% | 10% | 8% |

The plan says most roads are built from native materials with spot surfacing,
are seasonally unserviceable in wet conditions, and are generally permanent
because partial cutting requires repeated entries. Temporary roads and landings
are to be rehabilitated within about two years of harvest completion.

### Harvest systems

Section 8.1.1, printed page 107, gives three ground-based systems and two
slope-based classes:

- shortwood harvester/forwarder combination, particularly suited to thinning;
- feller-buncher/grapple skidder/processor combination, best suited to
  clearcutting;
- hand falling/cable skidder/hand bucking, best suited to large piece size,
  high value, or salvage;
- cable systems on Gavin Lake blocks with substantial area above 30% slope; and
- inaccessible areas above 60% slope.

The plan says ground-based systems dominate because less than 5% of net area
exceeds 30% slope.

### Access and operational assumptions

| Assumption | Value | Source |
| --- | ---: | --- |
| Maximum sustained favourable grade | 12% | 8.2.1, page 109 |
| Maximum sustained adverse grade | 8% | 8.2.1, page 109 |
| Maximum skid distance | 400 m | 8.2.1, page 109 |
| Circular routes | Not allowed | 8.2.1, page 109 |
| Annual road construction | 0.5-3 km/year | 8.2.1, page 110 |
| Planned new-road build period | 15 years | 8.2.1, page 110 |
| Annual cost of one percentage point of productive land in roads | About $75,000/year | 8.2.1, page 109 |
| Salvage share of average annual harvest, 2001-2005 | 18% | 8.1.3, page 108 |
| Partial-cutting share of Research Forest | 70% | 8.2.1, page 110 |

The $75,000 figure is an opportunity-cost and maintenance proxy for land taken
out of production. It is not a construction cost per kilometre.

### Landings and skid trails

Table 39, printed page 112, gives:

| Measure | Gavin Lake | Knife Creek | Total |
| --- | ---: | ---: | ---: |
| Net area (ha) | 4,922 | 3,117 | 8,040 |
| Existing landings (ha) | 24.1 | 34.2 | 58.3 |
| Landing area share | 0.5% | 1.1% | 0.7% |

Section 8.2.2 sets a maximum landing area of 0.25 ha, a landing service area of
30 ha, and a preference for roadside processing. Section 8.2.3 sets a target
skid-trail density of 10% of productive area, with trails 4 m wide and 40 m
apart.

### Access-plan maps

Appendix 11, printed pages 153-154, contains the Gavin Lake and Knife Creek
access plans. The legend distinguishes:

- primary, secondary, unimproved, and proposed roads;
- existing and rehabilitated landings;
- bridges, cattle guards, gates, gravel pits, railway crossings, pipeline
  crossings, rock blocks, and signs; and
- existing and proposed cutblocks, reserves, and wildlife-tree patches.

Both maps have a scale bar and north arrow. Neither has a coordinate grid or
coordinate labels. They are planning figures, not georeferenced GIS layers.
A warped raster is not a legal or field-verified access layer.

### Appendix 11 map recovery

`runbooks/recover_mwp3_access_maps.py` uses `figrecover 0.1.0a1` to render and
crop the two access maps and test their registration to known GIS boundaries.

- Knife Creek registers to the legal SUP boundary at a mean boundary distance
  of 4.48 px, about 10.68 m/px, with negligible rotation.
- Gavin Lake does not register to the managed-fragment union; the mean boundary
  distance is 49.17 px, and the fit is marked unresolved.

The Knife Creek overlay is `data/roads/plan_map/knife_creek_access_overlay.png`.
Green is the SUP boundary and blue is the public road layer. The public roads
align with the mapped road network well enough to confirm the georeference, but
not well enough to extract a complete network.

The Appendix 11 road tables and Table 37 disagree:

| Block | Measure | Appendix 11 | Table 37 | Difference |
| --- | --- | ---: | ---: | ---: |
| Knife Creek | Existing road length | 69.3 km | 86.2 km | -16.9 km |
| Knife Creek | Planned road length | 0.0 km | 77.2 km | -77.2 km |
| Gavin Lake | Existing road length | 91.9 km | 112.2 km | -20.3 km |
| Gavin Lake | Planned road length | 121.4 km | 136.1 km | -14.7 km |
| Knife Creek | Net area | 3,485.6 ha | 3,117 ha | +368.6 ha |
| Gavin Lake | Net area | 6,354.8 ha | 4,922 ha | +1,432.8 ha |

The maps use working-circle areas; Table 37 uses different net areas. These are
not rounding differences.

A test skeleton of the dark map lines produced about 70 km on Knife Creek,
close to the 69.3 km map total. Only about 5% of that skeleton fell within 10 m
of the public road layer, so the length match was coincidental: most of the
skeleton was contour or stream linework. The maps are useful for context and
class inventory, not for a road GIS layer.

### Log value and cost

Figure 7, printed page 21, shows average market value of log sales and adjusted
logging cost from 1988 to 2005, in 2005 dollars. The text says rising logging
costs and falling selling prices created budget pressure, and that AFRF
responded by increasing production, appointing a log broker, increasing
clearcutting, focusing on higher-value products, and working with loggers on
efficiency.

This is a historical trend, not a current price list and not a grade-specific
price matrix.

### Historical mills

The plan names historical mills but no current mill register:

- G.W.J. Moore Sawmill, 150 Mile House, date unknown;
- Knife Creek bush mills, 1940s to early 1960s;
- All-Fir Lumber sawmill, eastern end of Gavin Lake, mid-1950s to early 1960s;
- Merrill-Gardner/Merrill-Wagner sawmill, Gavin Lake, mid-1960s; and
- generic "large mills in Williams Lake" after the mid-1960s.

The transcribed references are in
`data/mills/mwp3_historical_mill_references.csv`. The plan gives no capacity,
accepted sort, coordinates, or price for any of them.

## What the plan does not provide

The plan does not contain:

- mill names, locations, operators, capacities, or current status;
- accepted log sorts by mill;
- grade-specific log prices;
- scaling rules or grade distributions;
- road construction, maintenance, haul, landing, or deactivation unit costs;
- a georeferenced road centerline layer;
- gate, bridge, culvert, or legal-access status;
- block-level harvest-system records; or
- the current approved order or legal access map.

Those gaps are recorded in `data/roads/gap_register.csv`.

## Legacy archive audit

The legacy AFRF Patchworks archive is `AFRF.zip`, SHA-256
`3652c493e21b1834e3e6d9c156f257fa1aa97f019df4672872d08ac1bf703a19`.

Findings:

- `AFRF/roads/` is present but empty.
- `AFRF/analysis/AFRF_H.pin` sets `useRoutes = false`.
- The pin defines `roadShapeFile = ../roads/access.shp` and
  `roadShapeKey = "ACCESS_"`, but the route tables are only loaded inside
  `if (useRoutes)`.
- `AFRF/scripts/02_build_roads.bsh` references
  `Roads_PW_v2.shp` and `Mills_PW.shp` at a legacy Windows path and uses
  `HAUL` as the cost type. Neither shapefile is in the archive.
- `AFRF/scripts/reports_Routes.bsh` still has a route-cost report for
  `Destination.CRB` and an active-road report, but there are no route tables.
- `AFRF/scripts/RATIO_ACCOUNTS.bsh` has commented-out
  `route.ratio.haul.CRB`, `route.ratio.build.CRB`, and
  `route.ratio.maint.CRB` accounts.

The legacy model planned a route model and then disabled it. The road and mill
spatial inputs were not archived.

## OneDrive payload audit

The acquired private DataLad payload at
`external/ubc-research-forests-data/` contains:

- `raw/ubc-research-forests-modelling-dropbox/992 Marshal/` - 24 plot
  polygons and eight tree-level plot shapefiles;
- `raw/ubc-research-forests-modelling-dropbox/KozakTaper_Version6/` - taper
  code, reports, and a provincial VRI sample; and
- `raw/ubc-research-forests-modelling-dropbox/LiDAR/` - 2009 FUSION
  LIDARBIN, 2013 LAS, 2019 rasters, and one 2024 LAZ tile.

It contains no road centerlines, mill register, log price list, scaling
records, harvest-system records, or road-cost workbook. The private payload is
not a delivered-wood source.

## Current instance layers

Knife Creek:

- `data/patchworks_knifecreek/spatial/roads.gpkg` has 44 public BC Forest
  Tenure road sections over 59.6 km.
- The 2007 plan records 86.2 km of existing roads.
- `data/patchworks_knifecreek/spatial/ROUTE_CONFIG_UNAVAILABLE.md` records that
  the route configuration is unavailable because destination, eligibility,
  access, and cost inputs are missing.

Gavin Lake:

- no road layer;
- no route configuration;
- no mill register; and
- no log-price basis.

## TSA23 extension audit

The TSA23 instance is the engineering template. Its route extension has:

- `config/ws4/route_c5_road.yaml`;
- `runtime/ws4/roads_c5/{segments,vertices,destinations,linkages}.csv`;
- three destinations: `destination.MILL_95_LBR`, `destination.MILL_694_LGH`,
  and `destination.MILL_733_LGH`;
- build, maintain, haul, and volume accounts, with total duplicates; and
- route-aware optimizer reports.

Network size:

- 465,263 segments;
- 72,299 vertices;
- 102,128 block linkages;
- about 229,718 km of total network length;
- about 8,447 km with zero build cost, treated as existing; and
- 426,316 segments with positive build cost.

Performance lessons:

- the all-open planned network is usable for report-only accounting;
- the existing-only network is too slow for optimization; and
- the reduced candidate network produced 7,587 unrouted rows and is not a valid
  road-aware optimization fixture.

The TSA23 mill identities and cost rates are not AFRF values. Reuse the schema,
the account pattern, and the performance lesson, not the numbers.

## FEMIC log-grade audit

The route model is `ws4.roads`, not `femic.roads`. The relevant modules are:

- `ws4.roads.network` - `load_route_tables`, `load_route_eligibility`,
  `existing_segments`, `RouteNetwork`, `route`, `route_length`, `route_cost`,
  and `nearest_destination`;
- `ws4.roads.accounts` - `RouteModel`, `RouteAccount`, `DuplicateAccount`,
  `load_route_config`, `RouteCostLedger`, and `resolve_account_values`; and
- the CLI and web surfaces that accept `--route-config` and serve
  `used_roads.csv`.

The log-grade engine is `femic.fmg.patchworks` with the `log-grades` BTC
indicator bank. It supports:

- explicit grades `Logs_Grade_D`, `F`, `H`, `I`, `J`, `U`, `X`, and `Y`;
- `Logs_Grade_All` as an opt-in, not part of the additive family;
- scaling to harvested volume;
- per-grade and per-treatment ratio weights;
- species-by-grade splits; and
- derived value products.

The shipped price matrices are `second_growth_coast_2025` and
`old_growth_coast_2025`. They are coastal. The TSA23 economic datasets
(`compiled_ft_econ`, `compiled_ft_econ_bc`, and `compiled_sf_risk`) contain no
`Logs_Grade_*` product labels, so the TSA23 configuration has not been proven
through a compiled dataset.

## Data request

Please provide, or point to, the following AFRF records:

1. `Roads_PW_v2.shp` and `Mills_PW.shp`, or their current equivalents.
2. The legacy route tables: `vertices`, `segments`, `destinations`, and
   `linkages`.
3. The haul-cost table used by `Mills_PW.shp`'s `HAUL` field.
4. Current AFRF road inventory: centerlines, class, surface, status, bridges,
   gates, culverts, deactivation, and right-of-way width.
5. Road construction, maintenance, haul, landing, and deactivation costs.
6. Mill register: name, location, operator, capacity, species and grade
   acceptance, minimum volume, and current status.
7. Log price lists, sales records, scaling records, and grade distributions.
8. Harvest-system records, block prescriptions, slope/terrain data, and
   operational constraints.
9. The current approved management plan or order that governs each block.
10. Publication permission for each layer: public, derived, or private-only.

## Public supplementary data

Two public BC sources fill part of the gap. They are candidate references, not
AFRF records.

### Major timber processing facilities

`runbooks/build_afrf_mill_candidates.py` reads the BC Major Timber Processing
Facilities feature layer (OGL-BC) and selects mills within 100 km of the Knife
Creek or Gavin Lake block centroids. The result is
`data/mills/afrf_mill_candidates.csv`: 20 candidate rows over 16 mills, with
location, product class, status, and estimated annual capacity.

The nearest operational mills include Williams Lake lumber, plywood, veneer,
pellet, and log-home facilities, plus 100 Mile House lumber and log-home
facilities and Quesnel lumber, plywood, veneer, chip, and pulp facilities. The
exact distance table is in the CSV.

The layer gives capacity, not demand. It also does not give accepted log sorts.
The `candidate_sort` column is inferred from the mill product class and is
marked `sort_confirmed = False`. It is a screening label, not an eligibility
rule.

### Interior log market and grades

`runbooks/build_bc_interior_price_reference.py` transcribes:

- the BC Interior Log Market Report for June-August 2026; and
- the BC Timber Scaling Manual Chapter 9 interior grade codes.

`data/log_prices/bc_interior_log_market_2026-08.csv` gives species-group and
sort volumes and average prices in CAD/m3. It is a regional market average, not
an AFRF sales record and not a grade-by-grade price matrix.

`data/log_prices/bc_interior_grade_codes.csv` records the five interior grades:
Z (firmwood reject), 6 (undersized), 1 (premium sawlog), 2 (sawlog), and 4
(lumber reject). These are not the coastal D/F/H/I/J/U/X/Y grades used by the
current FEMIC `log-grades` recipe. A crosswalk is a required decision, not an
assumption.

### Harvest-system screening

`runbooks/classify_kc_harvest_systems.py` measures slope from the 2024 LidarBC
1 m DEM for the 211 Knife Creek split blocks. The screening result is:

- 198 blocks are ground-based candidates;
- 13 blocks are cable candidates; and
- no block has at least 50% of its area above 60% slope.

The mean block has about 9.7% of its area above 30% slope and 1.3% above 60%.
The maximum block fraction above 30% is about 96%; the maximum above 60% is
about 41%.

The 50% threshold is a reproducible screening choice, not the plan's wording.
The output is not a field operability or cable-feasibility determination. See
`data/harvest_systems/README.md`.

## What can proceed without the missing data

- The 2007 plan extraction and source register are complete.
- The public Knife Creek road layer can be used for map context and a
  reconciliation check, not as a route model.
- A public Gavin Lake road layer can be fetched for map context, with the same
  caveat.
- The route-config schema and the log-grade scaffolding can be built and tested
  against synthetic fixtures, but not presented as an AFRF result.

## What cannot proceed without the missing data

- AFRF route costs or a defensible least-cost route model.
- Mill destinations, capacities, or accepted sorts.
- An interior price matrix and value accounts.
- A claim that the model represents current AFRF access or a legal operating
  plan.

## Related files

- `planning/p7-roads-logs-mills.md`
- `data/roads/source_manifest.json`
- `data/roads/gap_register.csv`
- `data/patchworks_knifecreek/spatial/ROUTE_CONFIG_UNAVAILABLE.md`
- `reference/AFRF-management-working-plan-3-2007.pdf`
