# AFRF Knife Creek Instance Roadmap

This roadmap is the plan of record and the issue tracker map for the AFRF Knife
Creek ws4 instance. Keep it in step with the GitHub issues, `CHANGE_LOG.md`, and
`notes/`. `scripts/check_workflow.py` parses the phase headers, status lines,
and checkboxes below, so keep their format.

Every phase starts as `planned` with `Parent issue: TBD`. Activate a phase only
after its parent issue exists and the maintainer approves it.

## Issue Tracker Map

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P0 Bootstrap and growth-engine contract | #1 | `feature/p0-bootstrap` | complete |
| P1 Data acquisition and stem lists | #7 | `feature/p1-data-acquisition` | active |
| P2 FVS-BC state-transition library | TBD | `feature/p2-state-library` | planned |
| P3 ws4 instance assembly | TBD | `feature/p3-ws4-assembly` | planned |
| P4 Verification and scenarios | TBD | `feature/p4-verification` | planned |
| P5 Release v0.1 | TBD | `feature/p5-release` | planned |
| P6 Maintain and merge readiness | TBD | `feature/p6-maintain` | planned |

## Lifecycle Map

| Stage | Phases | Exit criteria |
| --- | --- | --- |
| Scope and design | P0 | The instance contract, data requirements, and growth-engine decision are recorded |
| Build | P1, P2, P3 | Inputs are acquired, the FVS-BC state library is reproducible, and ws4 compiles the matrix |
| Verify | P4 | The baseline and selection scenarios have evidence and stated limits |
| Release and deploy | P5 | Tag, release notes, and a clean-checkout verification are approved |
| Operate and maintain | P6 | Review cadence holds and the merged-model contract is current |

## Conventions

- A phase is `P<n>`. A task is `P<n>.<m>`. A subtask is a checklist item inside
  the task's issue body. Three levels at most.
- Status values are `planned`, `active`, `pr-open`, `complete`, and `deferred`.
- A phase becomes `complete` only after its pull request merges to `main` and
  its parent issue closes.
- Source data is immutable. Derived stem lists, FVS-BC runs, and ws4 datasets
  are reproducible outputs, not edits of the source.

## Phase 0: Bootstrap and growth-engine contract

Parent issue: #1
Branch: `feature/p0-bootstrap`
Status: complete

Goal: adapt the workflow surfaces, state why Knife Creek needs uneven-aged
continuous cover, and record the FVS-BC growth-engine and ws4 state-transition
contracts.

