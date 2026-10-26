# Knife Creek bootstrap plan

Date: 2026-10-26
Status: Phase 0 in progress

## Goal

Build a public, reproducible ws4 model instance for the Knife Creek block that
represents uneven-aged continuous-cover selection forestry under mule-deer
winter-range constraints.

## Why this is not a standard FEMIC rebuild

FEMIC's standard growth lane is VDYP/TIPSY: stand-level curves for an age-class
model. That is a poor fit for Knife Creek:

- the block is predominantly IDF and Douglas-fir is relatively shade tolerant;
- almost the whole block is under mule-deer winter-range constraints;
- even-aged clearcutting is largely unavailable;
- selection cuts leave a residual diameter distribution that the next entry
  grows from; and
- the estate model needs the removed and retained stems, not only an average
  yield.

The growth engine is FVS-BC through `fresh-fvsbc`. The bridge is a
state-transition library.

## Work breakdown

### Phase 0: bootstrap and growth-engine contract

- adapt the workflow surfaces;
- record the uneven-aged growth-engine decision and the FVS-BC pin;
- record the data acquisition and publication boundary;
- scaffold the FVS-BC regime and ws4 state-transition templates; and
- make the dashboard green.

### Phase 1: data acquisition and stem lists

- boundary and block identifier;
- VRI / forest cover, BEC, site index, disturbance;
- mule-deer winter-range classes and constraints;
- CFI/research plots or a reviewed stem-list reconstruction;
- nemora stem populations per AU; and
- a data-quality and coverage audit.

### Phase 2: FVS-BC state-transition library

- define the state key and regimes;
- run one AU and one regime as a pilot;
- build a multi-cycle state graph;
- canonicalize states and close the graph;
- export ws4 tracks, treatments, curves, features, and products; and
- record the library manifest and validation.

### Phase 3: ws4 assembly

- assign blocks to initial states and AUs;
- build the dataset;
- build topology and patch accounts;
- build a selection-only baseline schedule; and
- run and validate.

### Phase 4: verification and scenarios

- verify area, AU, and state coverage;
- verify growth and transition curves;
- compare at least two selection regimes;
- report mule-deer indicators; and
- record the caveats.

## Data dependencies

| Input | Status | Owner | Notes |
| --- | --- | --- | --- |
| Legal boundary | required | AFRF / maintainer | Must be the Knife Creek block, not all AFRF |
| VRI / forest cover | required | AFRF / BC Data Catalogue | Polygon-level, not a tree list |
| BEC / site series | required | BC Data Catalogue / AFRF | Analysis-unit stratification |
| Site index | required | VRI / AFRF | Species-specific |
| Disturbance history | required | AFRF | 2013 wildfire and harvest history |
| Mule-deer constraints | required | AFRF / province | Spatial classes and values |
| CFI / research plots | optional | AFRF | Preferred stem-list basis |
| Tree-level tallies | optional | AFRF | If CFI is unavailable |

## Risks

- **No tree list.** VRI alone cannot seed FVS-BC. A synthetic nemora list is a
  labelled assumption, not field data.
- **Constraint ambiguity.** Mule-deer objectives may be spatial, structural, or
  both. An unmapped constraint is a gap, not a default.
- **State explosion.** A naive state key can produce too many states. The
  design uses reviewed classes and canonicalization.
- **Uncalibrated FVS-BC.** The first runs are structural and policy
  experiments, not calibrated forecasts.
- **Legacy comparison.** There is no legacy Knife Creek Patchworks model. The
  benchmark is internal consistency and FVS-BC plausibility, not a historical
  replay.

## Decisions

- Two block instances, one future merged model (`notes/adr/0001`).
- FVS-BC is the growth engine (`notes/adr/0002`).
- Public model, restricted sources by permission (`notes/adr/0003`).
- Merged model is a separate repository (`notes/adr/0004`).

## Open questions

1. What is the authoritative boundary source, and who can release it?
2. Are there usable CFI or research plot tree lists for Knife Creek?
3. Which mule-deer constraints are legal requirements and which are guidance?
4. What is the first selection regime to review?
5. How many states are needed before the graph is stable?
6. Should the first public baseline be a single regime or a portfolio?
