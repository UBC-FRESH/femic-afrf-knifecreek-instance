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
  even-aged silviculture. Do not claim legal compliance without the approved
  UWR order and the 2003 transition strategy.
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
| Approved UWR order + 2003 transition strategy | — | blocked |

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

MWP #3 Table 29:

| Habitat | Residual B | Max DBH | q | Cycle |
| --- | ---: | ---: | ---: | ---: |
| High | 29 m²/ha | 60 cm | 1.25 | 30 |
| Moderate | 22 m²/ha | 55 cm | 1.25 | 30 |
| Low | 16 m²/ha | 50 cm | 1.30 | 30 |

- Single-tree selection, small groups of 2–5 trees at maximum D.
- Concentrate removals below 37.5 cm DBH; typical thinning yield ~50 m³/ha.
- AAC: 82.0 ha/yr selection + 11.2 ha/yr salvage.
- Plan outcome: 0% conventional, 95% modified, 5% no harvest.
- Areas differ by source: Table 32 net 3,117 ha; Appendix 9 net 3,162.3 ha;
  SUP 3,533.1341 ha. Record, do not reconcile silently.

### Figure 11

- Recovered with `figrecover 0.1.0a1`
  (<https://github.com/ubc-fresh/figrecover>) from MWP #3 page 97.
- BA sums: Low `17.02`, Moderate `22.96`, High `30.17` m²/ha versus Table 29
  `16/22/29`. The difference is recorded, not forced.
- Recovered density implies q `1.306/1.254/1.253` versus `1.30/1.25/1.25`.
- Table 29 is the policy target; Figure 11 is the relative shape.
- Klinka 2004's figures are photographs and diagrams, not quantitative charts;
  the site-index tables were transcribed directly.

### FVS-BC keyword findings

- `THINQFA` is the correct BDq keyword. `THINBTA` is a trees-per-acre target,
  not a basal-area target.
- The BC variant converts `THINQFA` fields 2, 3 and 6 (minimum DBH, maximum
  DBH, class width) from **cm to inches** in `canada/bc/initre.f`. The KC
  templates use cm (`0.0`, `60/55/50`, `5.0`). The residual target is ft²/ac
  (`126.32/95.83/69.70`).
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

`ws4/state_library_v0/` is a provisional transition library from eight
PSP-derived stands × three Table 29 regimes × two 30-year entries:

- 8 initial states, 6 residual states, 48 transitions, 192 curves;
- mean residual BA: High 33.31, Moderate 29.19, Low 25.94 m²/ha against
  29/22/16;
- mean residual q: 1.284/1.255/1.296 against 1.25/1.25/1.30;
- mean residual maximum DBH about 73.6 cm against 60/55/50;
- the graph is not closed and the residual states are terminal;
- it is not a compiled ws4 dataset and not KC-calibrated.

The residual BA and maximum DBH exceed the targets because the source stands
contain trees above the Table 29 maximum DBH and because q deficits limit the
removal. Record the gap; do not claim the target is met.

The veteran-retention policy pilot is `ws4/policy_pilot_v0/`. It compares
`RETAIN_ABOVE_D` with split policies that retain 4, 6 or 8 m²/ha at 50 cm+ and
then thin the 0–50 cm component to the remaining Table 29 B. The split policies
hit the total BA target (High 27–28 vs 29; Moderate/Low exact) while holding
large-tree BA at 4/6/8. `RETAIN_ABOVE_D` leaves 31–37.5 m²/ha and 7.3–15.6
m²/ha of large trees. Clump count and crown-cover proxies scale with the
large-tree target. These are scenario axes, not approved MDWR policy, and FVS
does not model spatial clumps or snow interception.

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
| Gavin | #23 / `d04c8bb` | Klinka site index + GL AAC |
| FEMIC | #420, #423–#425 | Register/bump AFRF submodules |
| FEMIC | #428, #429, #430 | Benchmark, map note, THINQFA pin |
| FEMIC | #432, #433, #434, #435 | Unit correction, PSP lists, nemora pin, regression |
| `fresh-fvsbc` | #190 / `d86e78b` | P42.1 THINQFA supplemental record |

`nemora` used for the PSP fits: commit
`2e8776c0ffce15cb4b18e2fbd70bdd4c1c4467d9` (`0.0.1-alpha`).

## Open blockers and gaps

1. KC CFI or a released tree list. The PSP analog is regional, not KC.
2. Georeferenced AFRF site-series map. The Klinka maps are in pockets/CD-ROM.
3. Approved UWR boundary and legal mule-deer objectives.
4. The 2003 CCLUP Knife Creek transition strategy.
5. FVS-BC calibration for KC. No calibrated KC case exists.
6. `fresh-fvsbc` upstream documentation still describes `THINQFA` generically;
   the BC cm conversion is recorded here and in PR #190's comment, but a
   package doc/test follow-up remains.
7. `fresh-fvsbc` P42 roadmap closeout is still marked active, although the code
   is merged.
8. FEMIC has unrelated uncommitted lidar/tfl6 work in the local checkout; do
   not fold it into AFRF changes.

## What to request from Ionut / AFRF

- CFI/PSP tree tallies for KC and Gavin: plot coordinates, design, species,
  DBH, height, crown, age, site index, damage, measurement dates.
- Georeferenced site-series/ecosystem polygons.
- Approved UWR boundary and legal mule-deer objectives.
- 2003 Knife Creek transition strategy.
- Appendix 9 compartment/harvest-unit/reserve/OGMA polygons.
- Cutblock/opening polygons with harvest type/date, roads, fire severity and
  salvage.
- Current mule-deer habitat/suitability layers and legal attributes.
- Any FVS-BC/VDYP/TIPSY calibration, volume/decay equations or yield curves.
- Publication permissions: public, derived, or private-only.

## Next moves

1. Ingest the Ionut dump when it arrives and replace the regional PSP analog
   with KC CFI where possible.
2. Build KC AU strata and the FVS-BC state-transition library (P1.4/P2).
3. Use the conditional PSP lists for structural tests until then.
4. Add a `fresh-fvsbc` package note/test for the BC THINQFA cm fields.
5. Do not claim legal UWR compliance, calibration, or infinite information.

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
