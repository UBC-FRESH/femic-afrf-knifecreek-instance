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
