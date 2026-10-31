# P7 - Roads, log sorts, and mills

Date: 2026-10-31
Status: planned
Parent issue: TBD
Branch: `feature/p7-roads-logs-mills`

## Goal

Turn the Knife Creek and Gavin Lake estate models from volume-only models into
delivered-wood models. The phase adds:

- a road network with block access, route choice, build cost, maintenance cost,
  and haul cost;
- a mill register with location, capacity, accepted products, and
  product-to-mill eligibility;
- log-grade and log-sort products with a dated interior price basis;
- harvest-system classes and the operational constraints that decide whether a
  block can be cut; and
- route, sort, and cost accounts that can be reported, mapped, and later used
  by the wood-supply analyst.

The phase does not set AAC, tune even-flow, or claim legal access or legal
compliance. It builds the delivered-wood layer that those decisions can use.

## What the source audit found

### The 2007 management plan has the policy and the maps, not the cost ledger

The public AFRF *Management and Working Plan #3* (effective 1 January 2007) is
the main planning source. The relevant material is:

- section 8.1, timber harvesting systems and block layout;
- section 8.2, access, roads, landings, and road specifications;
- Table 37, existing and planned road length and area by block;
- Table 38, road construction specifications;
- Appendix 11, the Gavin Lake and Knife Creek access-plan maps; and
- Figure 7, average log value and logging cost, 1988-2005, adjusted to 2005
  dollars.

Table 37 gives the reconciliation targets:

| Access measure | Gavin Lake | Knife Creek | Total |
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

The plan also states:

- ground-based harvesting dominates, with less than 5% of net area above 30%
  slope;
- cable systems are expected on substantial Gavin Lake areas above 30% slope;
- areas above 60% slope are generally inaccessible;
- the master road plan assumes a maximum sustained favourable grade of 12%, a
  maximum sustained adverse grade of 8%, a maximum skid distance of 400 m, and
  no circular routes;
- the annual construction program is 0.5-3 km, with all planned new roads
  intended within 15 years;
- roads are generally permanent because partial cutting requires repeated
  entries, but temporary roads and landings are rehabilitated within about two
  years; and
- each percentage point of productive land in roads is treated as an annual
  cost of about $75,000 from lost productivity, capital, and maintenance.

Those are planning assumptions. They are not a construction-cost schedule, a
mill list, or a log-price list.

### The legacy archive did not ship a road or mill model

The legacy AFRF Patchworks archive (`AFRF.zip`, SHA-256
`3652c493e21b1834e3e6d9c156f257fa1aa97f019df4672872d08ac1bf703a19`) contains:

- `AFRF/analysis/AFRF_H.pin`, with `useRoutes = false`;
- an empty `AFRF/roads/` directory;
- `AFRF/scripts/02_build_roads.bsh`, which references
  `Roads_PW_v2.shp` and `Mills_PW.shp` at a legacy Windows path; and
- `AFRF/scripts/reports_Routes.bsh`, which still contains route-report code
  for `Destination.CRB`, but no route tables to run it on.

The pin also contains commented-out `route.ratio.haul`, `route.ratio.build`,
and `route.ratio.maint` accounts. The road model was planned, then disabled.
The spatial inputs were not archived.

### The OneDrive payload is inventory, taper, and LiDAR only

The private DataLad store
`external/ubc-research-forests-data/` currently contains:

- `992 Marshal/`: 24 plot polygons and eight tree-level plot shapefiles;
- `KozakTaper_Version6/`: taper code, reports, and a provincial VRI sample;
  and
- `LiDAR/`: 2009 FUSION LIDARBIN, 2013 LAS, 2019 rasters, and one 2024 LAZ
  tile.

It contains no road centerlines, mill register, log price list, scaling
records, harvest-system records, or road-cost workbook. The source inventory
must be treated as incomplete for this phase.

### Knife Creek has a public road layer, but not a route model

`data/patchworks_knifecreek/spatial/roads.gpkg` has 44 public BC Forest Tenure
road sections over 59.6 km. The 2007 plan records 86.2 km of existing roads on
Knife Creek. The difference is a real reconciliation gap: the public layer is a
tenure-road layer, not a field-verified AFRF access inventory.

`data/patchworks_knifecreek/spatial/ROUTE_CONFIG_UNAVAILABLE.md` correctly says
that a route configuration is unavailable because the destination assignment,
product eligibility, gate and bridge status, cost rates, and block-to-network
linkage are missing.

### Gavin Lake has no road layer at all

The Gavin Lake instance has the legacy blocks and topology, but no road
centerlines, no route tables, no mills, and no route config. The 2007 plan
records 112.2 km of existing roads and 136.1 km planned, but the spatial data
have not been acquired.

### The TSA23 extension is the engineering template, not the AFRF data

