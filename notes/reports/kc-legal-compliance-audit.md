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

The AU multi-entry runs now use a three-part legal-candidate cut at each entry:

1. `THINABA` from 37.5 cm to D, removing surplus large trees to the legal
   large-tree minimum.
2. `THINABA` above D, removing surplus reserve trees to the legal reserve
   ceiling.
3. `THINQFA` from 2.5–37.5 cm, leaving the small-tree component.

The `THINQFA` target is calibrated so the independently measured 5 cm q lands
near the legal range: 1.55 for Low and 1.50 for Moderate. This is an FVS
target, not a legal q value.

## Result

The legal-candidate scenario is HMZ-mixed: M/A Moderate, L Low, U no harvest.
It is `selection_gwm_legal` under `ws4/runtime/kc_au_stages`.

Legal-candidate run:

- 52 of 55 targets met.
- 2 below: q in `KC_IDFdk3_FDI_H.L` and `KC_IDFdk3_FDI_H.M`.
- 1 above: q in `KC_IDFxm_FDI_L.M`.
- Total BA, large-tree BA, maximum DBH and reserve ceilings pass.

Global-regime comparisons:

- `selection_gwm_low`: 51 of 55 met; 3 below, 1 above.
- `selection_gwm_moderate`: 52 of 55 met; 2 below, 1 above.

The three remaining failures are marginal q-factor misses, not reserve or BA
failures.

## Not tested / not compliant

- Spatial clumps of 4–10 mature trees with interlocking crowns.
- The 2–5-tree maximum-diameter subgroup inside each clump.
- Canopy openings 0.3–1.0 tree heights, mean 0.5.
- Pre-2026 retention of ≥80% of pre-harvest merchantable Douglas-fir BA.
- Current approved UWR order and legal HMZ/stand-structure map.
- Skid-trail and residual-damage checks.
- KC-calibrated growth and mortality.

## Consequence

Do not present the current model or the legal-candidate run as legal
compliance. The reserve account is a basal-area cap, not a spatial clump
check. The remaining work is to place and verify clumps and openings, add the
80% retention test, verify the current order and spatial layer, and close the
three q-factor misses without using the q target as a compliance claim.
