# KC provisional AAC and harvest schedule

Status: **provisional model-based AAC**. This is a decision-support range, not a
statutory allowable annual cut and not a legal-compliance determination.

## Run

- Dataset: `ws4/dataset_kc_au_stages_v1` (uncalibrated baseline).
- Targets: `ws4/targets_kc_evenflow.yaml`.
- 20 × 10-year periods, 200-year horizon.
- 50,000-iteration simulated-annealing search, 16 threads.
- Initial schedule: the HMZ-mixed legal-candidate schedule.
- Output: `ws4/runtime/kc_aac_50k/`.
- Evidence: `ws4/evidence/kc_aac/uncalibrated/`.

## Provisional AAC

| Metric | Value |
| --- | ---: |
| Mean period harvest | 33,983 m³ / 10 years |
| Mean AAC | **3,398 m³/year** |
| Minimum period | 30,839 m³ / 10 years |
| Maximum period | 37,972 m³ / 10 years |
| AAC range across periods | **3,084–3,797 m³/year** |
| Total 200-year harvest | 679,658 m³ |

All twenty 27,000 m³/period floors are met. The ±5% even-flow band is **not**
met: the later periods fall about 9–19% below period 1. Target status is 24 met
and 17 below.

This is a real schedule, but it is not an even-flow AAC yet. It should be read
as a **provisional sustainable-volume range** of roughly 3,100–3,800 m³/year,
with a central value near 3,400 m³/year.

## Calibrated sensitivity

The same 50,000-iteration search on the v1-calibrated stage graph gives:

| Metric | Calibrated |
| --- | ---: |
| Mean AAC | 2,616 m³/year |
| Period range | 2,022–3,417 m³/year |
| 27,000 m³ floors | **not met in later periods** |
| Target status | 4 met, 37 below |

The calibrated growth model cannot sustain the 27,000 m³/period floor under the
current treatment set. This is a material finding: the uncalibrated AAC is
optimistic relative to the calibrated sensitivity, and the calibrated case
needs either a lighter treatment, a different entry cycle, or a lower floor.

## Schedule shape

The uncalibrated schedule has 201 entries across 110 blocks, with offsets from
0 to 199. It is a multi-entry selection schedule, not a one-time harvest. The
period volumes are in `aac_periods.csv`; the block-level schedule is
`schedule.csv`.

## Limits

- Uncalibrated FVS-BC growth is the structural baseline; the calibrated model
  is a sensitivity.
- The stage graph is not yet spatially constrained by the LiDAR clump/opening
  layer.
- Kozak merchantable volume is computed for the mapped plots but not yet applied
  to the FVS product curves.
- The AAC is not a statutory determination; the current order and HMZ layer
  still require verification.
- The even-flow band is not converged.

## Next

1. Apply the calibrated/v2c ensemble to the AAC range.
2. Add Kozak volume correction to the product curves.
3. Add the LiDAR clump/opening constraints to the stage graph.
4. Rerun the 50k search and report a converged even-flow range.
