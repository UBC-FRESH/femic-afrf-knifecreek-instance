# KC legal-compliance audit

Status: **not compliant**. This is a legal-candidate structural check.

## Basis

GWM 2007 is the default legal basis. Knife Creek is U-5-002 `dwl_50` with
HMZ 1 M, 2 L, 3 M, 4 M, 5 A. The current approved order and legal spatial
layer still require verification.

## What was tested

`ws4/targets_kc_gwm2007_legal_candidate.yaml` checks, by AU/HMZ:

- total BA minimum (Moderate 22, Low 16 m²/ha);
- large-tree BA minimum (Moderate 11, Low 6 m²/ha above 37.5 cm);
- maximum DBH minimum (Moderate 60, Low 50 cm);
- q-factor range (Moderate 1.25–1.35, Low 1.25–1.40);
- reserve BA ceiling (Moderate 2.2, Low 1.6 m²/ha above D).

The target file does not yet test spatial 4–10-tree clumps, canopy openings,
pre-2026 80% Douglas-fir retention or the current approved order.

## Treatment tested

The AU multi-entry runs use a three-part legal-candidate cut at each entry:

1. `THINABA` from 37.5 cm to D, removing surplus large trees to the legal
   large-tree minimum.
2. `THINABA` above D, removing surplus reserve trees to the legal reserve
   ceiling.
3. `THINQFA` from 2.5–37.5 cm, leaving the small-tree component.

The `THINQFA` q target is calibrated per AU so the independently measured 5 cm
q lands inside the legal range. The overrides are:

| AU | Regime | FVS q target |
|---|---|---|
| `KC_IDFdk3_FDI_H` | Low | 1.60 |
| `KC_IDFdk3_FDI_H` | Moderate | 1.66 |
| `KC_IDFxm_FDI_L` | Moderate | 1.38 |

All other AU/regime pairs use 1.55 (Low) or 1.50 (Moderate). These are FVS
targets, not legal q values. The measured q is calculated independently from
the FVS tree list.

## Result

The legal-candidate scenario is HMZ-mixed: M/A Moderate, L Low, U no harvest.
It is `selection_gwm_legal` under `ws4/runtime/kc_au_stages`.

Legal-candidate run:

- **55 of 55** structural targets met.
- Total BA, large-tree BA, maximum DBH, q and reserve ceilings all pass.

This is a structural pass only. It does not certify legal compliance.

A calibrated sensitivity using the v1 PSP `BAIMULT`/`MORTMULT` parameters
meets 45/55 targets: 5 above and 5 below, with reserve-ceiling and q-factor
misses. The calibrated growth is more conservative and moves the structural
targets. See `notes/reports/kc-au-calibrated-sensitivity.md`. The uncalibrated
run remains the structural baseline.

## Not tested / not compliant

- Spatial clumps of 4–10 mature trees with interlocking crowns.
- The 2–5-tree maximum-diameter subgroup inside each clump.
- Canopy openings 0.3–1.0 tree heights, mean 0.5.
- Pre-2026 retention of ≥80% of pre-harvest merchantable Douglas-fir BA.
  A first-entry proxy is in `data/psp/kc_au_200y/kc_au_fir_retention_low.csv`
  and `..._moderate.csv`. Pooled first-entry retention is 0.39–0.79 under Low
  and 0.42–0.95 under Moderate; only one AU/regime group reaches 0.80. This is
  not yet a legal determination because the model has no calendar-2026 entry:
  if year 0 is 2026 and the first entry is after 2026, the pre-2026 rule is not
  triggered; if the first entry is the pre-2026 harvest, five of six AUs fail.
- Current approved UWR order and legal HMZ/stand-structure map.
- Skid-trail and residual-damage checks.
- KC-calibrated growth and mortality. The 2024 Marshall temporal holdout
  supports the v1 total-TPH calibration, but it is not independent-site or
  whole-block validation; the AU stage curves still use uncalibrated FVS.
- Independent validation of the AU-specific q target calibration.

## Consequence

Do not present the current model or the legal-candidate run as legal
compliance. The reserve account is a basal-area cap, not a spatial clump
check. The q pass depends on AU-specific FVS calibration and is not an
independent validation. The remaining work is to place and verify clumps and
openings, add the 80% retention test, verify the current order and spatial
layer, and calibrate growth to KC data.