The nearby TSA23 instance has a working route-model extension:

- `config/ws4/route_c5_road.yaml`;
- `runtime/ws4/roads_c5/{segments,vertices,destinations,linkages}.csv`;
- three mill destination accounts: `destination.MILL_95_LBR`,
  `destination.MILL_694_LGH`, and `destination.MILL_733_LGH`;
- build, maintain, haul, and volume accounts, plus total duplicates; and
- route-aware optimization reports in `reports/ws4-road-aware-opt.md` and
  `reports/ws4-road-aware-attempt.md`.

The network is large: 465,263 segments, 72,299 vertices, 102,128 block
linkages, and about 229,718 km of total network length, of which about
8,447 km has zero build cost and is treated as existing. The all-open planned
network is usable for report-only accounting, but the existing-only network and
the reduced candidate network were not viable for optimization: the existing
network was too slow, and the reduced network produced 7,587 unrouted rows.

Reuse the schema, account pattern, and performance lessons. Do not reuse the
TSA23 mill identities, haul rates, build rates, or maintenance rates as if they
were AFRF values.

### The FEMIC log-grade path exists, but the price basis is coastal

`femic.fmg.patchworks` already supports a `log-grades` BTC indicator bank. The
default compile recipe emits `Logs_Grade_D`, `F`, `H`, `I`, `J`, `U`, `X`, and
`Y`, excludes `Logs_Grade_All` by default, scales the explicit grades to
harvested volume, and can emit species-by-grade volume and value products. The
supported surface includes:

- `btc_indicator_banks: [log-grades]`;
- `btc_indicator_bank_compile_recipes`;
- `ratio_scaling_factors`, treatment overrides, and state overrides;
- `species_grade_split` with `price_matrix_selector` and
  `species_market_proxies`; and
- `emit_value_products`.

The shipped price matrices are `second_growth_coast_2025` and
`old_growth_coast_2025`. Those are coastal price systems and are not an
interior Williams Lake price basis. The TSA23 compiled economic datasets
(`compiled_ft_econ`, `compiled_ft_econ_bc`, `compiled_sf_risk`) contain no
log-grade product labels, so the TSA23 log-grade configuration has not yet
been proven through a compiled dataset.

The project can reuse the compile path and the overlay mechanism. It must add
an interior species-and-grade price matrix and an explicit species crosswalk.

### The roads module is `ws4.roads`

There is no `femic.roads` package in the current checkout. The route model is
`ws4.roads`, documented in `ws4/docs/reference/roads.rst` in the WS4 source
tree. Its main public surface is:

| Module | Function or type | Use |
| --- | --- | --- |
| `ws4.roads.network` | `load_route_tables(root)` | Load the four route tables |
| `ws4.roads.network` | `load_route_eligibility(path)` | Load product-to-destination eligibility |
| `ws4.roads.network` | `existing_segments(segments)` | Identify zero-build-cost existing roads |
| `ws4.roads.network` | `RouteNetwork.from_tables(...)` | Build the graph |
| `ws4.roads.network` | `.route`, `.route_length`, `.route_cost` | Least-cost path and cost |
| `ws4.roads.network` | `.nearest_destination(...)` | Least-haul-cost eligible mill |
| `ws4.roads.accounts` | `RouteModel` | Eligibility, destination choice, surplus |
| `ws4.roads.accounts` | `RouteAccount` | Haul, build, maintain, or volume account |
| `ws4.roads.accounts` | `DuplicateAccount` | Copy or aggregate route accounts |
| `ws4.roads.accounts` | `load_route_config(path)` | Load the YAML route configuration |
| `ws4.roads.accounts` | `RouteCostLedger` | Route cost, network, used-road, and route tables |
| `ws4.roads.accounts` | `resolve_account_values(...)` | Combine route and simulated accounts |

`ws4 simulate` and `ws4 optimize` accept `--route-config`. The web service can
serve the source road layer and the run's `used_roads.csv` overlay.

## Design

The delivered-wood layer is a chain of explicit, reviewable tables:

```text
MWP #3, AFRF GIS, mill records, price lists
        |
        +--> source register and provenance
        |
        +--> roads.gpkg --> vertices.csv, segments.csv, linkages.csv
        |                         |
        |                         +--> ws4.roads RouteNetwork
        |                                  |
        +--> mills.csv --> destinations.csv, eligibility.csv
        |                                  |
        |                                  +--> route accounts
        |
        +--> interior price matrix --> FEMIC log-grades --> product accounts
        |
        +--> harvest-system table --> treatment eligibility and cost accounts
```

The route tables follow the established format:

