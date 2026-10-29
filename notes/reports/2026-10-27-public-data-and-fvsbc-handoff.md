# Public-data and FVS-BC handoff — 2026-10-27

## Why this file exists

Chat history is not the record. This file and the git history are. A future
reader should be able to resume the AFRF work from this note, the linked
reference notes, the configuration, and the pull requests without reading a
chat transcript.

## Scope and standing requirements

- Two distinct ws4 instances: Gavin Lake and Knife Creek. A third merged AFRF
  model is reserved for later.
- Gavin Lake uses the legacy Patchworks H matrix. Do not replace it with
  FVS-BC; the legacy matrix remains the Gavin scenario source.
- Knife Creek uses FVS-BC because it is an uneven-aged, continuous-cover
  selection forest. VDYP and TIPSY are not the primary KC engine.
- KC has a strict mule-deer wintering-habitat constraint. No clearcuts or
  even-aged silviculture. The 2007 GWM order and 2003 transition plan are
  acquired; do not claim legal compliance without the spatial UWR/HMZ layer
  and the current approved order.
- Do not infer scenario-parameter intent. The user is the domain expert; ask
  about modelling intent. A deliberately unattainable minimum with a linear
  penalty, paired with even-flow, is a legitimate pull-up technique.
- Public data first; the AFRF private dump from Ionut Aron is still the
  preferred source for KC CFI/tree lists, site-series GIS and the legal UWR
  material.
- Do not present a schematic map as a georeferenced layer, and do not present
  Monte Carlo replication as new independent information.

## What is acquired and where it lives

### Knife Creek

| Input | Path | Status |
| --- | --- | --- |
| Legal SUP boundary S15382, 3,533.1341 ha | `data/boundaries/knife_creek_sup_S15382.gpkg` | acquired |
| VRI 2025, 183 polygons, 174 with site index | `data/inventory/vri_2025_kc.gpkg` | acquired |
| BEC: IDFdk3 3,051.80 ha, IDFxm 481.33 ha | `data/inventory/bec_kc.gpkg` | acquired |
| Fire perimeters and derived harvest history | `data/inventory/` | acquired |
| Public mule-deer habitat classes | `data/habitat/mule_deer_stand_structure_kc.gpkg` | acquired; not the legal order |
| Klinka 2004 site-unit report and site index | `reference/`, `data/site_index/` | acquired |
| MWP #3 PDF and KC MDWR contract | `reference/AFRF-management-working-plan-3-2007.pdf`, `config/mdwr_regimes.yaml` | acquired |
| Figure 11 target structure recovery | `data/benchmarks/mwp3_figure11_target_stand_structure.csv` | reviewed |
| MWP #3 Appendix 9 compartment table | `data/benchmarks/mwp3_kc_compartments.csv` | transcribed |
| FAIB PSP-derived IDF Cariboo stem lists | `data/psp/` | acquired synthetic analog |
| KC CFI or released tree list | — | still required |
| Georeferenced site-series map | — | blocked |
| 2007 GWM order + 2003 transition strategy | `/srv/shared-data/gep/ws4/sources/afrf-mule-deer/` | acquired; spatial UWR/HMZ layer still required |
| GWM 2007 legal targets and clump rules | `data/benchmarks/mdwr_gwm2007_*.csv` | extracted |

### Gavin Lake

| Input | Path | Status |
| --- | --- | --- |
| Legacy H matrix and evidence | `data/legacy_gavinlake/`, `ws4/evidence/` | complete |
| Klinka site index (SBSdw1/ICHmk3) | `data/site_index/` | acquired |
| MWP #3 GL AAC benchmark | `data/benchmarks/mwp3_gavin_aac.csv` | acquired |
| LTSY target | `ws4/targets_gavin_ltsy.yaml` | runnable |

## Key numbers and decisions

### Gavin Lake

- Legacy initial growing stock: `1,418,962.31 m³`; parity difference `-7.2e-7`.
- Baseline: clearcut at 80, re-enter every 80; mean `188,677.89 m³/period`.
- LTSY: CMAI `3.599653 m³/ha/yr` at age 100 on `4,662.96 ha`;
  `16,785.06 m³/yr`; `167,850.57 m³/period`; ×1.1 rounded `185,000`.
