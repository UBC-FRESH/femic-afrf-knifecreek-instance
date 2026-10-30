# Phase 5 close-out report: release v0.1

Phase: P5 Release v0.1
Parent issue: #76
Pull request: #80
Branch: `feature/p5-release` into `main`
Release commit: `94a530051504d7ed90a90850115ca61c3da24834`
Tag: `v0.1.0`
Date: 2026-10-30
Status: released.

## Recommendation

Approve these actions. The agent carries them out in this order and reads back
each result.

1. Close parent issue #76 with this tag and release evidence.
2. Launch P6: create its branch, set its roadmap status, create its child
   issues, and start P6.1.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| Release notes match the evidence | `notes/reports/p5-release-notes.md`; P3/P4 evidence | met |
| Known gaps recorded | release notes, P3/P4 closeouts | met |
| Clean checkout builds ws4 | `/tmp/opencode/kc-clean`; `ws4 build` | met |
| Clean checkout validates | `ws4 validate` | met |
| Clean checkout dashboard | `python scripts/dashboard.py` | met |
| FVS-BC pilot reproduced | `fresh_fvsbc` not installed | not met; documented prerequisite |
| Tag and publish | `v0.1.0` on `94a5300`; GitHub release | met |
| No private raw data published | release contains derived/public artifacts only | met |
| No calibration or legal claim | release notes and closeouts | met |

## 2. Release evidence

- Version: `v0.1.0`
- Tag commit: `94a530051504d7ed90a90850115ca61c3da24834`
- GitHub release: https://github.com/UBC-FRESH/femic-afrf-knifecreek-instance/releases/tag/v0.1.0
- Release notes: `notes/reports/p5-release-notes.md`
- Clean-checkout report: `notes/reports/p5-clean-checkout.md`
- Clean-checkout transcript: `ws4/evidence/kc_v1/p5_clean_checkout.log`

## 3. Clean-checkout result

At commit `41b2ada`:

- dashboard green;
- `ws4 build` produced the recipe/fragment matrix;
- `ws4 validate` accepted the dataset;
- counts: 160 fragments, 160 blocks, 19 tracks, 19 treatments, 6,661 curve
  points, 114 features, 38 products, 8 accounts.

`fresh_fvsbc` is not installed in this environment. The FVS-BC pilot is a
release prerequisite, not a claimed successful run.

## 4. Known gaps

- KC calibration is absent.
- Large-tree BA, reserve BA, maximum DBH, q-factor, species split and
  seral/opening features are absent.
- Route configuration is unavailable.
- Legal UWR/order verification is not done.
- Feature curves are 100-year space-for-time; product curves are 30 years.
- The patch account is managed area, not seral/opening.
- Raw PSP field data remains private.

## 5. Gate evidence

| Gate | Status |
| --- | --- |
| lint | green |
| format | green |
| types | green |
| tests | green |
| validator | green |
| docs | green |

## 6. Decision

- [x] Approve as written.
- [ ] Approve with changes stated here: <changes>.
