# Harvest-system screening

`runbooks/classify_kc_harvest_systems.py` measures slope from the 2024 LidarBC
1 m DEM and assigns a candidate harvest-system class to each Knife Creek split
block.

The 2007 management plan says:

- ground-based systems dominate where less than 5% of net area exceeds 30%
  slope;
- cable systems are expected where a substantial area exceeds 30% slope; and
- areas above 60% slope are generally inaccessible.

The screening rule is reproducible and deliberately simple:

- `inaccessible_candidate` if at least 50% of the valid block area is above
  60% slope;
- `cable_candidate` if at least 50% is above 30% slope; and
- `ground_based_candidate` otherwise.

This is **not** a field operability, cable feasibility, or legal-access
determination. The 2007 plan does not define "substantial" as a percentage; the
50% threshold is a modelling choice, not a policy rule.

Outputs:

- `kc_blocks_slope_2024.csv` - block slope fractions and candidate class;
- `kc_blocks_slope_2024.gpkg` - block polygons with the same fields; and
- `harvest_systems_metadata.json` - source, thresholds, and caveats.
