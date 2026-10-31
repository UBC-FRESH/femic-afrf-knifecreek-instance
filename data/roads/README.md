# Roads, log sorts, and mills data

This directory holds derived evidence for P7. It is not a legal access layer,
a route model, or a complete AFRF cost and mill dataset.

## Source extraction

`runbooks/build_mwp3_roads_audit.py` reads the 2007 AFRF Management and Working
Plan #3, verifies its SHA-256 and page count, and writes:

- `mwp3_table37_roads.csv` - existing and planned road length and area;
- `mwp3_table38_specs.csv` - road construction specifications;
- `mwp3_table39_landings.csv` - existing landing area;
- `mwp3_harvest_systems.csv` - harvest-system classes from section 8.1.1;
- `mwp3_access_assumptions.csv` - grades, skid distance, construction program,
  and landing/skid-trail assumptions;
- `mwp3_relevant_text.txt` - extracted text for review;
- `context/mwp3_gavin_access.jpg` and
  `context/mwp3_knife_creek_access.jpg` - rendered Appendix 11 maps; and
- `source_manifest.json` - source hash, pages, caveats, and outputs.

`gap_register.csv` records the missing road, mill, price, capacity, and
accepted-sort inputs.

## Caveats

- The Appendix 11 maps are schematic: scale bar and north arrow, no coordinate
  grid.
- Table 37 is a reconciliation target, not a segment-level road inventory.
- The $75,000/year per 1% productive-land figure is not a construction cost
  per kilometre.
- The plan does not contain mill capacities, accepted sorts, grade-specific
  prices, or road unit costs.
- No file here is a legal access determination.

## Next step

Acquire the AFRF road, mill, cost, and price records listed in
`notes/reference/afrf-roads-logs-mills-sources.md`. Do not substitute TSA23
mill identities or C5-class cost rates for AFRF values.

## Public-access proximity

`runbooks/measure_kc_public_access.py` measures straight-line distance from each
split block to the public road layer.

- `kc_public_access_nearest.csv` - one row per block with the nearest public
  road section and distance; and
- `kc_public_access_metadata.json` - counts and caveats.

Current result: 59 blocks within 100 m, 169 within 400 m, and 42 beyond 400 m.
This is an access-context check, not a route linkage or legal access
determination. The public layer is incomplete against Table 37.

## Appendix 11 access maps

`plan_map/` records the figrecover recovery of the two scanned access maps.
Knife Creek registers to the SUP boundary at about 4.5 px mean boundary
distance; Gavin Lake is unresolved against the managed-fragment union. The map
road tables disagree with Table 37 and are transcribed, not reconciled. See
`plan_map/README.md`.