| Table | Required fields |
| --- | --- |
| `vertices.csv` | `vertex_id`, `x`, `y` |
| `segments.csv` | `segment_id`, `from_vertex`, `to_vertex`, `length_m`, `haul_cost`, `build_cost`, `maintain_cost` |
| `destinations.csv` | `name`, `vertex_id` |
| `linkages.csv` | `block_id`, `vertex_id`, `link_distance_m` |

The destination name is an account name, not a mill ID. The mill register keeps
the identity and the evidence; `destinations.csv` keeps the account name that
the route model uses.

Additional derived tables:

| Table | Purpose |
| --- | --- |
| `mills.csv` | Mill identity, location, operator, capacity, accepted species and grades, status, source, date |
| `eligibility.csv` | Product-to-destination eligibility |
| `harvest_systems.csv` | Block-level system, slope class, access constraint, source |
| `log_prices.yaml` | Dated interior species-by-grade price matrix, with provenance |
| `source_manifest.json` | Hash, path, date, licence, and use of every source |

## Work packages

### P7.1 Source audit and extraction

- Extract the road, harvest-system, log-value, and access material from the
  2007 plan. Record page numbers and hashes.
- Render the Appendix 11 access-plan pages and record that they are schematic:
  they have a scale bar and north arrow but no coordinate grid.
- Inventory the private OneDrive payload and the legacy `AFRF.zip`; record what
  is present, absent, or unreadable.
- Reconcile the legacy pin, the empty `AFRF/roads/` directory, and the missing
  `Roads_PW_v2.shp` and `Mills_PW.shp` references.
- Write the AFRF data request in `notes/reference/afrf-roads-logs-mills-sources.md`.

Deliverables:

- `notes/reference/afrf-roads-logs-mills-sources.md`;
- `data/roads/source_manifest.json`; and
- a dated gap list for Ionut Aron and AFRF operations.

Acceptance: every fact used by later tasks points to a page, file, hash, or
named source; missing data are recorded as missing, not filled by assumption.

### P7.2 Road network and access topology

- Acquire or build the best available road centerline for each block.
- Classify each segment as existing, planned, permanent, temporary, active,
  deactivated, or unknown.
- Assign a road class and, where evidence exists, surface, bridge, gate,
  culvert, and seasonal-access attributes.
- Reconcile length and right-of-way area against Table 37. Record the residual
  and do not silently rescale the public layer to match the plan.
- Build the four route tables, with vertex coordinates and one block-to-access
  linkage per block.
- Link split Knife Creek blocks at the split-block level, with the parent block
  retained for audit.
- Apply the 400 m maximum skid distance. Mark blocks beyond it as unreachable
  or requiring a new road, rather than assigning a false linkage.

Deliverables:

- `data/roads/{block}/roads.gpkg`;
- `data/roads/{block}/{vertices,segments,destinations,linkages}.csv`;
- `data/roads/{block}/roads_metadata.json`; and
- a reconciliation table against Table 37.

Acceptance: the network is connected, every block has one explicit linkage or
an explicit unreachable flag, and the route tables load through
`ws4.roads.network.load_route_tables`.

### P7.3 Mills, destinations, and eligibility

- Build a mill register with name, operator, coordinates, status, capacity,
  accepted species, accepted log sorts, minimum volume, and source date.
- Distinguish mill capacity from mill demand and from the route model's
  destination account.
- Build product-to-destination eligibility. A product that is not eligible for
  any mill is surplus, not silently routed.
- Add delivery or capacity constraints only where the source states them.
- Use the TSA23 route config as a pattern, but not its mill identities or
  rates.

Deliverables:

- `data/mills/mills.csv`;
- `data/mills/eligibility.csv`;
- `data/mills/destinations.csv`; and
- `data/mills/mills_metadata.json`.

Acceptance: every destination in the route config has a mill record; every
mill record has a source; no capacity or acceptance rule is inferred from a
mill name.

### P7.4 Log sorts and prices

- Define the interior species and grade crosswalk for the AFRF species set.
- Build a dated interior price matrix in CAD/m3, with source, region, species,
  grade, and period.
- Add the matrix through the FEMIC recipe overlay; do not edit the shipped
  coastal matrices in place.
- Configure the `log-grades` bank with explicit grades, harvested-volume
  scaling, species splits, and value products.
- Prove that the explicit grade family sums to harvested volume and that the
  value accounts reconcile to grade volume times price.
- Keep the coastal matrices as a named sensitivity, not the base case.

Deliverables:

- `config/log_prices.afrf.yaml`;
- `config/log_grade_species_crosswalk.csv`;
- a compiled dataset with `Logs_Grade_*` products; and
- a grade-reconciliation report.

Acceptance: the grade family is additive, the price basis is interior and
dated, and every product label has a resolved price or an explicit unpriced
flag.

### P7.5 Harvest systems and operational constraints

