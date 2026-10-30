# Phase 3 close-out report: ws4 instance assembly

Phase: P3 ws4 instance assembly
Parent issue: #60
Pull request: pending
Branch: `feature/p3-ws4-assembly` into `main`
Evidence head: `39438d3`, plus the P3.8 report commit
Date: 2026-10-30
Status: queued for approval. Not merged.

## Recommendation

Approve these actions. The agent carries them out in this order and reads back
each result.

1. Squash-merge the P3 pull request and delete the branch
   `feature/p3-ws4-assembly`.
2. Close parent issue #60 with a closeout comment citing the merge commit.
3. Launch P4: create its branch, set its roadmap status, create its child
   issues, and start P4.1.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| KC ForestModelXML recipe exists | `data/kc_ws4_recipe/forestmodel.xml`; SHA-256 in `ws4/dataset_kc_v1/manifest.json` | met |
| Matrix-builder fragments exist | `data/kc_ws4_recipe/fragments.csv`; 160 fragments | met |
| `ws4 build` compiles the recipe | `runbooks/run_kc_ws4_pipeline.py`; `Built dataset → ws4/dataset_kc_v1` | met |
| `ws4 validate` accepts the dataset | `Dataset is valid → ws4/dataset_kc_v1` | met |
| No-cut baseline runs | `ws4/runtime/kc_v1/baseline_no_cut` | met |
| Selection-smoke run runs | `ws4/runtime/kc_v1/selection_smoke` | met |
| Reports are written | `report/report_targets.csv` and `report/report_accounts.csv` in both runs | met |
| Web UI serves the model | `http://127.0.0.1:8766`; `/api/summary` returns `dataset_kc_v1` | met |
| Product and feature accounts resolve | `ws4/evidence/kc_v1/account_audit.json`; 0 issues | met |
| HMZ/clump/reserve group aggregation | `ws4/dataset_kc_v1/groups.parquet`; 12 groups, 800 memberships | met |
| Topology covers every block | `ws4/topology.csv`; 500 pairs, all 160 blocks | met |
| Roads present or explicitly unavailable | `data/patchworks_knifecreek/spatial/roads.gpkg` (44 sections, 59.6 km); route configuration explicitly unavailable | met with a stated limit |
| Patch membership runs | `ws4/runtime/kc_v1/selection_smoke/patch_accounts.csv`; 10 period rows | met |
| Large-tree, reserve, seral and species-split accounts | not present | not met; data gap, not fabricated |
| Legal compliance | no current approved order/spatial verification | not met; not claimed |

## 2. Compiled model counts

| Object | Count |
| --- | ---: |
| Fragments | 160 |
| Blocks | 160 |
| Reachable tracks/strata | 19 |
| Treatments | 19 |
| Curves (unique ids / points) | 651 / 6,661 |
| Feature rows | 114 |
| Product rows | 38 |
| Accounts | 8 |
| Group memberships (blocks × groups) | 800 |
| Groups | 12 |
| Topology pairs | 500 |
| Road sections | 44 |
| Road length | 59.6 km |

The source H scaffold has 92 tracks. The compiled matrix has 19 because the
WS4 matrix builder enumerates only strata reachable from the current inventory
and treatment transitions. The 92-track scaffold contains unreachable
combinations and is not a compiled-model count.

## 3. Run summaries

The smoke targets all have a zero minimum. Their `met` statuses are structural
checks, not management outcomes.

| Run | Product yield (m³) | Feature yield | Feature BA | Target status |
| --- | ---: | ---: | ---: | --- |
| Baseline no cut | 0 | 2,623,713 | 229,999 | 3 met |
| Selection smoke | 575,068 | 543,598 | 67,602 | 3 met |

Product values are the first-period selection output. Feature values are
whole-estate aggregates at the period end, so their units are not directly
comparable to the product total.

## 4. Gavin Lake functional comparison

Gavin Lake is the sibling legacy age-class instance. KC is an uneven-aged ws4
instance. The comparison is functional, not a claim that the two growth
surfaces are equivalent.

| Surface | Gavin Lake | Knife Creek P3 |
| --- | --- | --- |
| Compiled ws4 matrix | legacy H matrix | ForestModelXML-built matrix |
| Growth engine | legacy matrix | FVS-BC-derived source curves |
| Clearcut | part of the legacy regime | absent by design |
| Selection treatments | reference only | 19 selection treatment rows |
| Baseline run | established | `baseline_no_cut` |
| Selection run | established | `selection_smoke` |
| Reports | established | written |
| Web service | established | port 8766 |
| Topology / patches | established | 500 pairs, managed-area patch account |
| Calibrated KC growth | not applicable | no |
| Legal compliance | not applicable | no |

## 5. Gate evidence

| Gate | Status |
| --- | --- |
| lint | green |
| format | green |
| types | green |
| tests | green |
| validator | green (`ws4 validate`) |
| docs | green |

`python scripts/dashboard.py` reports `OVERALL: GREEN` at the evidence head.

## 6. Deviations and limits

| Item | Status |
| --- | --- |
| Large-tree BA feature | unavailable; no defensible per-track curve in the current source |
| Reserve BA feature | unavailable as a per-track curve; reserve classes are block groups only |
| Seral/opening feature | unavailable; patch account uses managed area |
| Species-split features/products | unavailable; source species data is not wired into the track curves |
| Route configuration | explicitly unavailable; no destination, eligibility, access or cost inputs |
| Product curve horizon | 30 years |
| Feature curve horizon | 100 years; space-for-time, not a KC chronology |
| Growth calibration | not calibrated to KC |
| Optimizer / full scenario study | not run in P3 |
| Legal compliance | not claimed |
| Patchworks runtime | not used; not a KC deliverable |

## 7. Evidence files

- `data/kc_ws4_recipe/forestmodel.xml`
- `data/kc_ws4_recipe/fragments.csv`
- `data/kc_ws4_recipe/manifest.json`
- `ws4/dataset_kc_v1/manifest.json`
- `ws4/evidence/kc_v1/pipeline_manifest.json`
- `ws4/evidence/kc_v1/account_audit.json`
- `ws4/runtime/kc_v1/baseline_no_cut/report/report_targets.csv`
- `ws4/runtime/kc_v1/selection_smoke/report/report_targets.csv`
- `ws4/topology.csv`
- `data/patchworks_knifecreek/spatial/roads_metadata.json`
- `data/patchworks_knifecreek/spatial/ROUTE_CONFIG_UNAVAILABLE.md`

## 8. Next phase

P4 verifies the model and compares selection regimes:

- verify area, AU and state coverage;
- verify the FVS-BC transition and growth curves;
- run the baseline and at least two selection regimes;
- record the scenario comparison and caveats.

P4 is not a calibrated-growth or legal-compliance phase. The missing
large-tree, reserve, seral and species accounts and the route configuration
carry forward as explicit gaps.

## 9. Decision

- [ ] Approve as written.
- [ ] Approve with changes stated here: <changes>.
