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
| P0 Bootstrap and growth-engine contract | #1 | `feature/p0-bootstrap` | active |
| P1 Data acquisition and stem lists | #7 | `feature/p1-data-acquisition` | planned |
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
Status: active

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
Status: planned

Goal: acquire and verify the Knife Creek boundary, inventory, BEC, site index,
disturbance, and mule-deer constraints, then construct reviewed stem lists.

- [ ] P1.1 Acquire and checksum the legal boundary and block identifier (#8)
- [ ] P1.2 Acquire VRI, BEC, site-series, and disturbance source data (#9)
- [ ] P1.3 Acquire or reconstruct tree-level tallies and CFI plot data (#10)
- [ ] P1.4 Build AU strata and nemora stem populations (#11)
- [ ] P1.5 Record the data-quality and coverage audit (#12)

Acceptance criteria:

- Every source has a provenance record and checksum.
- The boundary and inventory join without unexplained gaps.
- Each AU has a documented stem-list basis and a stated uncertainty.

## Phase 2: FVS-BC state-transition library

Parent issue: TBD
Branch: `feature/p2-state-library`
Status: planned

Goal: run FVS-BC selection-cut regimes and build the state-transition library
that ws4 will consume.

- [ ] P2.1 Define the state key and the selection regimes
- [ ] P2.2 Run the FVS-BC pilot for one AU and one regime
- [ ] P2.3 Build the multi-cycle state graph and canonicalize states
- [ ] P2.4 Generate ws4 tracks, treatments, curves, features, and products
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

1. Phase 0 is active under parent issue #1. The bootstrap commit is on `main`;
   the task issues #2-#6 record the completed surfaces.
2. Phase 1 is planned under parent issue #7. Activate it only after Phase 0 is
   approved and the Phase 0 pull request or bootstrap closeout is accepted.
3. Keep the legacy archive out of Git; commit the sanitized package and its
   hash.
