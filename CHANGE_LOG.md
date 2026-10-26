# Change Log

Newest entries last. Each milestone gets a dated entry that matches the roadmap
status and the GitHub issue comments.

## 2026-10-26

- Created `femic-afrf-knifecreek-instance` from the UBC-FRESH dev workflow
  seed. The seed supplied the agent contract, roadmap, docs skeleton, validator,
  dashboard, and tests.
- Recorded the Knife Creek modelling decision: the block is predominantly IDF,
  Douglas-fir is relatively shade tolerant there, and almost the whole block is
  under mule-deer winter-range constraints. Even-aged clearcutting is largely
  unavailable, so the instance is an uneven-aged continuous-cover selection
  model.
- Recorded that VDYP and TIPSY are not the primary growth engine for this
  regime. The engine is FVS-BC through `UBC-FRESH/fresh-fvsbc`, pinned at
  commit `ca33d0e26a079a72add5108f1b182b798b0c4e3e` (package 0.11.0).
- Recorded the state-transition design: FVS-BC per-tree and cut-list outputs
  become a library of pre-cut states, residual states, and growth curves, which
  ws4 consumes as tracks, treatments, curves, features, and products.
- Recorded the data-acquisition boundary. No field data, stem lists, FVS-BC
  runs, or ws4 dataset are committed yet.
- Ran the green dashboard in the Phase 0 branch. The plan is to merge this
  bootstrap via the Phase 0 pull request and then register the repository as a
  submodule of `UBC-FRESH/femic` at
  `external/femic-afrf-knifecreek-instance`.
- Linked Phase 0 to parent issue #1 and child issues #2-#6. Phase 1 (data acquisition and stem lists) is planned under parent issue #7 and is not active.
- Merged Phase 0 in pull request #13 (commit `beafb5a`). P0 is complete; P1 remains planned under parent issue #7.
- Activated Phase 1 under parent issue #7. Completed P1.1: the legal Knife
  Creek boundary is Special Use Permit S15382, "Research or Educational",
  ACTIVE, 3,533.1341 ha. It was found through the FEMIC BCDC resolver and
  fetched from the public Forest Tenure Special Use Permit Polygon WFS layer.
  The selected polygon is `data/boundaries/knife_creek_sup_S15382.gpkg` with
  provenance in `metadata/boundary_source.yaml`.
- Recorded that FADM_TSA places the block in Williams Lake TSA (TSA 29), and
  that the TSA boundary is not the research-forest boundary.
- Recorded the 46.13 ha difference between the SUP permit block area
  (3,533.1341 ha) and the published Management and Working Plan area (3,487 ha).
  The SUP polygon is the legal gross boundary; the net area waits on the VRI
  join.
