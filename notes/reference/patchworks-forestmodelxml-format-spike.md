# Patchworks ForestModelXML format spike

Date: 2026-10-29
Task: P3.1 / issue #61
Status: **H-matrix lane buildable; ForestModelXML blocked**

## Question

Can we author a valid Patchworks `ForestModelXML` for the Knife Creek package
from the material in this repository?

## Sources checked

- Gavin Lake archive inventory and intake notes: the archive contains
  `fragments.shp`, `tracks/H/`, `topo_fragments.csv`, the pin and scenario
  scripts, but **no ForestModelXML**.
- The Gavin crosswalk explicitly says the archive has no recipe and that ws4
  ingests the compiled matrix rather than rebuilding it.
- Local `/srv/shared-data/gep` search: no `ForestModelXML` example, schema or
  compiler.
- Public web search for `"ForestModelXML"` and Patchworks forestry: no usable
  schema or example found.

## Decision

Proceed with the **compiled H-matrix lane**:

- `fragments.shp`;
- `tracks/H/` tables;
- `topo_fragments.csv`;
- roads;
- `KC_H.pin` and scenario scripts;
- ws4 ingest and validation.

Do **not** hand-write a ForestModelXML and call it validate or compatible. The
recipe lane remains blocked until we have at least one of:

1. a known-valid ForestModelXML and its Patchworks version;
2. the Patchworks schema/compiler;
3. authoritative Patchworks documentation from the vendor or AFRF.

## Consequences

- P3.2-P3.8 can proceed on the H-matrix lane.
- P3.1 remains open/blocked for recipe parity.
- The closeout must say “H-matrix compatible; ForestModelXML not validated.”
- If a valid recipe arrives, P3.3 curves and P3.4 accounts can be reused as
  inputs; the spatial and matrix layers do not need redesign.
