# P4 scenario comparison

Status: structural scenario comparison. Not a calibrated-growth result and not
a legal-compliance determination.

Dataset: `ws4/dataset_kc_v1`
Runbook: `runbooks/run_kc_scenarios.py`
Horizon: 30 years
Area: 3,481.773591 ha

## Runs

| Run | Schedule | Scheduled blocks |
| --- | --- | ---: |
| Baseline no cut | empty schedule | 0 |
| GWM low | preferred `GWM_LOW`, fallback `GWM_MODERATE` | 157 |
| GWM moderate | preferred `GWM_MODERATE`, fallback `GWM_LOW` | 157 |

Three blocks have no treatment on their compiled track and therefore receive
no selection entry in either regime. This is a track-operability fact, not a
failure of the schedule.

## End-of-run structural indicators

Values are whole-estate account sums divided by the 3,481.773591 ha model area
where a per-hectare mean is meaningful.

| Indicator | Baseline no cut | GWM low | GWM moderate |
| --- | ---: | ---: | ---: |
| Product yield, first period (m³) | 0 | 575,068 | 546,223 |
| Residual BA (m²/ha) | 67.44 | 25.65 | 27.62 |
| Residual QMD (cm; area-weighted) | 41.74 | 32.60 | 33.01 |
| Residual TPH (stems/ha) | 506.2 | 311.8 | 328.5 |
| Canopy CCF account / ha | 261.1 | 110.8 | 122.6 |
| Feature yield account | 2,725,752 | 806,922 | 902,941 |

Canopy CCF is reported as the source account divided by area. The source CCF
scale is not independently verified in this phase, so the number is a
comparative index, not a field canopy-cover measurement.

## What changed

- The baseline grows from the initial inventory for 30 years with no entry.
- Both selection regimes remove a large share of BA at the first entry. The
  low regime leaves about 25.7 m²/ha; the moderate regime leaves about
  27.6 m²/ha.
- Moderate produces about 5% less first-period volume than low, but leaves
  about 7.6% more residual BA and about 12% more feature yield.
- The two schedules are materially distinct because every low-preferred block
  receives `GWM_LOW` and the moderate-preferred blocks receive
  `GWM_MODERATE` where that treatment is operable.

## Targets

The smoke target file has three zero-minimum targets. All three report `met` in
all runs:

- `product.yield.managed.total`
- `feature.yield.managed.total`
- `feature.habitat.basal_area`

These statuses verify wiring, not policy performance. A zero minimum cannot
distinguish a good regime from a poor one.

## Mule-deer structural indicators

Available and reported:

- basal area;
- quadratic mean diameter;
- trees per hectare;
- canopy CCF account.

Not available and therefore not reported as habitat tests:

- large-tree basal area;
- reserve basal area;
- species-split softwood/hardwood structure;
- maximum DBH;
- q-factor;
- spatial clump and interlocking-crown geometry;
- seral/opening area.

The available indicators are necessary context, not a GWM 2007 compliance test.

## Calibrated, assumed, deferred

| Class | Content |
| --- | --- |
| Calibrated to KC | none |
| Assumed | VRI projected ages; PSP-derived IDF Cariboo space-for-time curves; 100-year feature horizons; 30-year product horizons; GWM treatment windows and target-track wiring |
| Deferred | KC CFI calibration; legal UWR/order verification; large-tree/reserve/seral/species accounts; route configuration; full scenario optimization |

## Evidence

- `ws4/evidence/kc_v1/scenario_manifest.json`
- `ws4/evidence/kc_v1/scenario_reports/`
- `ws4/runtime/kc_v1/baseline_no_cut/report/report_targets.csv`
- `ws4/runtime/kc_v1/selection_gwm_low/report/report_targets.csv`
- `ws4/runtime/kc_v1/selection_gwm_moderate/report/report_targets.csv`
- `ws4/evidence/kc_v1/coverage_audit.json`
- `ws4/evidence/kc_v1/integrity_audit.json`
