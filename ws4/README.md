# Knife Creek ws4 instance

The ws4 dataset for Knife Creek is a **state-transition matrix**:

- a track is a stand state at a selection entry;
- a treatment is a selection regime that moves the block to a residual state;
- the entry clock is years since the last selection entry;
- the growth curve is the interval growth from FVS-BC;
- features carry the habitat indicators; and
- products carry the cut yield.

There is no clearcut treatment in the default model.

## Status

The provisional structural library is in `state_library_v0/`: 8 initial
states, 6 residual states, 48 selection transitions and 192 interval curves,
built from the PSP-derived IDF Cariboo analog. It is a **legacy Table 29**
library, not the default GWM 2007 basis. It is **not** a compiled ws4 dataset
and the residual graph is not closed. See `state_library_v0/README.md`. The
next library is `state_library_v1` with `basis=GWM_2007`.

A veteran/large-tree retention policy pilot is in `policy_pilot_v0/`: four
policies on two PSP-derived conditional stands, showing the trade-off between
large-tree BA, total Table 29 BA and clump-cover proxies. `build_clump_scenarios.py`
adds 276 geometric clump scenarios; these are scenario axes, not empirical
clump statistics. The legal GWM 10 clump is **4–10 or more mature trees with
interlocking crowns**, not 2–5; the 2–5 figure is the maximum-diameter subgroup.
It is not approved policy. Policy definitions are in
`../config/retention_policies.yaml`. The public PSP stem maps are too sparse for
empirical clump geometry; see `../notes/reference/psp-stem-map-limits.md`.
The legal order and the AFRF Table 29 differ on D and large-tree BA. GWM 2007 is
the default basis and Table 29 is a named alternative; see
`../notes/reference/mdwr-canopy-clump-requirements.md`,
`../docs/reference/mdwr-legal-basis.rst` and
`../docs/guides/mdwr-habitat-constraints.rst`.

A **GWM 2007 legal-basis pilot** is in `gwm_pilot_v0/`: five PSP-derived stands ×
three GWM classes × two methods. It passes 17/30 stand-structure checks. The
selected rule is a post-FVS **clump reserve**: retain above D, then reserve the
largest 2–5 trees above D per 4–10-tree clump and harvest the rest. With the
DBH-ranked six-tree proxy, that passes 13/15 cases and harvests 1.07/2.64/5.12
m²/ha of large BA on average. It is a marking scenario, not a new FVS growth
run and not a compliance result. See `gwm_pilot_v0/README.md`.

A synthetic ws4 validation dataset is in `dataset_v1_synthetic/`: 4 synthetic
1 ha blocks, 23 tracks, 25 treatments and 575 curves from the canonical GWM
2007 graph. `ws4 validate` passes.

A partial 30-year structural generator is in `kc_psp_generator/`; it produces
BA/TPH/QMD/large-BA curves only and keeps ingrowth as an explicit block-specific
scenario.

A state reconstruction of the 96 observed transitions is in
`kc_psp_simulation/`; it is conditional on observed ingrowth and is not an
ingrowth forecast. Simulated end states match the observed canonical
BA/QMD/large-tree state on 75/96 transitions (78.1%).

Tree-level empirical models are in `kc_psp_tree_models/`: DBH increment and
survival transfer reasonably in leave-one-block-out tests; Poisson ingrowth
does not. They are diagnostics, not yet a stand model.

The spatial structural dataset is in `dataset_kc_spatial_v3/`: 160 clipped VRI
blocks (3,481.77 ha), 92 HMZ-specific tracks, 49 treatments. HMZ M/L/U track
offers are enforced. Block groups carry observed LidarBC clump classes and a
spatial reserve class; `block_features.csv` and
`data/lidar/kc_2024/reserve_trees.parquet` carry the per-block/per-tree reserve
scenario. `ws4 validate` passes. It is closer to a KC dataset but still uses
PSP-derived tree lists, not KC CFI. See `dataset_kc_spatial_v3/README.md`.

The contract is in `state_transition_contract.md`; the target and
patch-account files remain templates.

## Planned files

| File | Purpose |
| --- | --- |
| `state_transition_contract.md` | The table and identifier contract |
| `state_library_v0/` | Legacy Table 29 transition library |
| `state_library_v1/` | Provisional GWM 2007 clump-reserve transition library |
| `policy_pilot_v0/` | Legacy Table 29 veteran-retention policy pilot |
| `gwm_pilot_v0/` | GWM 2007 legal-basis stand-structure pilot |
| `dataset_v1_synthetic/` | Synthetic ws4 validation dataset |
| `dataset_kc_spatial_v1/` | Spatial VRI/HMZ structural dataset |
| `dataset_kc_spatial_v2/` | v1 plus observed LiDAR clump classes |
| `dataset_kc_spatial_v3/` | v2 plus spatial reserve classes and tree assignments |
| `targets.template.yaml` | Harvest and habitat target template |
| `patch_accounts.template.yaml` | Selection-opening patch account template |
| `topology.csv` | Block topology, once the boundary exists |
| `schedules/` | Baseline and scenario schedules |
| `evidence/` | Small JSON evidence summaries |

## Relationship to Gavin Lake

Gavin Lake uses an age-class legacy matrix. Knife Creek uses a state-transition
matrix. Both compile to the same ws4 schema. The merged model is a later
project; see `notes/adr/0004-merged-afrf-model.md`.
