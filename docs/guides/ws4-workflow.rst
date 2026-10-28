ws4 Workflow
============

Status
------

There are two structural ws4 datasets:

- ``ws4/dataset_v1_synthetic`` — 4 synthetic 1 ha blocks, 23 canonical tracks,
  25 treatments, 575 curves;
- ``ws4/dataset_kc_spatial_v1`` — 160 clipped VRI blocks (3,481.77 ha), 92
  HMZ-specific tracks, 49 treatments.

Both pass ``ws4 validate``. The spatial dataset enforces HMZ track offers:
M = Low/Moderate, L = Low only, A = all, U = no treatment. It is still a
structural fixture, not a KC operating dataset: the tree lists are PSP-derived,
not KC CFI, and the clump rule is not spatial.

Assembly sequence
-----------------

1. Build the stem-list manifest and the FVS-BC state library; v1 and its
   canonical graph are in ``ws4/state_library_v1``.
2. Export the library as ws4 tables:
   ``tracks``, ``strata``, ``treatments``, ``curves``, ``features``,
   ``products``, ``protoaccounts``, ``accounts``, and ``groups``.
3. Build ``fragments`` by assigning each block to an initial state and AU.
4. Build ``blocks`` from the block geometry and area.
5. Write the dataset manifest.
6. Validate with ``ws4 validate``.
7. Build a baseline selection schedule and simulate.

Dataset contract
----------------

The ws4 dataset is the contract. The state-transition library is an upstream
artifact; it is not read by the simulator or optimizer directly.

The required tables and columns are the ws4 schema:

- ``fragments``: fragment_id, block_id, area_ha, age, track_id;
- ``blocks``: block_id, track_id, offset, area_ha;
- ``tracks``: track_id, name;
- ``strata``: track_id, offset, next_age, cycle;
- ``treatments``: track_id, begin, end, treatment, new_track, offset, retain;
- ``curves``: curve_id, x, y;
- ``features``: track_id, label, curve_id;
- ``products``: track_id, treatment, label, curve_id;
- ``accounts`` / ``protoaccounts``: group, attribute, account, sum; and
- ``groups``: block_id, group.

The exact column order and types are in the ws4 compiled-dataset reference.

Baseline
--------

The baseline is a selection-only schedule:

- every block starts on its assigned state track;
- a block becomes eligible for a selection entry after the cutting cycle;
- the schedule chooses one reviewed regime per block;
- the default regime set is GWM 2007, with Table 29 as a named alternative;
- the run reports harvest, growing stock, habitat indicators, and entry
  frequency; and
- no clearcut treatment exists in the dataset.

The baseline is not an optimization. It is a reproducible reference that shows
the model runs and the constraints are visible.

Optimization
------------

The first optimization should be a regime-portfolio question:

- choose selection entries by block and period;
- meet even-flow or non-declining harvest targets;
- respect the cutting cycle, the 4–10-tree clump/opening pattern, and the HMZ
  floors; and
- compare the baseline with the optimized schedule.

A global accounting run across Gavin Lake and Knife Creek is a later, merged
model question. See the merge ADR.

Evidence
--------

Every run writes:

- the dataset manifest and source hashes;
- the target set;
- the schedule;
- the seed and runtime;
- the account values and target report; and
- a short JSON summary under `ws4/evidence/`.

Generated runtime files stay under `ws4/runtime/` and are ignored by Git.