- Build slope, terrain, riparian, road-access, and seasonal constraints from
  the best available DEM and spatial layers.
- Classify each block as shortwood, feller-buncher/grapple, hand-falling/cable,
  or inaccessible, using the 2007 plan's slope thresholds.
- Apply the 30% and 60% slope thresholds, the 400 m skid limit, and the
  no-circular-route assumption.
- Add harvest-system eligibility to treatments. Add a system cost only where a
  source supports it.
- Keep Knife Creek's selection and GWM constraints intact; do not let the
  harvest-system layer override the legal structure.

Deliverables:

- `data/harvest_systems/{block}_systems.csv`;
- `data/harvest_systems/{block}_constraints.gpkg`; and
- a treatment-eligibility audit.

Acceptance: every block has a system class and a constraint record; no block is
assigned a system that contradicts its slope or legal constraint.

### P7.6 Knife Creek integration

- Use the frozen model-of-record `ws4/dataset_kc_au_stages_split_volume_v1`
  and its 211 split blocks. Do not rebuild the growth or volume basis in this
  phase.
- Add the route config, mill destinations, log-grade products, and harvest
  system accounts to the KC dataset.
- Run a no-cut baseline and one selection scenario with route accounting.
- Write `route_values.csv`, `network_table.csv`, `route_cost_report.csv`, and
  `used_roads.csv`.
- Serve the source road layer and the used-road overlay in the web map.
- Keep the AAC diagnostics frozen. The route layer is a cost and delivery
  layer, not a new AAC target.

Deliverables:

- `ws4/dataset_kc_au_stages_split_volume_roads_v1/`;
- `config/kc_route.yaml`;
- `ws4/runtime/kc_roads_v1/`; and
- a web map screenshot with used roads.

Acceptance: the dataset validates, the runs have zero unrouted products, the
route accounts reconcile, and the used-road overlay renders.

### P7.7 Validation, uncertainty, and publication

- Reconcile road length and area to Table 37, with the Knife Creek public-layer
  gap explained.
- Check route connectivity, destination eligibility, build-once behavior,
  maintenance per period, and haul distance.
- Run low/base/high price and cost sensitivities.
- Record the performance envelope: report-only all-open network versus
  optimizer use, and the conditions under which a reduced network is valid.
- Publish a source note and a methods page. Do not publish raw private data or
  claim legal access.

Deliverables:

- `notes/reports/p7-roads-logs-mills-validation.md`;
- `notes/reports/p7-roads-logs-mills-uncertainty.md`; and
- docs pages for the delivered-wood layer.

Acceptance: the validation report states what is measured, what is assumed,
what is missing, and what is not claimed.

## Data request to AFRF

The phase is blocked on source data that the archive does not contain. Request:

1. `Roads_PW_v2.shp` and `Mills_PW.shp`, or their current equivalents.
2. The route tables used by the legacy model: `vertices`, `segments`,
   `destinations`, and `linkages`.
3. Current AFRF road inventory: centerlines, class, surface, status, bridges,
   gates, culverts, deactivation, and right-of-way width.
4. Road construction, maintenance, haul, landing, and deactivation costs.
5. Mill register: name, location, operator, capacity, species and grade
   acceptance, minimum volume, and current status.
6. Log price lists, sales records, scaling records, and grade distributions.
7. Harvest-system records, block prescriptions, slope/terrain data, and
   operational constraints.
8. The current approved management plan or order that governs the block.
9. Publication permission for each layer: public, derived, or private-only.

## Risks and controls

| Risk | Control |
| --- | --- |
| Road and mill data are absent | Record the gap; request the source; do not invent values |
| Appendix 11 maps are schematic | Use them for context only; do not present a warped raster as a legal layer |
| Public KC road layer is incomplete | Report the Table 37 residual; do not rescale silently |
| TSA23 rates are not AFRF rates | Reuse schema and code, not numbers |
| Coastal log prices are wrong for the interior | Add an interior matrix and keep the coast as sensitivity |
| Mill capacities and sorts are unknown | Leave capacity unconstrained; mark eligibility unknown |
| Full network is slow in optimization | Measure first; use report-only all-open or a connected reduced network |
| Roads double-count THLB area | Reconcile right-of-way area against the landbase and document the treatment |
| Legal access is unknown | Label the layer as modelled access, not legal access |

## Definition of done

- The source register and gap list are complete.
- Both blocks have a road network, route config, mill register, and sort basis,
  or an explicit statement of what is still missing.
- The KC model-of-record has a delivered-wood run with route and sort accounts.
- The Gavin baseline has the same layer at its own block resolution.
- The validation report reconciles to Table 37 and states every unresolved
  residual.
- No document presents the result as a statutory AAC, a legal access
  determination, or a legal-compliance finding.