- Baseline meets `185,000` in 22 of 30 periods. The `1,277,067 m³` growing-stock
  target is the binding constraint.
- GL demonstration AAC from MWP #3: 2.4 ha/yr clearcut, 3.0 partial, 2.4
  salvage, 7.8 total on 478 ha net with a 100-year cycle. This is not the
  legacy 4,662.96 ha / 80-year rotation.

### Knife Creek management contract

ADR 0005 makes **GWM 2007 the default** and keeps **AFRF_MWP3_TABLE29** as a
named alternative. Surplus large trees above the legal minimum are harvestable.

Legal GWM 2007 targets (IDFdk3/IDFdw):

| Habitat | B | BA >37.5 | D | q | Reserve above D |
| --- | ---: | ---: | ---: | ---: | ---: |
| High | ≥29 m²/ha | ≥16 m²/ha | ≥70 cm | 1.20–1.35 | 0–2.9 m²/ha |
| Moderate | ≥22 | ≥11 | ≥60 | 1.25–1.35 | 0–2.2 |
| Low | ≥16 | ≥6 | ≥50 | 1.25–1.40 | 0–1.6 |

- GWM 10 clumps: 4–10 or more mature trees with interlocking crowns; the
  maximum-diameter subgroup is 2–5 trees.
- Canopy openings 0.3–1.0 tree heights, mean 0.5; cutting cycle ≥30 years.
- Before 2026, retain ≥80% of pre-harvest merchantable Douglas-fir BA.
- Knife Creek HMZ 1–5: M, L, M, M, A.
- Typical thinning yield ~50 m³/ha; AAC 82.0 ha/yr selection + 11.2 ha/yr
  salvage.

AFRF Table 29 alternative:

| Habitat | Residual B | Max DBH | q | Cycle |
| --- | ---: | ---: | ---: | ---: |
| High | 29 m²/ha | 60 cm | 1.25 | 30 |
| Moderate | 22 m²/ha | 55 cm | 1.25 | 30 |
| Low | 16 m²/ha | 50 cm | 1.30 | 30 |

Table 29 matches the legal total B but uses lower D (60/55/50 vs 70/60/50) and
omits the legal BA >37.5 targets and reserve. It is an AFRF interpretation, not
legal compliance. Areas differ by source: Table 32 net 3,117 ha; Appendix 9 net
3,162.3 ha; SUP 3,533.1341 ha. Record, do not reconcile silently.

### Figure 11

