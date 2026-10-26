# Data acquisition runbook

Status: Phase 1 procedure. No source data is committed yet.

## 1. Boundary

1. Obtain the legal Knife Creek boundary from AFRF or the responsible
   provincial source.
2. Record the source, licence, retrieval date, and checksum.
3. Transform to EPSG:3005 only as a derived copy; keep the source CRS.
4. Validate the polygon: area, closure, self-intersections, and a plausible
   location near UTM 10U 575165 E, 5767955 N.
5. Store the boundary under `data/boundaries/` if it is public; otherwise keep
   it outside Git and record its checksum.

## 2. Inventory and BEC

1. Acquire VRI or the AFRF forest-cover inventory.
2. Acquire the current BEC and site-series mapping.
3. Join on the best available key; record the match rate and the unmatched
   area.
4. Record the attribute mapping in a small YAML or Markdown table.

## 3. Disturbance

1. Acquire the 2013 wildfire perimeter and severity.
2. Acquire the harvest history and any salvage history.
3. Assign each polygon an origin and a time-since-disturbance.
4. Record the unresolved area.

## 4. Mule-deer constraints

1. Obtain the winter-range designation and the applicable objectives.
2. Record whether each constraint is spatial, structural, or both.
3. Do not invent a value. If a constraint cannot be mapped, record a gap.
4. Review the mapping with the maintainer before it enters a scenario.

## 5. Stem lists

1. Prefer measured CFI or research plot tallies.
2. If none are available, reconstruct a stand table from VRI species, age,
   site index, and density.
3. Use `nemora` to generate a synthetic population and label it as synthetic.
4. Record the generator, parameters, and uncertainty.

## 6. Audit

Write a Phase 1 audit with:

- total boundary area;
- joined area and unmatched area;
- BEC coverage;
- site-index coverage;
- area inside and outside the 2013 burn;
- mule-deer class coverage;
- age and species distributions; and
- every unresolved or conflicting source.

Acceptance is a known join and a known gap, not a clean load.
