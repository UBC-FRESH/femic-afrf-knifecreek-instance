# AFRF Knife Creek Instance

A **ws4 forest-estate model instance** for the Knife Creek block of the UBC Alex
Fraser Research Forest (AFRF).

Knife Creek is different from Gavin Lake. Most of the block is Interior
Douglas-fir (IDF), the Douglas-fir is relatively shade tolerant there, and
almost the whole block carries mule-deer winter-range constraints. The
practical consequence is that even-aged clearcutting is largely unavailable.
The model therefore has to represent **uneven-aged, continuous-cover selection
forestry**.

Neither VDYP nor TIPSY is adequate for that regime. The growth engine for this
instance is **FVS-BC** through the `UBC-FRESH/fresh-fvsbc` Python wrapper. The
wrapper runs individual-tree simulations, applies selection-cut keywords, and
returns the per-tree, cut-list, structural, and summary tables needed to build
a state-transition library for ws4.

## Status

Phase 0 (bootstrap and growth-engine contract) is complete. Phase 1 (data
acquisition and stem lists) is active under issue #7. The legal boundary and the
public inventory layers are acquired: SUP S15382 (3,533.1341 ha), VRI 2025,
BEC, historical fire perimeters, harvest history, and mule-deer habitat classes.
The Klinka et al. 2004 site-unit report is acquired and the IDFxm/IDFdk3
site-series classification and site-index tables are extracted. The AFRF
Management and Working Plan #3 is acquired; its Knife Creek MDWR contract is in
`config/mdwr_regimes.yaml`, and Figure 11 was recovered into
`data/benchmarks/`. The georeferenced site-series map, the legal UWR order and
the 2003 transition strategy are blocked under P1.2a (#15). A stem-list basis is
still required. The repository does **not** yet carry a calibrated FVS-BC
library or a runnable ws4 dataset. See `ROADMAP.md` and `CHANGE_LOG.md`.

## The modelling chain

```text
AFRF boundary + VRI / CFI plots
        |
        v
FEMIC data prep (boundary, BEC, strata, site index, disturbance)
        |
        v
nemora stem populations  ->  fresh-fvsbc (FVS-BC)
        |                         |
        |                         +-- selection-cut keywords
        |                         +-- per-tree and cut-list tables
        v                         v
state-transition library  ->  ws4 tracks / treatments / curves
        |
        v
ws4 estate optimization with mule-deer and cutting-cycle constraints
```

The state-transition library is the bridge. Each state is a stand condition at
a selection entry. A selection regime moves the block to a post-cut state. The
growth curve between entries comes from FVS-BC. ws4 schedules entries by block
and optimizes the estate-level objective.

## Why FVS-BC

- It is an individual-tree, distance-independent growth model. It can represent
  a residual stand after a selection cut, not just an age-class average.
- `fresh-fvsbc` exposes FVS-BC's selection and thinning keywords, including
  `THINQFA` (BDq), `THINBBA`, `THINABA` and `THINDBH`, plus
  `FVS_TreeList_Metric`, `FVS_CutList_Metric`, `FVS_ATRTList_Metric`,
  `FVS_Summary_Metric`, and `FVS_StrClass_Metric`.
- The Knife Creek regimes use `THINQFA` with the Table 29 residual B/D/q
  values. `THINBTA` is not a basal-area target; it is a thin-from-below to a
  trees-per-acre target.
- The per-tree and cut-list outputs give the removed stems, the residual stems,
  and the post-cut state needed for the next entry.
- VDYP and TIPSY produce stand-level averages that cannot carry a residual
  diameter distribution through repeated selection entries.

`fresh-fvsbc` is pinned in `config/toolchain.yaml`. The current reference is
commit `ca33d0e26a079a72add5108f1b182b798b0c4e3e` (package version 0.11.0).
FVS itself is a USDA Forest Service model in the U.S. public domain; the
wrapper is MIT. See the wrapper's own documentation for the build recipe and
its known limits.

## What this repository contains

- `config/` — the instance identity, the toolchain pin, data requirements, the
  MWP #3 management contract, and the reviewed selection regimes.
- `data/benchmarks/` — reviewed public figure and table recoveries, including
  the MWP #3 Figure 11 target structure and the Appendix 9 compartment table.
- `data/site_index/` — the Klinka 2004 site-index tables by site series and
  species.
- `docs/` — the instance contract, data acquisition, growth-engine design,
  state-transition design, and publication boundary.
- `notes/` — ADRs for the two-block architecture, the uneven-aged growth
  engine, the publication boundary, and the merged model.
- `planning/` — the bootstrap plan and the FVS-BC state-transition design.
- `ws4/` — the state-transition contract and target/account templates.
- `runbooks/` — the acquisition, FVS-BC pilot, and ws4 assembly procedures.

There is no `data/legacy_*` package here. Knife Creek is bootstrapped from
source data, not from a legacy Patchworks matrix.

## Quick start

The repository does not yet have a runnable model. The first executable
milestone is a single FVS-BC selection-cut pilot once the boundary, inventory,
and stem-list inputs exist. The intended shape is:

```bash
python -m fresh_fvsbc data/fvsbc/populations/AU01.json \
  --directory runtime/fvsbc/AU01_sel_mdwr_high \
  --species FD --tree-age 60 \
  --keyword SITECODE=FD,100 \
  --keyword NUMCYCLE=4 \
  --keyword THINQFA=1,0.0,23.62,0,1.25,1.97,126.32 \
  --keyword PROCESS \
  --block "DATABASE|DSNOut|FVSOut.db|TreeLIDB|CutLIDB|ATRTLIDB|Summary|StrClass" \
  --keyword STOP
```

The exact keyword order and entry-year semantics are not yet validated. The
`THINQFA` supplemental residual-density-units record is not yet supported by
`fresh-fvsbc` 0.11.0, so this example is a target, not a runnable command. See
`config/fvsbc/regimes.yaml`, `runbooks/FVSBC_PILOT.md` and
`planning/fvsbc-state-transition-design.md`.

## Data status

No field data or stem list is committed yet. Acquired inputs and remaining gaps
are listed in `config/data_requirements.yaml` and
`docs/guides/data-acquisition.rst`:

- the Knife Creek legal boundary and block identifier — acquired;
- VRI or AFRF forest-cover inventory — acquired;
- BEC and site-series classification — BEC and classification acquired; the
  georeferenced site-series map is blocked;
- site index and species composition — VRI and Klinka 2004 tables acquired;
- disturbance history, including the 2013 wildfire — acquired;
- public mule-deer habitat classes and MWP #3 management direction — acquired;
  the legal UWR order is blocked; and
- tree-level tallies or a reviewed synthetic stem-population basis — still
  required.

## Related repositories

- `UBC-FRESH/femic` — the FEMIC package and parent checkout.
- `UBC-FRESH/fresh-fvsbc` — the FVS-BC wrapper used as the growth engine.
- `UBC-FRESH/nemora` — synthetic stem-population generation from inventory
  tallies.
- `UBC-FRESH/femic-afrf-gavinlake-instance` — the sibling Gavin Lake instance.
- `UBC-FRESH/ws4` — the estate model runtime.
- `UBC-FRESH/ubc-fresh-dev-workflow` — the planning and workflow seed.

The future merged AFRF model is reserved as `UBC-FRESH/femic-afrf-instance`.
It is not created yet. The merge contract is recorded in
`notes/adr/0004-merged-afrf-model.md`.

## License

MIT for the repository's original code and documentation. Source data and
third-party model components retain their own terms. See
`docs/reference/data-publication-boundary.rst`.
