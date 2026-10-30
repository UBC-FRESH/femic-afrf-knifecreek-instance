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
- Completed P1.2: acquired the public VRI 2025 R1, BEC map, historical fire
  perimeters, consolidated-cutblock harvest history, and Cariboo mule-deer
  stand structure habitat classes. All layers are clipped to the SUP S15382
  boundary in EPSG:3005.
- Recorded coverage: VRI 183 polygons over 3,533.13 ha (160 FDI-leading, 174
  with site index); BEC IDFdk3 3,051.80 ha and IDFxm 481.33 ha; fire 2013
  6.04 ha, 1938 62.11 ha, 1937 0.66 ha; harvest 60 openings over 2,478.73 ha,
  1956-2023; mule-deer High 1,327.68 ha, Moderate 1,135.66 ha, Low 1,020.53 ha,
  Nil 6.15 ha.
- Added `metadata/layer_sources.yaml`, `metadata/data_sources.csv`, and the
  clipped layers under `data/inventory/` and `data/habitat/`. The raw
  consolidated-cutblock polygons are not committed because the catalogue records
  them as Access Only; a derived harvest-history table is committed instead.
- Opened P1.2a (#15) for the two authoritative layers that are not available
  from the public BCDC pass: the AFRF site-series / ecosystem map and the
  approved UWR boundary plus legal mule-deer objectives. They are not inferred
  from BEC or the public habitat classes.
- Acquired the Klinka et al. 2004 AFRF site-unit report
  (`reference/AFRF-site-unit-report-2004.pdf`, SHA-256 `94459a7b…f5705`). It
  gives the IDFxm 01-09 and IDFdk3 01-10 site-series classification, nine site
  groups, keys, edatopic grids, and descriptions. The extract is
  `config/site_series.yaml`; the context note is
  `notes/reference/site-series-klinka-2004.md`.
- Recorded that the report's georeferenced site-series maps are in the map
  pockets/CD-ROM, not the PDF. The spatial site-series map remains blocked under
  P1.2a (#15). The report gives Knife Creek as 3,484 ha, Douglas-fir ~3,000 ha
  (87%), elevation 720-1,020 m.

## 2026-10-27

- Activated P1.2b (#18) to turn the quantitative public figures and tables in
  the AFRF reference documents into reviewed benchmark data.
- Acquired the AFRF Management and Working Plan #3
  (`reference/AFRF-management-working-plan-3-2007.pdf`, SHA-256 `9bfd8b8f…ff6a`).
  It is a public UBC AFRF planning document, not OGL. Extracted the Knife Creek
  MDWR contract into `config/mdwr_regimes.yaml`: single-tree selection,
  30-year cycle, Table 29 structures (High 29 m²/ha, D 60 cm, q 1.25; Moderate
  22/55/1.25; Low 16/50/1.30), Table 35 AAC (82.0 ha/year selection, 11.2
  ha/year salvage), and the 0% conventional / 95% modified / 5% no-harvest
  outcome. The legal UWR order and 2003 transition strategy remain blocked.
- Recovered MWP #3 Figure 11 with `figrecover` 0.1.0a1 after rendering page 97
  at 300 dpi, masking the legend, and calibrating the bar/line chart. The
  reviewed table is `data/benchmarks/mwp3_figure11_target_stand_structure.csv`;
  the long table, metadata, review manifest and recovery note are beside it.
  Recovered basal-area sums are 17.02/22.96/30.17 m²/ha for Low/Moderate/High
  versus Table 29 targets 16/22/29. Table 29 remains the target; Figure 11 is
  the relative diameter-distribution shape.
- Transcribed MWP #3 Appendix 9 (PDF page 162) into
  `data/benchmarks/mwp3_kc_compartments.csv`: KC01–KC11 and RD05–RD07; gross
  3,485.6 ha, net 3,162.3 ha. The source map is schematic with no coordinate
  grid, so it is a table transcription, not a GIS layer.
- Transcribed Klinka et al. 2004 Tables 8.2.1–8.2.4 into
  `data/site_index/klinka_2004_site_index.csv` (105 rows; IDFxm, IDFdk3,
  SBSdw1, ICHmk3; site index m @ 50 yr bh). The report's figures are
  photographs and flow diagrams, not quantitative charts; the tables are the
  right source.
- Recorded the FVS-BC keyword correction: `THINQFA` implements BDq;
  `THINBTA` is a thin-from-below to a trees-per-acre target, not basal area.
  Replaced the placeholder `SEL_BA18/25/30` regimes with
  `SEL_MDWR_HIGH/MODERATE/LOW`. Added the wrapper gap: `fresh-fvsbc` 0.11.0
  does not yet model the `THINQFA` supplemental residual-density-units record.
- Kept the MWP #3 page-162 map out of the GIS stack. It has a north arrow and a
  scale bar but no coordinate grid; a georeference would need control points
  from the SUP/VRI/road network and should be treated as approximate.
- Checked the recovered Figure 11 density distribution against the Table 29
  q-factors. The log-linear fit gives q 1.306/1.254/1.253 for
  Low/Moderate/High, versus 1.30/1.25/1.25. The basal-area totals remain
  4-6% above Table 29; the q shape agrees closely.
- Recorded the MWP #3 landscape-map inventory: Appendix 3 (forest cover),
  Appendix 7 (seral stage), Appendix 9 (compartments), Appendix 10 (harvest
  priorities), Appendix 11 (roads) and Appendix 12 (research projects). The
  Knife Creek pages are 150, 158, 162, 164, 166 and 168. They are schematic
  planning maps with north arrows and scale bars but no coordinate grids; no
  page was georeferenced.

## 2026-10-27

- P1.2c: moved the `fresh-fvsbc` pin from `ca33d0e` (0.11.0) to
  `d86e78b0fc31386684aae1a0a1a9a821c0ee2baf` (0.12.0, post-v0.12.0 main).
  The new pin carries P42.1's `THINQFA` supplemental-record support, so the KC
  `SEL_MDWR_HIGH/MODERATE/LOW` regimes are now expressible.
- Marked the `THINQFA` supplemental-record wrapper gap resolved in
  `config/fvsbc/regimes.yaml`. The entry-year/cycle semantics and the stem list
  remain the blockers to a real FVS-BC run.
- Updated the README, growth-engine guide, state-transition design, pilot
  runbook and ADR 0002 to name the new pin and to stop calling the supplemental
  record a blocker.

## 2026-10-27

- P1.2d: ran the controlled synthetic `THINQFA` pilot against the built
  `FVSbc`. Cycle 1 cuts at year 0; cycle 2 with `TIMEINT=,30` and `NUMCYCLE=2`
  cuts at year 30; cycle 4 with `TIMEINT=,10` also cuts at year 30. The
  entry-year question is settled.
- Corrected the BC `THINQFA` units. `canada/bc/initre.f` converts fields 2, 3
  and 6 (minimum DBH, maximum DBH, class width) from centimetres to inches.
  The KC templates had stored those fields in inches; passing `23.62` shortened
  the range to about 23.6 cm and the activity was cancelled. The templates now
  store `0.0`, `60.0`/`55.0`/`50.0` and `5.0` cm. The residual-density target
  remains square feet per acre (`126.32`/`95.83`/`69.70`).
- Added `notes/reference/fvsbc-thinqfa-pilot.md`. The pilot also showed that
  `THINQFA` does not guarantee the residual BA target from a grown stand with a
  q deficit; the High Figure 11 shape left 36 m²/ha against a 29 m²/ha target.
  This is recorded as a structural caveat, not a calibration result.
- Removed the remaining "inches" wording from the KC README, growth-engine
  guide, regime templates and pin note. The regimes remain not runnable until a
  KC stem list exists.

## 2026-10-27

- P1.3 interim: acquired the public FAIB PSP compilation and built an IDF
  Cariboo stem-list analog instead of waiting for the KC CFI. The source is the
  FAIB Forest Inventory Ground Plot Data FTP, Open Government Licence - BC.
- Filtered to first-measurement, Douglas-fir-leading, mature IDF PSPs in the
  Williams Lake and 100 Mile House TSAs: 51 plots, 4,553 live trees >=9.1 cm,
  45 stable per-plot Weibull fits.
- Fit the pooled lower-truncated Weibull: a=1.0200, beta=7.8411, lower bound
  9.1 cm, KS=0.0109. Added `runbooks/build_psp_stemlists.py` and generated 24
  synthetic one-hectare stem lists (22,178 trees) by inverse-CDF sampling,
  calibrated to each source plot's BA. Files are in `data/psp/`.
- Ran three PSP-derived stands through FVS-BC with the corrected cycle-2
  THINQFA. Residual BA was 30-34 m2/ha against the 29 m2/ha target; the
  structural caveat is recorded. This is a regional IDF analog, not KC data.
- Recorded the source hashes, selection, fitting and caveats in
  `notes/reference/psp-idf-cariboo-stemlists.md`. Raw PSP files are not
  committed.
- P1.3b: pinned `nemora` at `2e8776c0ffce15cb4b18e2fbd70bdd4c1c4467d9`
  (`0.0.1-alpha`) for the PSP stem-list fit and inverse-CDF sampling. The note
  records that nemora has grouped PDF fitting, not a covariate regression;
  the per-plot fits are retained for that next step.
- P1.3c: fitted a Weibull DBH scale regression on QMD/TPA. The QMD-only
  model is selected (`log beta = -3.863 + 2.049 log QMD`, R² 0.471, adj. 0.459,
  LOOCV 0.306); TPA is not significant after QMD (`t=0.86`, VIF 2.71). The
  shape `a` is not predictable; the pooled `a=1.0200` is used. Five conditional
  stem lists span QMD 18-26 and BA 22.9-29.4 m²/ha. Generalized gamma was
  tested; no stable GG fit beat Weibull, so Weibull is retained. Two conditional
  stands ran through FVS-BC; residual BA was 35-38 m²/ha against the 29 target.
- Added the persistent 2026-10-27 handoff at
  `notes/reports/2026-10-27-public-data-and-fvsbc-handoff.md`. It records the
  standing requirements, public data, Figure 11 recovery, MWP #3 contract,
  THINQFA unit/cycle findings, PSP/regression work, maps, PR/commit index,
  blockers, and the Ionut data request list. Chat is not the durable record.
- P2.0 v0: built the provisional FVS-BC state-transition library at
  `ws4/state_library_v0/`. Eight PSP-derived stands × three Table 29 regimes ×
  two 30-year entries produced 8 initial states, 6 residual states, 48
  transitions and 192 curves. Mean residual BA was 33.31/29.19/25.94 m²/ha
  against 29/22/16; mean q was 1.284/1.255/1.296 against 1.25/1.25/1.30;
  mean residual max DBH was ~73.6 cm against 60/55/50. The residual graph is
  not closed and no ws4 dataset has been compiled. The gap is recorded as a
  structural result, not a calibration claim.
- P2.0 policy pilot: added `config/retention_policies.yaml` and
  `ws4/policy_pilot_v0/`. Four policies on two PSP-derived conditional stands
  × three Table 29 regimes: `RETAIN_ABOVE_D`, `LT4_50`, `LT6_50`, `LT8_50`.
  Split policies hit the total BA target (High 27–28 vs 29; Moderate/Low exact)
  while holding large-tree BA at 4/6/8 m²/ha. `RETAIN_ABOVE_D` left 31–37.5
  m²/ha and 14.5–15.6 m²/ha of large trees in the cases with an after-treatment
  tree list. Clump count and crown-cover are post-processing proxies, not
  spatial snow modelling.
- P2.2 clump geometry and PSP stem-map limits: added
  `runbooks/build_clump_scenarios.py`, `clump_scenarios.csv`/summary (276
  scenarios), and `notes/reference/psp-stem-map-limits.md`. Of 45 stable PSP
  plots, 11 are fully mapped and only one has more than one mapped tree ≥50 cm;
  the public PSP analog cannot estimate clump size or spacing. The clump
  scenarios are explicit geometry, not observations. Corrected the pilot to
  treat a canceled treatment with no after-treatment tree list as missing
  large-tree metrics rather than zero.
- P2.3 MDWR source correction: acquired the 2007 Shallow/Moderate GWM order,
  the 2003 Knife Creek transition plan, Part 1a/1b (LMH 60/59), Extension Note
  25A and LMH 13. GWM 10 requires clumps of 4–10 or more mature trees with
  interlocking crowns; the 2–5 figure in MWP #3 is only the maximum-diameter
  subgroup. Legal stand-level targets use BA >37.5 cm ≥16/11/6 m²/ha and Table
  2 D ≥70/60/50 for High/Moderate/Low; MWP #3 Table 29 uses D 60/55/50 and is
  an AFRF interpretation, not the legal curve. Added the source index, updated
  the clump scenarios to 4–10 trees, and recorded the Knife Creek HMZ matrix
  and the north-facing >20% slope, >10 ha exemption. No legal-compliance claim.
- P2.4 MDWR legal basis is the default, with user-facing docs: added ADR 0005,
  GWM 2007 default and Table 29 named alternative in `config/mdwr_regimes.yaml`
  and `config/fvsbc/regimes.yaml`, and the surplus-large-tree split cut
  (`THINABA` above 37.5 cm, then `THINQFA` 0–37.5 cm). Added Sphinx pages
  `reference/mdwr-legal-basis` and `guides/mdwr-habitat-constraints`, plus the
  legal target/HMZ/clump CSVs. `state_library_v0` is marked legacy Table 29;
  `state_library_v1` is the planned GWM 2007 rebuild. No legal-compliance claim.
- P2.5 GWM 2007 legal-basis pilot: added `runbooks/build_gwm_pilot.py` and
  `ws4/gwm_pilot_v0/` (5 stands × 3 classes × 2 methods; 30 transitions, 120
  curves). Stand-structure pass 17/30. Retain above D passes 13/15; the
  D-protected split passes 4/15 because the >D reserve pushes q above the legal
  range in most High/Moderate cases. A full-range split meets q but strips the
  largest trees and leaves max DBH below D. This is not a legal-compliance
  result; a tree-level reserve/marking rule is required before `state_library_v1`.
- P2.6 selected clump-reserve rule: added `runbooks/apply_clump_reserve.py`
  and `clump_reserve.csv`/summary. Start from the retain-above-D FVS result,
  reserve the largest 2–5 trees above D per 4–10-tree clump (DBH-ranked
  six-tree proxy), and harvest the rest above D. 13/15 cases pass; mean removed
  large BA 1.07/2.64/5.12 m²/ha. High `PSP-REG-001` and `PSP-REG-002` fail on
  starting large-tree structure. Retrospective marking scenario, not a new FVS
  growth run and not a legal-compliance claim.
- P2.7 provisional GWM 2007 state library v1: added
  `runbooks/build_state_library_v1.py` and `ws4/state_library_v1/` (8 stands ×
  3 GWM classes × 2 entries; 48 transitions, 192 curves, 72 per-chain states).
  The FVS cut is followed by the selected clump-reserve marking rule and a
  weighted residual resample. 33/48 stand-structure checks pass. The graph is
  not closed and the clump proxy is not spatial; no legal-compliance claim.
- P2.8 canonical graph and synthetic ws4 compile: added
  `runbooks/canonicalize_state_library.py`, `ws4/state_library_v1/canonical/`
  (23 states, 25 transitions, 500 curve rows, 6 terminal states, 0 cycles),
  `runbooks/compile_ws4_dataset.py` and `ws4/dataset_v1_synthetic/` (4 synthetic
  1 ha blocks, 23 tracks, 25 treatments, 575 curves). `ws4 validate` passes.
  The dataset is a structural fixture, not a KC operating dataset.
- P2.9 HMZ spatial acquisition: fetched the BC Map Hub/DataBC Cariboo mule-deer
  HMZ layer, clipped it to SUP S15382 and built a VRI × HMZ crosswalk. Areas:
  HMZ 1 M 738.29 ha, 2 L 1,217.15 ha, 3 M 320.51 ha, 4 M 1,213.33 ha, 5 A
  0.00045 ha; total 3,489.27 ha against the 3,533.13 ha SUP. Added
  `runbooks/fetch_mdwr_hmz.py`, `runbooks/assign_hmz.py` and
  `notes/reference/mdwr-hmz-layer.md`. The synthetic ws4 dataset is not yet
  spatially masked.
- P3.0 spatial VRI/HMZ dataset: added `runbooks/compile_kc_spatial_dataset.py`
  and `ws4/dataset_kc_spatial_v1/` (160 clipped VRI blocks, 3,481.77 ha, 92
  HMZ-specific tracks, 49 treatments). HMZ groups M 113, L 44, U 3; M offers
  Low/Moderate, L offers Low only, U offers no treatment. `ws4 validate`
  passes. Tree lists remain PSP-derived and clumps remain a DBH-ranked proxy;
  this is still a structural fixture, not a KC operating model.
- P3.1 LidarBC canopy inventory pilot: discovered 134 point-cloud, 76 DEM and
  72 DSM tiles over the SUP; downloaded the 2024 1 m DEM/DSM for tile
  `093a001_2_4_3`; built 20,513 canopy trees over 247.56 ha (82.9 TPH), with
  spatial clump analysis. At 10 m linkage for trees ≥20 m: 2,177 clumps, 207
  4–10-tree clumps, 1,418 singletons, 8.8 clumps/ha. Added
  `runbooks/lidar_tree_inventory.py`, `notes/reference/lidarbc-kc-pilot.md` and
  the LiDAR Sphinx page. DBH is height-allometry only; this is not a CFI.
- P3.2 all-2024 LidarBC canopy inventory: downloaded all 72 2024 DEM/DSM
  pairs (940 MB); 28 tiles intersect the SUP enough to produce clipped trees.
  Added `runbooks/lidar_inventory_all_tiles.py` and `data/lidar/kc_2024/`:
  278,318 canopy trees, 78.8 TPH, height mean 19.5 m, 117,297 trees ≥20 m.
  At 10 m linkage, 50,401 clumps and 6,046 4–10-tree clumps. The inventory is
  still canopy-only, with height-allometry DBH and no species/understory.
- P3.3 LiDAR block features: added `runbooks/lidar_block_features.py` and
  `data/lidar/kc_2024/block_tree_summary.csv`. All 160 spatial blocks have
  LiDAR coverage; mean 77.2 TPH, 39.1 large TPH (≥20 m), 18.2 4–10-tree
  clumps/ha. Added `ws4/dataset_kc_spatial_v2/` with block group clump classes
  (29 `<10`, 54 `10–20`, 68 `20–30`, 9 `30+` clumps/ha); `ws4 validate`
  passes. The FVS treatment reserve remains the DBH-ranked proxy.
- P3.4 spatial LiDAR reserve scenario: added
  `runbooks/lidar_reserve_scenario.py` and
  `data/lidar/kc_2024/reserve_trees.parquet` / `block_reserve_summary.csv`.
  4–10-tree clumps reserve the three largest trees; 88,640 reserve and 28,191
  harvest trees across 160 blocks (mean 30.0 reserve TPH, 9.15 harvest TPH).
  Added `ws4/dataset_kc_spatial_v3/` with observed clump and reserve classes;
  `ws4 validate` passes. The FVS treatment reserve remains the DBH-ranked
  proxy, so this is still not the FVS tree-level cut.
- P3.5 AFRF KC PSP data documentation: added ADR 0006, the reference note
  `kc-afrf-psp-dataset.md` and the Sphinx page `kc-afrf-psp-data`. Read FRDA
  Report 242, FRDA 267 and the 2020 Forests paper. Confirmed the 24 × 0.05 ha
  rectangular plots (15.81 × 31.62 m), plot/block/treatment mapping, `P = I/B`
  interior/buffer distinction, vigor classes, crown-diameter and live-crown
  definitions. Remaining unknowns: `TS`, `TC`, `D1/D2/DA/DS/WTA`, `HT13`,
  duplicate columns and exact X/Y conversion. Raw workbook remains private.
- P3.6 AFRF KC PSP ingest and first FVS backtest: added the private tidy tree
  ingest, public plot summary/schema/metadata under `data/psp/`, and
  `ws4/kc_psp_validation/`. 1993 interior trees with 20× expansion; no cut.
  v0's intermediate-year table was misaligned and is superseded by v1 below.
- P3.7 PSP mortality/ingrowth analysis and MORTMULT sensitivity: added
  `runbooks/summarize_psp_dynamics.py` and public dynamics summaries; observed
  annual mortality 1.0/1.4/2.1/2.4% across the four intervals. Corrected the
  FVS interval alignment to 4/7/4/5 years. v1 2013: BA 36.42 vs 35.38, QMD
  14.61 vs 14.98, TPH 2,713 vs 2,291. MORTMULT 1/2/2.5/3/4 at 2013 gives TPH
  +422/+126/-0.5/-115/-336 and BA +1.04/-2.00/-3.25/-4.34/-6.67. No global
  multiplier fits both; site-index 80 vs 60 was identical. Structural result,
  not calibration.\n- P3.8 FVS-BC species-group calibration: added
  `runbooks/fvs_calibrate_afrf_kc_psp.py` and
  `ws4/kc_psp_calibration/`. Damped fixed-point fit to 2013 group BA/TPH
  converged at iteration 28 (max parameter change 0.0009, loss change
  3.6e-5). Final 2013 BA 36.38 vs 35.38, QMD 15.76 vs 14.98, TPH 2,313 vs
  2,291. FD/SE/HW match; PL is unmodelled MPB. The earlier 0.5 cm QMD
  threshold was ad hoc and is not a gate. The VRI age/site summary is context
  only: the PSP plots are uneven-aged and have no plot age. FVS-BC does not use
  site index. No legal or whole-block claim.
- P3.9 VRI age/site documentation: added
  `runbooks/summarize_vri_age_site.py` and
  `data/inventory/vri_2025_kc_age_site_summary.json` as polygon-level context
  only. The plots are uneven-aged and have no plot age, so no VRI age was
  backdated or assigned. FVS-BC reports that site index is not used. Removed
  the ad hoc QMD acceptance gate; calibration status is `converged` with
  residual diagnostics.
- P3.10 held-out validation: added `runbooks/fvs_cross_validate_afrf_kc_psp.py`
  and `ws4/kc_psp_cv/`. Leave-one-block-out calibration does not transfer
  consistently: calibrated BA bias is worse when B or C is held out, QMD bias
  is worse when C or D is held out, and fold parameters are unstable. The
  calibration is diagnostic only; the uncalibrated backtest remains the
  defensible structural baseline. No age or site index is assigned.
- P3.11 observed PSP transitions: added
  `runbooks/build_psp_transitions.py` and public derived tables
  `data/psp/kc_afrf_psp_transitions.csv` (96 plot-interval rows) and
  `kc_afrf_psp_transitions_species.csv`. The table carries start/end BA, TPH,
  QMD, height, large-tree metrics, mortality, ingrowth and a Block C/D flag.
  DBH presence is the working live indicator; TS/TC remain unresolved. No age
  or site index is assigned.
- P3.12 state-support audit: added `runbooks/audit_psp_state_support.py` and
  `data/psp/kc_afrf_psp_state_support*.csv/json`. The 96 observed transitions
  map to 18 canonical BA/QMD/large-tree pairs (12 repeated, median 4) but 36
  species-mix pairs with 19 one-off (median 1). Canonical support is sufficient
  only for a coarse graph; species-resolved empirical transitions are too
  sparse. No acceptance threshold is applied.
- P3.13 tree-level models: added `runbooks/fit_psp_tree_models.py` and
  `ws4/kc_psp_tree_models/`. Leave-one-block-out DBH increment RMSE
  0.087–0.102 cm/yr; survival Brier 0.060–0.071 and AUC 0.805–0.896.
  Empirical block/treatment ingrowth still fails transfer (observed/predicted
  totals B 1/81, C 127/18, D 35/64). Start-cohort stand aggregate (no
  ingrowth): BA -0.04 m²/ha (MAE 1.49), TPH +12.8 (MAE 91.1), QMD -0.02 cm
  (MAE 0.31). Growth and survival are diagnostics; ingrowth must be
  block-specific scenario data. No age or site index is assigned.
- P3.15 state reconstruction: added `runbooks/simulate_psp_states.py` and
  `ws4/kc_psp_simulation/`. Leave-one-block-out growth/survival models applied
  to 96 transitions. Cohort (no ingrowth): BA -0.04 m²/ha (MAE 1.49), TPH
  -21.2 (MAE 109.3), QMD +0.11 (MAE 0.34). Conditional (observed recruits):
  BA -0.04 (MAE 1.49), TPH +12.4 (MAE 91.5), QMD -0.02 (MAE 0.31). BA/QMD
  reconstruct well; TPH is noisier. Ingrowth remains block-specific scenario
  data, not a forecast.
- P3.16 simulated-state comparison: added `runbooks/compare_simulated_states.py`
  and state-match tables. Simulated end states match observed canonical
  BA/QMD/large-tree states on 75/96 transitions (78.1%): B 26/32, C 26/32,
  D 23/32. The bins are coarse (all QMD <20 cm, most large BA <6 m²/ha), so
  this is mainly a BA-class match.
- P3.17 partial ws4 generator: added `runbooks/generate_psp_transitions.py`
  and `ws4/kc_psp_generator/`. It generates 24 no-cut, 30-year structural
  curves (BA/TPH/QMD/large BA) in five-year steps, with block/treatment
  ingrowth scenarios held separately. It is not a compiled ws4 dataset and
  has no volume, canopy or treatment response.
- P3.0 activate the Patchworks-compatible Knife Creek package: opened parent
  issue #60, child issues #61–#68, and branch
  `feature/p3-patchworks-package`. The phase now treats fragments.shp,
  tracks/H, product and feature accounts, topology, roads, pin and
  ForestModelXML as primary deliverables, with ws4 ingestion as the runtime
  lane. No model claim is added.
- P3.1 ForestModelXML format spike: checked the Gavin archive, local
  repositories and public sources. No valid ForestModelXML, schema or compiler
  was found. Decision: build the compiled `tracks/H` + `fragments.shp` + pin
  package now, and keep the recipe lane blocked rather than hand-writing
  unvalidated XML. Also corrected X/Y to metres from plot centre and recorded
  the Marshall metadata response.
- P3.2 Patchworks fragment layer: added
  `data/patchworks_knifecreek/spatial/fragments.shp` and derived
  `fragments.csv` for 160 VRI blocks, 3,481.77 ha, EPSG:3005. Block order
  matches `dataset_kc_spatial_v3`; `RES_KEY`/`BLOCK`, `TRACK`, `F_AGE`, BEC,
  HMZ, clump and reserve attributes are carried. Matrix, roads, topology, pin
  and ForestModelXML remain pending.
- P3.3 H-matrix scaffold: added `runbooks/build_kc_patchworks_h.py` and
  `data/patchworks_knifecreek/tracks/H/` with 160 blocks, 92 tracks, 49
  treatments, 174 curves and 549 points. `ws4 ingest` succeeds and
  `ws4 validate` passes. Curves cover 0–30 years only; the 300-year extension,
  accounts, roads, pin and ForestModelXML remain open.
- P3.3a space-for-time PSP panel: added
  `runbooks/build_psp_space_for_time.py` and public IDF Cariboo tables.
  Across 338 IDF sites and 697 visits, 590 visit states pass the screen; 87
  first-measurement site states (age 48–247, BA 5.4–52.5 m²/ha) have 50-year
  no-cut FVS-BC curves. Repeated visits are time-for-time data, not independent
  space-for-time states. This is not a growth chronology and not a KC CFI. H
  feature integration is in P3.3b.
- P3.3b H feature integration: added `runbooks/integrate_psp_space_for_time.py`
  and mapped the 92 IDF Cariboo space-for-time states to the H track states.
  Feature curves now cover 0–50 years for BA, QMD, TPH, canopy and volume;
  products remain 0–30 years. `ws4 ingest` succeeds and `ws4 validate` passes.
  The mismatch in horizon and the minimal accounts remain explicit.
- P3.3c time/space correction: FAIB `CLSTR_ID` is visit-specific; repeated
  visits must be grouped by `SITE_IDENTIFIER`. The panel now uses one first-
  measurement state per stable site: 338 sites, 590 qualifying visits, 87
  sampled site states (age 48–247, BA 5.4–52.5). Added an experimental
  BA-asymptote table; 50 years is too short to treat it as carrying capacity.
  H feature curves were regenerated from the corrected panel and still ingest
  and validate.
- P3.3d stratified space-for-time panel: expanded the public FAIB panel to 132
  first-measurement site states stratified by BEC, leading species, age and BA.
  Ages 44–248, BA 5.5–52.1; 100-year no-cut FVS-BC curves. H feature curves
  were regenerated at 100 years; products remain 30 years. The BA asymptote
  table remains experimental because even 100 years does not reliably reach
  an asymptote. `ws4 ingest` and `ws4 validate` pass.
- P3.4 partial account wiring: added `feature.area.managed.total`,
  `product.area.managed.total` and product area curves; accounts now have eight
  `_MANAGED_` rows. H matrix has 552 feature rows, 98 product rows and 6,660
  curve points; `ws4 ingest` and `ws4 validate` pass. Large-tree/reserve,
  softwood/hardwood split and full group accounts remain open.
- P3.5 topology, roads and structural patch accounts: built 500 block pairs
  (352 touching) at 100 m, 44 BC Forest Tenure road sections (59.6 km), and a
  managed-area patch account. `ws4 simulate --topology --patch-accounts` writes
  patch membership and metrics. Roads are public-derived, not field-verified;
  route configuration remains open.
- P3.6 pin, scenarios and targets: added `KC_H.pin`, `scenarios_KC_H.bsh`,
  `RATIO_ACCOUNTS.bsh`, structural patch targets, `ws4/targets_kc_smoke.yaml`
  and a draft `ws4/targets_kc_gwm2007.yaml`. The GWM draft explicitly lacks
  large-tree, reserve, maximum-DBH and seral accounts and is not legal
  compliance.
