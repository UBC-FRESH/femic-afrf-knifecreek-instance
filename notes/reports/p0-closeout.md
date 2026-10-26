# Phase 0 close-out report

Phase identifier: P0
Status: approved and merged in pull request #13
Branch: `feature/p0-bootstrap`
Parent issue: see `ROADMAP.md`

## Goal

Adapt the workflow surfaces to the Knife Creek instance, record the uneven-aged
growth-engine decision and the data boundary, and scaffold the FVS-BC and ws4
contracts.

## What was done

- Created the repository from the UBC-FRESH dev workflow seed.
- Wrote the instance README, agent contract, roadmap, and changelog.
- Recorded the Knife Creek context: IDF, shade-tolerant Douglas-fir,
  mule-deer winter-range constraints, and the resulting uneven-aged regime.
- Recorded the growth-engine decision: FVS-BC through `fresh-fvsbc`, pinned at
  commit `ca33d0e26a079a72add5108f1b182b798b0c4e3e` (0.11.0).
- Recorded the state-transition design and the ws4 table contract.
- Recorded the data-acquisition requirements and the publication boundary.
- Scaffolded the FVS-BC regime templates and the ws4 target/patch templates.
- Ran the green dashboard on the Phase 0 branch.

## Evidence

- `notes/adr/0001-two-block-instances.md`
- `notes/adr/0002-fvsbc-growth-engine.md`
- `notes/adr/0003-data-publication-boundary.md`
- `notes/adr/0004-merged-afrf-model.md`
- `planning/fvsbc-state-transition-design.md`
- `ws4/state_transition_contract.md`
- `python scripts/dashboard.py` result: recorded in the phase pull request.

## What is not done

- No boundary, inventory, BEC, site index, disturbance, or mule-deer layer is
  committed.
- No stem list or nemora population exists.
- No FVS-BC run exists.
- No ws4 dataset exists.
- The selection regimes are templates, not reviewed policy.

## Risks

- The project cannot run a model until the boundary and inventory are acquired.
- The mule-deer constraints are not yet mapped to model accounts.
- The FVS-BC wrapper is pinned but not installed in this environment; the
  pilot needs the built variant.

## Recommendation

Approve Phase 0 and authorize Phase 1 (data acquisition and stem lists).
Do not start Phase 2 until the boundary, inventory, and a stem-list basis exist.
