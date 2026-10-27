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
