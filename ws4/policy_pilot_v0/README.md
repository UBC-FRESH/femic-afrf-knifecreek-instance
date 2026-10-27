# Veteran / large-tree retention policy pilot v0

Status: **structural policy pilot**. Not a compiled ws4 dataset and not an
approved MDWR policy.

## Purpose

The MDWR objective needs clumpy, closed-canopy, large-crown trees that intercept
snow. The economic objective wants the large-tree cash log value. This pilot
separates those two concerns and lets the model vary:

- the residual large-tree basal area above a threshold (4, 6 or 8 m²/ha at
  50 cm+);
- the treatment method: retain every tree above the habitat maximum DBH, or
  remove surplus large trees and then thin the small-tree component;
- the clump-size assumption (2–5 trees per clump).

## Policies

| Policy | Method | Large-tree target |
| --- | --- | --- |
| `RETAIN_ABOVE_D` | Full-range BDq up to the habitat maximum DBH | Retain all trees above D |
| `LT4_50` | `THINABA` surplus at 50 cm+ to 4 m²/ha, then `THINQFA` 0–50 cm to B−4 | 4 m²/ha at 50 cm+ |
| `LT6_50` | Same split to 6 m²/ha | 6 m²/ha at 50 cm+ |
| `LT8_50` | Same split to 8 m²/ha | 8 m²/ha at 50 cm+ |

The split policies use the Table 29 B and q for the small component and keep the
large-tree target as an explicit policy variable.

## Data and runs

- Source stands: `PSP-REG-004` (QMD 24, BA 29.4) and `PSP-REG-005` (QMD 26,
  BA 29.2) from the PSP-derived conditional lists.
- Three Table 29 regimes × four policies × two stands = 24 transitions.
- One 30-year entry per transition (`TIMEINT=,10`, `NUMCYCLE=4`, cycle 4).
- Corrected BC THINQFA units; `THINABA` target BA is m²/ha and its DBH fields
  are cm.

## Results

From `benchmark.csv`:

| Regime | Policy | Mean post BA | Mean post q | Mean large BA | Mean large TPH | Clump count/ha | Clump cover proxy |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| High | RETAIN_ABOVE_D | 37.5 | 1.250 | 7.27 | 23.4 | 7.8 | 12.0% |
| High | LT4_50 | 27.0 | 1.322 | 4.00 | 17.9 | 6.0 | 7.9% |
| High | LT6_50 | 28.0 | 1.240 | 6.00 | 25.4 | 8.5 | 11.3% |
| High | LT8_50 | 28.0 | 1.270 | 8.00 | 32.2 | 10.7 | 14.8% |
| Moderate | RETAIN_ABOVE_D | 34.5 | 1.250 | 15.41 | 48.5 | 16.2 | 25.3% |
| Moderate | LT4_50 | 22.0 | 1.250 | 4.00 | 17.9 | 6.0 | 7.9% |
| Moderate | LT6_50 | 22.0 | 1.250 | 6.00 | 25.4 | 8.5 | 11.3% |
| Moderate | LT8_50 | 22.0 | 1.250 | 8.00 | 32.2 | 10.7 | 14.8% |
| Low | RETAIN_ABOVE_D | 31.0 | 1.300 | 15.59 | 49.4 | 16.5 | 25.8% |
| Low | LT4_50 | 16.0 | 1.300 | 4.00 | 17.9 | 6.0 | 7.9% |
| Low | LT6_50 | 16.0 | 1.300 | 6.00 | 25.4 | 8.5 | 11.3% |
| Low | LT8_50 | 16.0 | 1.300 | 8.00 | 32.2 | 10.7 | 14.8% |

Interpretation:

- The split policies meet the total BA target (Low/Moderate exactly; High
  27–28 vs 29) while holding the large-tree BA at 4/6/8.
- `RETAIN_ABOVE_D` leaves much more total BA, especially at Low, because it
  protects every tree above D. It is the highest large-tree retention and the
  highest residual BA.
- The q factor is close to Table 29 for all policies; the High LT4 case is
  slightly above at 1.322.
- Clump count and crown-cover proxy scale with the large-tree target. These are
  **post-processing proxies**, not a spatial clump design or a snow model.

## What this does and does not establish

Establishes:

- A policy axis that varies large-tree retention independently of the total
  Table 29 B/q target.
- `THINABA` + `THINQFA` can produce a target large-tree BA and a target total B
  in the same entry.
- The trade-off between large-tree retention and total residual BA is visible.

Does not establish:

- a spatial clump layout or a physical snow-interception model;
- a legal UWR compliance claim;
- KC calibration;
- a preferred policy. The policy levels are scenario axes for the user to
  review.

## Files

- `transitions.csv` — 24 policy transitions with large-tree and clump metrics.
- `curves.csv` — 96 growth curves.
- `benchmark.csv` — the table above.
- `manifest.json` — source, policies, run hashes, caveats.
- Generator: `runbooks/build_policy_pilot.py`.
- Policy definitions: `config/retention_policies.yaml`.

## Reproduction

```bash
PYTHONPATH=/path/to/fresh-fvsbc/src \
  /path/to/fvsbc-build-venv/bin/python runbooks/build_policy_pilot.py \
  --sample data/psp/idf_cariboo_psp_conditional_stemlists.csv \
  --policies config/retention_policies.yaml \
  --out-dir ws4/policy_pilot_v0 \
  --runtime-dir runtime/policy_pilot_v0
```
