# Knife Creek bootstrap plan

Date: 2026-10-30
Status: Phases 0-4 complete; production AAC/estate lane active

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

### Scope boundary

AAC scenario parameters, flow reference periods and harvest-flow targets belong
to the downstream wood-supply analyst. This instance builds and validates the
model they consume: inventory, growth, volume, spatial structure, legal
accounts, provenance and uncertainty.

### Phase 5: production AAC/estate model

- normalize the Marshal tree shapefiles and plot polygons;
- derive LiDAR canopy, clump and opening metrics;
- port the Kozak taper/merchantable-volume equations;
- add spatial clump/opening and retention accounts;
- run the 20-period AAC optimization with the v1/v2c ensemble; and
- publish the AAC range, harvest schedule and legal/structural scorecard.

## Data dependencies

| Input | Status | Owner | Notes |
| --- | --- | --- | --- |
| Legal boundary | acquired | AFRF / maintainer | S15382; verify current order |
| VRI / forest cover | acquired | AFRF / BC Data Catalogue | Polygon-level |
| BEC / site series | acquired | BC Data Catalogue / AFRF | AU stratification |
| Site index | acquired | VRI / AFRF | Species-specific |
| Disturbance history | acquired | AFRF | 2013 wildfire and harvest history |
| Mule-deer constraints | acquired | AFRF / province | Spatial classes and values |
| CFI / research plots | acquired | AFRF | 24 Marshall remeasurements, 1993-2024 |
| Tree-level tallies | acquired | AFRF | 8 spatial tree plots + 24 plot polygons |
| LiDAR | acquired | UBC Research Forests | 2009, 2013, 2019 and 2024 products |
| Taper/volume equations | acquired | UBC Research Forests | Kozak 2004 package |

## Risks

- **Spatial realization.** The model now has tree lists and LiDAR, but the
  stage graph is still non-spatial. Clump and opening layout must be added.
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

1. Which current approved order and HMZ layer governs the block?
2. Which mule-deer constraints are legal requirements and which are guidance?
3. How should the 2019 LiDAR be calibrated to the 2013/2024 plot structure?
4. How should the v1-local and v2c-regional calibrations be weighted for AAC?
5. Should the first AAC be a single even-flow schedule or a portfolio?