- Recovered with `figrecover 0.1.0a1`
  (<https://github.com/ubc-fresh/figrecover>) from MWP #3 page 97.
- BA sums: Low `17.02`, Moderate `22.96`, High `30.17` m²/ha versus Table 29
  `16/22/29`. The difference is recorded, not forced.
- Recovered density implies q `1.306/1.254/1.253` versus `1.30/1.25/1.25`.
- Table 29 is the AFRF shape comparison; the GWM tables are the legal default.
  Figure 11 is the relative shape.
- Klinka 2004's figures are photographs and diagrams, not quantitative charts;
  the site-index tables were transcribed directly.

### FVS-BC keyword findings

- `THINQFA` is the correct BDq keyword. `THINBTA` is a trees-per-acre target,
  not a basal-area target.
- The BC variant converts `THINQFA` fields 2, 3 and 6 (minimum DBH, maximum
  DBH, class width) from **cm to inches** in `canada/bc/initre.f`. GWM 2007
  uses `THINABA` above 37.5 cm to the large-tree minimum, then `THINQFA` on
  0–37.5 cm. Table 29 uses full-range `THINQFA` with D 60/55/50. Both store
  those fields in cm; the residual target is ft²/ac.
- The supplemental record is `0` BA/ac, `1` TPA, `2` SDI; it has no `END`.
- Entry cycle: cycle 1 = year 0; cycle 2 with `TIMEINT=,30` = year 30; cycle 4
  with 10-year periods also = year 30.
- `fresh-fvsbc` P42.1 added `Keyword.supplemental`; KC pins it at
  `d86e78b0fc31386684aae1a0a1a9a821c0ee2baf` (0.12.0, post-v0.12.0 main).
- Pilot residuals were above the Table 29 target because grown stands have q
  deficits. Example: 28.8 → 45 at year 30, post-cut 31; 38.5 → 53, post-cut 34.
  Record, do not call this calibrated.

### Public PSP analog

- Source: FAIB Forest Inventory Ground Plot Data, OGL-BC, PSP FTP.
- 338 first-measurement IDF PSPs in Williams Lake + 100 Mile House TSAs.
- Selected 51 Douglas-fir-leading, mature IDF plots (age 80–180, BA 20–40,
  QMD 15–25); 4,553 live trees ≥9.1 cm; 45 stable Weibull fits.
- Pooled shifted Weibull: `a=1.0200`, `beta=7.8411`, lower bound 9.1 cm,
  KS=0.0109.
- 24 synthetic one-hectare stem lists, 22,178 trees; `data/psp/`.
- Regression: `log(beta) = -3.863 + 2.049 log(QMD)`, R² 0.471, adj. 0.459,
  LOOCV 0.306. TPA is not significant after QMD (`t=0.86`, VIF 2.71). Shape
  `a` is not predictable; pooled `a` used.
- GG tested per plot: 5/45 lower AICc but all degenerate; no stable GG beat
  Weibull.
- Conditional lists: QMD 18–26 / TPA 550–900 / BA 22.9–29.4 m²/ha.
- FVS-BC conditional pilot: QMD 22/750 → 41 pre, 35 post; QMD 24/650 → 41 pre,
  38 post. Target 29, so the q deficit persists.
- **Finite information:** 45 plots / 4,553 trees. `--stands N` can generate more
  stands, but that is Monte Carlo replication, not new independent plots.

### State-transition library v0

`ws4/state_library_v0/` is a **legacy Table 29** transition library from eight
PSP-derived stands × three Table 29 regimes × two 30-year entries. It is not
the default GWM 2007 basis:

- 8 initial states, 6 residual states, 48 transitions, 192 curves;
- mean residual BA: High 33.31, Moderate 29.19, Low 25.94 m²/ha against
  29/22/16;
- mean residual q: 1.284/1.255/1.296 against 1.25/1.25/1.30;
- mean residual maximum DBH about 73.6 cm against 60/55/50;
- the graph is not closed and the residual states are terminal;
- it is not a compiled ws4 dataset and not KC-calibrated;
- a legal-basis rebuild should be `state_library_v1` with `basis=GWM_2007`.

The residual BA and maximum DBH exceed the targets because the source stands
contain trees above the Table 29 maximum DBH and because q deficits limit the
removal. Record the gap; do not claim the target is met.

The veteran-retention policy pilot is `ws4/policy_pilot_v0/`. It compares
`RETAIN_ABOVE_D` with split policies that retain 4, 6 or 8 m²/ha at 50 cm+ and
then thin the 0–50 cm component to the remaining Table 29 B. The split policies
hit the total BA target (High 27–28 vs 29; Moderate/Low exact) while holding
large-tree BA at 4/6/8. `RETAIN_ABOVE_D` leaves 31–37.5 m²/ha and 14.5–15.6
m²/ha of large trees in the cases with an after-treatment tree list. Clump
count and crown-cover proxies scale with the large-tree target.

`ws4/policy_pilot_v0/clump_scenarios.csv` adds 276 geometric clump scenarios:
the retained large-tree TPH is placed in **4, 6, 8 or 10** tree clumps at 3, 5
or 7 m radius. GWM 10 requires 4–10 or more mature trees with interlocking
crowns. With 4–10-tree clumps, within-clump closure is high (0.86–0.98 at 3 m)
while total stand cover is lower. These are scenario axes, not approved MDWR
policy, and not a snow-interception model.

The first GWM 2007 pilot is `ws4/gwm_pilot_v0/`: five conditional stands ×
three classes × two methods. It passes 17/30 stand-structure checks. Retain
above D passes 13/15; the D-protected split passes 4/15. The split preserves D
but leaves the >D reserve, so q is too high in most High/Moderate cases. A
full-range split meets q but strips the largest trees and leaves max DBH below
D. The selected rule is a post-FVS clump reserve: retain above D, then reserve the
largest 2–5 trees above D per 4–10-tree clump and harvest the rest. With a
DBH-ranked six-tree proxy, this passes 13/15 cases and harvests 1.07/2.64/5.12
m²/ha of large BA on average. It is a marking scenario, not a new FVS growth
run. See `ws4/gwm_pilot_v0/README.md` and `clump_reserve_summary.csv`.

The public PSP stem maps are too sparse for empirical clump geometry: of the 45
stable plots, 11 are fully mapped, 3 have any mapped tree ≥50 cm, and only one
has more than one (four trees). See `notes/reference/psp-stem-map-limits.md`.
Use KC CFI/tree lists or the approved UWR material when available.

The 2007 shallow/moderate GWM order and the 2003 Knife Creek transition plan
were located after the first clump pilot. ADR 0005 makes **GWM 2007 the
default** and keeps **AFRF_MWP3_TABLE29** as a named alternative. Surplus large
trees above the legal minimum are harvestable (default split cut). GWM 10
requires clumps of 4–10 or more mature trees with interlocking crowns, not
2–5; the 2–5 figure in MWP #3 is the maximum-diameter subgroup. The legal
stand-level targets are BA >37.5 cm ≥16/11/6 m²/ha and Table 2 D ≥70/60/50 for
High/Moderate/Low. MWP #3 Table 29 uses lower D (60/55/50) and is an AFRF
interpretation, not the legal curve.
The Knife Creek HMZ matrix is HMZ 1 M, 2 L, 3 M, 4 M, 5 A; the order also has a
north-facing >20% slope, >10 ha exemption in the Moderate Snowpack zone. Do not
claim legal compliance without the UWR spatial layer. See
`notes/reference/mdwr-canopy-clump-requirements.md` and
`notes/reference/mdwr-source-index.md`.

### State-transition library v1

`ws4/state_library_v1/` is the provisional GWM 2007 clump-reserve library:

- 8 initial stands × 3 GWM classes × 2 entries = 48 transitions;
- 72 state IDs, 192 curves; residual states are terminal;
- 33/48 stand-structure checks pass (High 10/16, Moderate 11/16, Low 12/16);
- the clump reserve uses a DBH-ranked six-tree proxy, not spatial clumps;
- residual populations are weighted resamples of the FVS after-treatment list;
- `legal_compliance` is false on every row;
- the state IDs are per stand/regime/entry and are not yet canonical shared
  states. See `ws4/state_library_v1/README.md`.

### Canonical graph and synthetic ws4 dataset

The v1 graph is canonicalized in `ws4/state_library_v1/canonical/`:

- 23 shared BA/QMD/large-tree/reserve states;
- 25 aggregated transitions;
- 500 curve rows;
- 6 terminal states;
- 0 cycles;
- terminal-closed, not cycle-closed.

`ws4/dataset_v1_synthetic/` compiles 4 synthetic 1 ha blocks, 23 tracks,
25 treatments and 575 curves from the canonical graph. `ws4 validate` passes.

`ws4/dataset_kc_spatial_v1/` compiles 160 clipped VRI blocks (3,481.77 ha),
92 HMZ-specific tracks and 49 treatments. HMZ groups: M 113, L 44, U 3. HMZ
track offers enforce M = Low/Moderate, L = Low only, A = all, U = no
treatments. `ws4 validate` passes. Tree lists are still PSP-derived, not KC
CFI; the clump rule is not spatial.

### LidarBC canopy inventory

LidarBC discovery over the SUP found 134 point-cloud tiles, 76 DEM and 72 DSM
tiles. All 72 2024 DEM/DSM pairs were downloaded; 28 tiles intersect the SUP enough to
produce clipped trees. The merged inventory has 278,318 canopy trees over
3,533.13 ha (78.8 TPH; height mean 19.5 m, p95 28.6 m). At 10 m linkage for
trees ≥20 m: 50,401 clumps, 6,046 4–10-tree clumps, 30,214 singletons. Block-
level features are in `data/lidar/kc_2024/block_tree_summary.csv`; all 160
spatial blocks are covered, with mean 18.2 4–10-tree clumps/ha. `ws4/
dataset_kc_spatial_v2` groups blocks by observed clump class (29 `<10`, 54
`10–20`, 68 `20–30`, 9 `30+`). A spatial reserve scenario
(`lidar_reserve_scenario.py`) assigns 88,640 reserve trees and 28,191 harvest
trees across 160 blocks; `ws4/dataset_kc_spatial_v3` carries the reserve
classes. This is a canopy inventory, not a CFI: no species, understory or
measured DBH. See `notes/reference/lidarbc-kc-pilot.md`.

### AFRF Knife Creek PSP dataset

The AFRF KC PSP workbook is the primary field-data candidate: 24 permanent
0.05 ha plots (15.81 × 31.62 m), 1993–2013, stem-map coordinates, species,
DBH/height/crown/vigor. FRDA Report 242 confirms the design, plot/block/
treatment mapping, the `P = I/B` interior/buffer distinction and the vigor/
crown definitions. The raw workbook is private and not committed. Remaining
metadata questions are limited to `TS`, `TC`, `D1/D2/DA/DS/WTA`, `HT13`,
duplicate columns and the exact X/Y conversion. See
`notes/reference/kc-afrf-psp-dataset.md`.

The first FVS backtest is `ws4/kc_psp_validation/`: 1993 interior trees,
20× expansion, no cut. Version v1 corrects cycle-year alignment. 2013 BA 36.42
predicted vs 35.38 observed; QMD 14.61 vs 14.98; TPH 2,713 vs 2,291. Observed
annual mortality rises from 1.0% to 2.4%. `MORTMULT` 1/2/2.5/3/4 gives 2013
TPH +422/+126/-0.5/-115/-336 and BA +1.04/-2.00/-3.25/-4.34/-6.67; no global
multiplier fits both. Age/site index are placeholders; not a calibration claim.

Calibration v1 (`ws4/kc_psp_calibration/`) converged at iteration 28 with FD
BAI 1.6213/mort 1.7593, SE 1.3948/3.8261, PL 1.0/8.0 and HW 1.0/1.2012. 2013
BA 36.38 vs 35.38, QMD 15.76 vs 14.98, TPH 2,313 vs 2,291. FD/SE/HW match; PL
is unmodelled MPB. Status is converged-not-accepted because QMD bias is 0.77
cm against a 0.5 cm criterion.

### Maps

MWP #3 landscape appendices, KC pages: 150 forest cover, 158 seral, 162
compartments, 164 harvest priorities, 166 roads, 168 research. Page 162 has
KC01–KC11, RD05–RD07, habitat classes, deferred areas and the management zone,
but only a north arrow and scale bar — no coordinate grid. It was transcribed as
an area table, not georeferenced. A defensible overlay needs control points from
the SUP, roads/lake shoreline and VRI/cutblock corners, plus residual reporting.
The separate 2014 `KC_General_Map.pdf` is a 1:30,000 general map with roads,
cutblocks, proposed cutblocks, WTPs, pipeline, contours, wetlands, trails and
compartment labels. It is not the site-series map and was not georeferenced;
see `notes/reference/kc-general-map-2014.md`.

## Pull-request and commit index

| Repository | PR / commit | Content |
| --- | --- | --- |
| KC | #17 / `eb3e038` | Klinka 2004 site-unit classification |
| KC | #19 / `b91d140` | MWP #3 + Figure 11 + site index + compartments |
| KC | #20 / `9f2cdfe` | Figure 11 q-factor check |
| KC | #21 / `c9adad6` | MWP #3 map-appendix inventory |
| KC | #23 / `5974dae` | Pin THINQFA-capable `fresh-fvsbc` |
| KC | #24 / `1c5ac00` | Roadmap status correction |
| KC | #26 / `6d3e813` | BC THINQFA units + synthetic pilot |
| KC | #27 / `78d71cb` | PSP-derived IDF Cariboo stem lists |
| KC | #28 / `2b7c005` | Pin `nemora` |
| KC | #29 / `c39e8b3` | Weibull QMD/TPA regression + conditional lists |
| KC | #30 / `1057094` | Persistent public-data/FVS-BC handoff |
| KC | #31 / `1da9050` | 2014 general-map note |
| KC | #32 / `97b62e3` | State-transition library v0 |
| KC | #33 / `c1e4c3c` | Veteran-retention policy pilot |
| KC | #34 / `bf62b8f` | Clump geometry + PSP stem-map limits |
| KC | #35 / `62c460b` | MDWR legal basis correction |
| Gavin | #23 / `d04c8bb` | Klinka site index + GL AAC |
| FEMIC | #420, #423–#425 | Register/bump AFRF submodules |
| FEMIC | #428, #429, #430 | Benchmark, map note, THINQFA pin |
| FEMIC | #432, #433, #434, #435 | Unit correction, PSP lists, nemora pin, regression |
| FEMIC | #438, #439, #440, #442 | State v0, policy pilot, clump geometry, legal basis |
| `fresh-fvsbc` | #190 / `d86e78b` | P42.1 THINQFA supplemental record |

`nemora` used for the PSP fits: commit
`2e8776c0ffce15cb4b18e2fbd70bdd4c1c4467d9` (`0.0.1-alpha`).

## Open blockers and gaps

1. KC CFI or a released tree list. The PSP analog is regional, not KC.
2. Georeferenced AFRF site-series map. The Klinka maps are in pockets/CD-ROM.
3. Legal UWR boundary/current order verification. The HMZ spatial layer is
   acquired at `data/habitat/mule_deer_hmz_kc.gpkg` and crosswalked to VRI; the
   legal boundary and stand-structure map still need verification.
4. FVS-BC calibration for KC. No calibrated KC case exists.
5. `fresh-fvsbc` upstream documentation still describes `THINQFA` generically;
   the BC cm conversion is recorded here and in PR #190's comment, but a
   package doc/test follow-up remains.
6. `fresh-fvsbc` P42 roadmap closeout is still marked active, although the code
   is merged.
7. FEMIC has unrelated uncommitted lidar/tfl6 work in the local checkout; do
   not fold it into AFRF changes.

## What to request from Ionut / AFRF

- CFI/PSP tree tallies for KC and Gavin: plot coordinates, design, species,
  DBH, height, crown, age, site index, damage, measurement dates.
- Georeferenced site-series/ecosystem polygons.
- Legal UWR/HMZ spatial layer and current approved order at the time of a
  compliance claim.
- Appendix 9 compartment/harvest-unit/reserve/OGMA polygons.
- Cutblock/opening polygons with harvest type/date, roads, fire severity and
  salvage.
- Current mule-deer habitat/suitability layers and legal attributes.
- Any FVS-BC/VDYP/TIPSY calibration, volume/decay equations or yield curves.
- Publication permissions: public, derived, or private-only.

## Next moves

1. Run a GWM 2007 legal-basis pilot on the conditional PSP stands and check
   whether High BA >37.5 ≥16 is reachable.
2. Rebuild the state-transition library as `state_library_v1` with
   `basis=GWM_2007`; keep v0 as the Table 29 legacy comparison.
3. Add the HMZ spatial constraint and the 4–10-tree clump/canopy-opening
   post-processing to the ws4 compile.
4. Ingest the Ionut dump when it arrives and replace the regional PSP analog
   with KC CFI where possible.
5. Add a `fresh-fvsbc` package note/test for the BC THINQFA cm fields.
6. Do not claim legal UWR compliance, calibration, or infinite information.

## Reproduction

- `runbooks/recover_mwp3_figure11.py`
- `runbooks/build_psp_stemlists.py`
- `runbooks/fit_psp_weibull_regression.py`
- `python scripts/dashboard.py`

## Related notes

- `notes/reference/mwp3-kc-management-direction.md`
- `notes/reference/mwp3-figure11-recovery.md`
- `notes/reference/fvsbc-thinqfa-pin.md`
- `notes/reference/fvsbc-thinqfa-pilot.md`
- `notes/reference/psp-idf-cariboo-stemlists.md`
- `notes/reference/site-series-klinka-2004.md`
- `notes/reference/kc-general-map-2014.md`
- `notes/reference/gavin-baseline-findings.md` (Gavin repo)
