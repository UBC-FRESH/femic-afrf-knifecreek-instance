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
- reserve BA ceiling (Moderate 2.2, Low 1.6, High 2.9 m²/ha).

The target file excludes max DBH, q-factor, spatial 4–10-tree clumps, canopy
openings and pre-2026 80% retention because the model does not yet carry those
tests.

## Result on the stage runs

After switching the FVS entries from `THINQFA` alone to the documented split
cut (`THINABA` above 37.5 cm, then `THINQFA` on the small-tree component):

GWM low:

- 37 of 55 targets met
- 8 below (mostly q-factor)
- 10 reserve-ceiling failures
- total-BA and large-tree-BA floors met

GWM moderate:

- 39 of 55 targets met
- 10 below (mostly q-factor and max DBH)
- 6 reserve-ceiling failures
- total-BA and large-tree-BA floors met

The failures are concentrated in the non-spatial reserve proxy, especially
HMZ L and several Moderate groups. The proxy reserves too much above D for the
legal ceilings.

## Not tested / not compliant

- Maximum DBH is now tested and fails in some groups.
- q is now tested and is below the legal range in several groups.
- Spatial clumps of 4–10 mature trees with interlocking crowns.
- Canopy openings 0.3–1.0 tree heights, mean 0.5.
- Pre-2026 retention of ≥80% of pre-harvest merchantable Douglas-fir BA.
- Current approved UWR order and legal HMZ/stand-structure map.
- Skid-trail and residual-damage checks.

## Consequence

Do not present the current model or the candidate target run as legal
compliance. The next steps are: replace the reserve proxy with a rule that
meets the legal ceiling, add max DBH and q accounts, add spatial clump/opening
checks, add the 80% retention test, and verify the current order and spatial
layer.
