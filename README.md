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
`data/benchmarks/`. The 2007 GWM order and the 2003 Knife Creek transition plan
are acquired; GWM 2007 is the default basis and Table 29 is a named AFRF
alternative. The georeferenced site-series map and the legal UWR/HMZ spatial
layer are still blocked under P1.2a (#15). A public
PSP-derived IDF Cariboo stem-list analog is committed under `data/psp/` for the
interim FVS-BC pilot; the KC CFI is still preferred. The repository now carries a compiled structural ws4 dataset at
`ws4/dataset_kc_v1`, built from the KC ForestModelXML recipe at
`data/kc_ws4_recipe/forestmodel.xml`, plus a no-cut baseline, a selection-smoke
run, reports and a web service. It is still **not calibrated** and is not a
legal-compliance model. See
`ROADMAP.md` and `CHANGE_LOG.md`. The persistent session record is
`notes/reports/2026-10-27-public-data-and-fvsbc-handoff.md`.

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
- The default Knife Creek regimes are GWM 2007: `THINABA` above 37.5 cm to the
  legal large-tree minimum, then `THINQFA` on 0–37.5 cm to the remaining B.
  Table 29 is a named AFRF alternative. `THINBTA` is not a basal-area target;
  it is a thin-from-below to a trees-per-acre target.
- The per-tree and cut-list outputs give the removed stems, the residual stems,
  and the post-cut state needed for the next entry.
- VDYP and TIPSY produce stand-level averages that cannot carry a residual
  diameter distribution through repeated selection entries.

`fresh-fvsbc` is pinned in `config/toolchain.yaml`. The current reference is
commit `d86e78b0fc31386684aae1a0a1a9a821c0ee2baf` (package version 0.12.0, post-v0.12.0 main).
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

The repository has a runnable structural ws4 model:

```bash
python runbooks/run_kc_ws4_pipeline.py \
  --xml data/kc_ws4_recipe/forestmodel.xml \
  --fragments data/kc_ws4_recipe/fragments.csv \
  --spatial-fragments data/patchworks_knifecreek/fragments.csv \
  --fragment-shapefile data/patchworks_knifecreek/spatial/fragments.shp \
  --dataset ws4/dataset_kc_v1 \
  --runtime ws4/runtime/kc_v1 \
  --evidence ws4/evidence/kc_v1
```

The FVS-BC selection-cut pilot shape remains:

```bash
python -m fresh_fvsbc data/fvsbc/populations/AU01.json \
  --directory runtime/fvsbc/AU01_sel_mdwr_high \
  --species FD --tree-age 60 \
  --keyword SITECODE=FD,100 \
  --keyword TIMEINT=,30 \
  --keyword NUMCYCLE=2 \
  --keyword THINABA=2,16.0,1.0,37.5,999.0,0.0,999.0 \
  --keyword THINQFA=2,0.0,37.5,0,1.25,5.0,56.63 \
  --keyword PROCESS \
  --block "DATABASE|DSNOut|FVSOut.db|TreeLIDB|CutLIDB|ATRTLIDB|Summary|StrClass" \
  --keyword STOP
```

The BC variant reads `THINQFA` fields 2, 3 and 6 in **centimetres** and
converts them to inches; the target density is square feet per acre. The
supplemental record is supported at the pinned commit `d86e78b`. The cycle-2 /
30-year entry is the synthetic pilot's reviewed setting; this example is still
a target, not a validated command. See
`config/fvsbc/regimes.yaml`, `runbooks/FVSBC_PILOT.md` and
`planning/fvsbc-state-transition-design.md`.

## Data status

No Knife Creek field data or stem list is committed yet. A public IDF Cariboo PSP-derived stem-list analog is committed under `data/psp/` for the interim FVS-BC structural pilot. Acquired inputs and remaining gaps
are listed in `config/data_requirements.yaml` and
`docs/guides/data-acquisition.rst`:

- the Knife Creek legal boundary and block identifier — acquired;
- VRI or AFRF forest-cover inventory — acquired;
- BEC and site-series classification — BEC and classification acquired; the
  georeferenced site-series map is blocked;
- site index and species composition — VRI and Klinka 2004 tables acquired;
- disturbance history, including the 2013 wildfire — acquired;
- public mule-deer habitat classes, MWP #3 management direction, the 2007 GWM
  order and the 2003 transition plan — acquired; the legal UWR/HMZ spatial
  layer is still blocked; and
- tree-level tallies or a reviewed synthetic stem-population basis — a public
  IDF Cariboo PSP analog is available; the KC CFI is still preferred.

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