- [x] P0.1 Adapt `AGENTS.md`, `README.md`, and the roadmap to Knife Creek (#2)
- [x] P0.2 Record the uneven-aged growth-engine decision and the FVS-BC pin (#3)
- [x] P0.3 Record the data acquisition and publication boundary (#4)
- [x] P0.4 Scaffold the FVS-BC regime and ws4 state-transition templates (#5)
- [x] P0.5 Confirm the green dashboard and the docs build (#6)

Acceptance criteria:

- The repository states why VDYP and TIPSY are not the primary growth engine
  for Knife Creek.
- The FVS-BC wrapper is pinned by repository and commit.
- The data requirements identify every input needed before a pilot run.
- `python scripts/dashboard.py` is green.

## Phase 1: Data acquisition and stem lists

Parent issue: #7
Branch: `feature/p1-data-acquisition`
Status: active

Goal: acquire and verify the Knife Creek boundary, inventory, BEC, site index,
disturbance, and mule-deer constraints, then construct reviewed stem lists.

- [x] P1.1 Acquire and checksum the legal boundary and block identifier (#8)
- [x] P1.2 Acquire VRI, BEC, site-series, and disturbance source data (#9)
- [ ] P1.2a Acquire the AFRF site-series map and legal UWR/HMZ spatial layer (#15)
  - [x] Acquire the 2007 GWM order text, 2003 transition plan, Part 1a/1b,
    Extension Note 25A and LMH 13.
  - [x] Acquire the HMZ spatial layer and VRI crosswalk
    (`data/habitat/mule_deer_hmz_kc.gpkg`).
  - [ ] Verify the legal UWR boundary and stand-structure map.
- [x] P1.2b Recover public figure and table benchmarks (#18)
- [x] P1.2c Pin the THINQFA-capable fresh-fvsbc (#22)
- [x] P1.2d Correct THINQFA BC units and record the pilot (#25)
- [ ] P1.3 Acquire or reconstruct tree-level tallies and CFI plot data (#10)
  - [x] Build a LidarBC canopy-tree inventory pilot for one 2024 tile.
  - [x] Extend the 2024 DEM/DSM run to all downloaded tiles: 278,318 canopy
    trees, 28 tiles intersecting the SUP.
  - [x] Derive block-level LiDAR clump features and add them to
    `ws4/dataset_kc_spatial_v2`.
  - [ ] Calibrate the canopy inventory against a CFI and replace the FVS
    DBH-ranked reserve proxy with observed clumps.
  - [x] Build a public IDF Cariboo PSP stem-list analog for the interim pilot.
  - [x] Fit a QMD/TPA Weibull scale regression and generate conditional lists.
  - [ ] Acquire the Knife Creek CFI or released tree list.
- [ ] P1.4 Build AU strata and nemora stem populations (#11)
- [ ] P1.5 Record the data-quality and coverage audit (#12)

Findings:

- FADM_TSA confirms the block is in Williams Lake TSA (TSA 29). The TSA
  boundary is not the research-forest boundary.
- The legal boundary is Special Use Permit S15382, "Research or Educational",
  ACTIVE, in the public Forest Tenure Special Use Permit Polygon layer. It is
  3,533.1341 ha and is stored at
  `data/boundaries/knife_creek_sup_S15382.gpkg`.
- The SUP polygon is OGL-BC and public. The raw fetch is reproducible with
  `femic data bcdc-fetch`; see `metadata/boundary_source.yaml`.
- The published Management and Working Plan area is 3,487 ha, a 46.13 ha
  difference from the SUP permit block area. The SUP polygon is the legal gross
  boundary; the net area waits on the VRI join.
- VRI 2025 R1: 183 clipped polygons over 3,533.13 ha; 160 FDI-leading; 174 of
  183 carry a site index.
- BEC map: IDFdk3 3,051.80 ha and IDFxm 481.33 ha. No SBPSmk polygon inside
  the SUP in the current map.
- Fire: 2013 6.04 ha, 1938 62.11 ha, 1937 0.66 ha.
- Harvest history: 60 openings over 2,478.73 ha, 1956-2023.
- Mule-deer habitat classes: High 1,327.68 ha, Moderate 1,135.66 ha, Low
  1,020.53 ha, Nil 6.15 ha. These are public classes, not the legal UWR/HMZ
  layer.
- The 2007 GWM order and 2003 transition plan are acquired. GWM 2007 is the
  default basis; Table 29 is a named AFRF alternative. The legal clump is 4–10
  mature trees with interlocking crowns; the legal large-tree threshold is
  37.5 cm and Table 2 D is 70/60/50.
- The Klinka et al. 2004 site-unit report is acquired. It gives the IDFxm
  01-09 and IDFdk3 01-10 site-series classification, nine site groups, keys,
  edatopic grids, and descriptions. The Knife Creek block is 3,484 ha,
  Douglas-fir ~3,000 ha (87%), elevation 720-1,020 m.
- The georeferenced site-series map is **not** in the PDF; it is in the
  report's map pockets/CD-ROM. The spatial site-series map is still P1.2a.
- The AFRF site-series map and the legal UWR/HMZ spatial layer are P1.2a. They
  are not inferred from BEC or the public habitat classes.
- The public FAIB PSP compilation has 338 first-measurement IDF PSPs in the
  Williams Lake and 100 Mile House TSAs. The selected 51 Douglas-fir-leading,
  mature IDF plots yielded 4,553 live trees >=9.1 cm, 45 stable Weibull fits,
  and 24 synthetic one-hectare stem lists (22,178 trees). Three stands ran
  through FVS-BC with the corrected cycle-2 THINQFA; residual BA was 30-34
  m²/ha against the 29 m²/ha target. A QMD/TPA Weibull scale regression was
  fitted; TPA was not significant after QMD, so QMD-only is selected and the
  pooled shape is used. Conditional lists span QMD 18-26 and BA 22.9-29.4
  m²/ha. Generalized gamma was tested but no stable fit beat Weibull. This is
  a regional analog, not KC data. See
  `notes/reference/psp-idf-cariboo-stemlists.md`.

- The AFRF Management and Working Plan #3 (2007) is acquired. It gives the
  AFRF alternative: single-tree selection, 30-year cycle, Table 29 residual
  structures (High 29 m²/ha, D 60 cm, q 1.25; Moderate 22/55/1.25; Low
  16/50/1.30), and Table 35 AAC (82.0 ha/year selection, 11.2 ha/year salvage).
  GWM 2007 is the default legal basis; Table 29 is the AFRF comparison.
- MWP #3 Figure 11 was recovered with `figrecover` 0.1.0a1. The reviewed table
  is `data/benchmarks/mwp3_figure11_target_stand_structure.csv`; recovered BA
  sums are 17.02/22.96/30.17 m²/ha vs Table 29 16/22/29. Use Table 29 for the
  AFRF shape comparison and Figure 11 for the shape.
- The Klinka 2004 site-index tables are transcribed as
  `data/site_index/klinka_2004_site_index.csv` (105 rows; IDFxm, IDFdk3,
  SBSdw1, ICHmk3).
- MWP #3 Appendix 9 gives the KC01–KC11 and RD05–RD07 compartment table (gross
  3,485.6 ha, net 3,162.3 ha). The map is schematic and has no coordinate grid;
  it is not a georeferenced GIS layer.
- The default GWM 2007 cut uses `THINABA` above 37.5 cm to the legal
  large-tree minimum, then `THINQFA` on 0–37.5 cm. Table 29 uses full-range
  `THINQFA`. `THINBTA` is a trees-per-acre target, not a basal-area target.
  The wrapper now supports `THINQFA`'s supplemental record at pin `d86e78b`
  (P1.2c).
- A synthetic pilot (P1.2d) settled the entry cycle: cycle 1 is year 0; cycle 2
  with `TIMEINT=,30` is year 30. The BC variant converts `THINQFA` fields 2, 3
  and 6 from centimetres to inches, so the KC templates store those fields in
  centimetres. Passing inches shortened the range and cancelled the activity.
  The pilot also showed that `THINQFA` does not guarantee the residual BA target
  from a grown stand with a q deficit. Evidence:
  `notes/reference/fvsbc-thinqfa-pilot.md`.

Acceptance criteria:

- Every source has a provenance record and checksum.
- The boundary and inventory join without unexplained gaps.
- Each AU has a documented stem-list basis and a stated uncertainty.

## Phase 2: FVS-BC state-transition library

Parent issue: TBD
Branch: `feature/p2-state-library`
Status: planned

A **legacy Table 29** structural library exists at `ws4/state_library_v0/` (8
initial states, 6 residual states, 48 transitions, 192 curves). It is not the
default GWM basis. A veteran/large-tree retention policy pilot is at
`ws4/policy_pilot_v0/` (4 policies × 3 regimes × 2 stands, 24 transitions,
276 geometric clump scenarios). It is not a closed graph and not a compiled
ws4 dataset; Phase 2 has not been opened as a formal phase. The public PSP stem
maps are too sparse for empirical clump geometry; the clump scenarios are
explicit geometric assumptions, not observations.

The 2007 shallow/moderate GWM order and the 2003 Knife Creek transition plan
have been acquired. GWM 10 requires clumps of 4–10 or more mature trees with
interlocking crowns, BA >37.5 cm ≥16/11/6 m²/ha, and Table 2 D ≥70/60/50 for
High/Moderate/Low. The AFRF Table 29 uses lower D (60/55/50); it is an AFRF
interpretation, not the legal curve. See
`notes/reference/mdwr-canopy-clump-requirements.md`.

Goal: run FVS-BC selection-cut regimes and build the state-transition library
that ws4 will consume. The next library is `state_library_v1` with
`basis=GWM_2007`; v0 remains the Table 29 comparison.

- [x] P2.1 Define the state key and the selection regimes
- [~] P2.2 Run the FVS-BC GWM pilot; stand-structure pass 17/30. The selected
  rule is post-FVS clump reserve (largest 2–5 above D per 4–10-tree clump),
  13/15 pass with a DBH-ranked six-tree proxy. A spatial clump rule is still
  required for KC.
- [~] P2.3 Build the multi-cycle state graph and canonicalize states. v1 has
  48 transitions and 72 per-chain states; graph closure and shared
  canonicalization are still open.
- [~] P2.4 Generate ws4 tracks, treatments, curves, features, and products.
  A synthetic 4-block dataset and a 160-block VRI/HMZ spatial structural dataset
  validate. The KC operating dataset is still blocked on CFI and spatial
  clumps; the HMZ layer is acquired and enforced structurally.
- [ ] P2.5 Record the library manifest and validation evidence

Acceptance criteria:

- One AU completes at least two selection cycles without losing state.
- Every transition has a pre-cut state, a cut list, a residual state, and a
  growth curve.
- The library validates against the ws4 schema.
- The known limits of FVS-BC and the wrapper are recorded.

## Phase 3: ws4 instance assembly

Parent issue: TBD
Branch: `feature/p3-ws4-assembly`
Status: planned

Goal: compile the Knife Creek ws4 dataset and run a first baseline.

- [ ] P3.1 Map blocks and AUs to initial state tracks
- [ ] P3.2 Compile the ws4 dataset
- [ ] P3.3 Generate topology and patch accounts
- [ ] P3.4 Build and run the baseline selection schedule
- [ ] P3.5 Record the assembly evidence

Acceptance criteria:

- `ws4 validate` accepts the dataset.
- The baseline uses selection entries only; no clearcut treatment exists.
- The cutting cycle and mule-deer constraints are enforced or explicitly
  reported as not yet enforced.

## Phase 4: Verification and scenarios

Parent issue: TBD
Branch: `feature/p4-verification`
Status: planned

Goal: verify the model and compare selection regimes and estate-level targets.

- [ ] P4.1 Verify area, AU, and state coverage
- [ ] P4.2 Verify the FVS-BC transition and growth curves
- [ ] P4.3 Run the baseline and at least two selection regimes
- [ ] P4.4 Record the scenario comparison and caveats

Acceptance criteria:

- Every block maps to a state and an AU.
- The scenario comparison states what is calibrated, assumed, and deferred.
- The mule-deer habitat indicators are reported.

## Phase 5: Release v0.1

Parent issue: TBD
Branch: `feature/p5-release`
Status: planned

Goal: tag and publish the Knife Creek instance with release notes and a clean
checkout verification.

- [ ] P5.1 Write release notes and the known-gaps list
- [ ] P5.2 Tag and publish after maintainer approval
- [ ] P5.3 Verify the release from a clean checkout

Acceptance criteria:

- The release notes match the evidence.
- A clean checkout reproduces the FVS-BC pilot and the ws4 validation.

## Phase 6: Maintain and merge readiness

Parent issue: TBD
Branch: `feature/p6-maintain`
Status: planned

Goal: keep the instance current and define the contract for the future merged
AFRF model.

- [ ] P6.1 Set a review cadence and record the first review
- [ ] P6.2 Define the cross-block identifier, track, and account contract
- [ ] P6.3 Record the merged-model handoff and open questions

Acceptance criteria:

- The merge contract is specific enough to implement without re-reading this
  roadmap.
- The sibling Gavin Lake instance can consume the contract.

## Detailed Next Steps Notes

0. The persistent public-data/FVS-BC session record is
   `notes/reports/2026-10-27-public-data-and-fvsbc-handoff.md`. Read it before
   resuming; it indexes the data, decisions, pilots, PRs, blockers and the
   private-data request list.
1. Phase 0 is complete under parent issue #1.
2. Phase 1 is active under parent issue #7. P1.1 (boundary) and P1.2 (public
   layers) are complete.
3. P1.2a (#15) is blocked on the AFRF site-series map and the legal UWR/HMZ
   spatial layer. The 2007 order text and 2003 transition plan are acquired.
4. P1.2b (#18) is complete: public benchmarks from MWP #3 Figure 11, the
   Appendix 9 compartment table, and the Klinka 2004 site-index tables are
   reviewed and committed.
5. P1.3 (#10) has a public IDF Cariboo PSP stem-list analog for the interim
   pilot; the KC CFI or released tree list is still the preferred basis. P1.4
   (#11) is the next model-preparation task: build AU strata and stem
   populations.
6. Run a GWM 2007 legal-basis pilot on the conditional PSP stands, then rebuild
   the state library as `state_library_v1` with `basis=GWM_2007`. Do not compile
   the legacy Table 29 v0 library as legal compliance. The synthetic THINQFA
   pilot and the BC unit check are complete; the KC stem list is still missing.
