# Phase 4 close-out report: verification and scenarios

Phase: P4 verification and scenarios
Parent issue: #70
Pull request: #75
Branch: `feature/p4-verification` into `main`
Evidence head: `e603408`, plus the P4.3/P4.4 commits
Date: 2026-10-30
Status: queued for approval. Not merged.

## Recommendation

Approve these actions. The agent carries them out in this order and reads back
each result.

1. Squash-merge the P4 pull request and delete the branch
   `feature/p4-verification`.
2. Close parent issue #70 with a closeout comment citing the merge commit.
3. Launch P5: create its branch, set its roadmap status, create its child
   issues, and start P5.1.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| Every block maps to a state and an AU | `ws4/evidence/kc_v1/coverage_audit.json`; 160/160 blocks, AU=1 | met |
| Area coverage | 3,481.773591 ha across fragments, blocks, recipe and source | met |
| Reachable-state accounting | 19 reachable tracks; 92 source tracks; 73 unreachable scaffold combinations | met |
| Group coverage | 12 groups; HMZ/clump/reserve membership for every block | met |
| Transition targets valid | `ws4/evidence/kc_v1/integrity_audit.json`; 19/19 | met |
| Curve integrity | 651 compiled curves; 650 source curves reproduce; all references resolve | met |
| No clearcut | treatment labels `GWM_LOW`, `GWM_MODERATE`; no `CC` | met |
| Baseline run | `baseline_no_cut`, 30 years | met |
| Two selection regimes | `selection_gwm_low`, `selection_gwm_moderate` | met |
| Reports for all runs | committed evidence under `ws4/evidence/kc_v1/scenario_reports/` | met |
| Scenario comparison | `notes/reports/p4-scenario-comparison.md` | met |
| Mule-deer indicators | BA, QMD, TPH and canopy CCF reported; large-tree/reserve/seral explicitly unavailable | met with a stated limit |
| Calibrated KC growth | none | not claimed |
| Legal compliance | no current order/legal verification | not claimed |

## 2. Coverage evidence

- Blocks: 160
- Fragments: 160
- Recipe fragments: 160
- Source fragments: 160
- Topology blocks: 160
- Topology pairs: 500
- AU values: 1
- Reachable tracks: 19
- Source scaffold tracks: 92
- Unreachable scaffold tracks: 73
- Groups: 12
- Group memberships: 800
- Area reconciliation: 3,481.773591 ha

The 73 unreachable scaffold tracks are source combinations that no current
fragment reaches through the treatment transitions. They are not silently
dropped from a model that should contain them; they are not reachable from the
inventory.

## 3. Integrity evidence

- Compiled curve ids: 651
- Source curve ids: 650 plus `unity`
- Curves checked against source: 650
- Curve domains strictly increasing: yes
- Feature references resolved: yes
- Product references resolved: yes
- Treatment targets resolved: 19/19
- Clearcut treatment: none
- Strata cycle: normalized to the source 30-year cycle
- Treatment labels: `GWM_LOW`, `GWM_MODERATE`

## 4. Scenario results

| Run | Scheduled blocks | Product yield (m³) | Residual BA (m²/ha) | Residual QMD (cm) | Residual TPH | Feature yield account |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline no cut | 0 | 0 | 67.44 | 41.74 | 506.2 | 2,725,752 |
| GWM low | 157 | 575,068 | 25.65 | 32.60 | 311.8 | 806,922 |
| GWM moderate | 157 | 546,223 | 27.62 | 33.01 | 328.5 | 902,941 |

The comparison is structural. Moderate leaves more residual BA and feature
yield than low, while producing about 5% less first-period volume. All three
smoke targets are zero-minimum wiring checks; their `met` status is not a
policy result.

## 5. Mule-deer statement

Reported: basal area, QMD, TPH and the canopy CCF account.

Not available and not substituted: large-tree BA, reserve BA, maximum DBH,
q-factor, species split, spatial clump/interlocking-crown geometry, and seral
or opening area. The available indicators do not constitute a GWM 2007 legal
test.

## 6. Calibrated, assumed and deferred

| Class | Content |
| --- | --- |
| Calibrated to KC | none |
| Assumed | VRI projected age; PSP-derived IDF Cariboo space-for-time curves; 100-year feature horizons; 30-year product horizons; source GWM treatment windows |
| Deferred | KC CFI calibration; legal UWR/order verification; large-tree/reserve/seral/species accounts; route configuration; full scenario optimization |

## 7. Gate evidence

| Gate | Status |
| --- | --- |
| lint | green |
| format | green |
| types | green |
| tests | green |
| validator | green |
| docs | green |

`python scripts/dashboard.py` reports `OVERALL: GREEN` at the evidence head.

## 8. Deviations and limits

| Item | Status |
| --- | --- |
| Large-tree and reserve features | unavailable; not fabricated |
| Seral/opening feature | unavailable; patch account remains managed area |
| Species split | unavailable |
| Route configuration | explicitly unavailable |
| Product horizon | 30 years |
| Feature horizon | 100 years, space-for-time |
| KC calibration | not done |
| Legal compliance | not claimed |
| Optimizer / full scenario study | not run |

## 9. Evidence files

- `notes/reports/p4-scenario-comparison.md`
- `notes/reports/p4-closeout.md`
- `ws4/evidence/kc_v1/coverage_audit.json`
- `ws4/evidence/kc_v1/integrity_audit.json`
- `ws4/evidence/kc_v1/scenario_manifest.json`
- `ws4/evidence/kc_v1/scenario_reports/`
- `runbooks/audit_kc_coverage.py`
- `runbooks/audit_kc_integrity.py`
- `runbooks/normalize_kc_strata.py`
- `runbooks/run_kc_scenarios.py`

## 10. Next phase

P5 is the v0.1 release: tag, release notes, and a clean-checkout verification.
P5 does not turn the structural model into a calibrated or legal-compliance
model.

## 11. Decision

- [ ] Approve as written.
- [ ] Approve with changes stated here: <changes>.
