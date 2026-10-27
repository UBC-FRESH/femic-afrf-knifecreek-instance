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
- the clump-size assumption. GWM 10 requires 4–10 or more mature trees with
  interlocking crowns; the 2–5 figure is only the maximum-diameter subgroup.

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
- The policy pilot uses a 50 cm large-tree threshold and Table 29 D values. It
  is a structural policy axis, not the legal GWM basis. The legal order uses
  BA >37.5 cm and D ≥70/60/50 for High/Moderate/Low; see
  `../../notes/reference/mdwr-canopy-clump-requirements.md`.

## Results

From `benchmark.csv`:

| Regime | Policy | Mean post BA | Mean post q | Mean large BA | Mean large TPH | Clump count/ha | Clump cover proxy |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| High | RETAIN_ABOVE_D | 37.5 | 1.250 | 14.54 | 46.7 | 7.8 | 24.0% |
| High | LT4_50 | 27.0 | 1.322 | 4.00 | 17.9 | 3.0 | 7.9% |
| High | LT6_50 | 28.0 | 1.240 | 6.00 | 25.4 | 4.2 | 11.3% |
| High | LT8_50 | 28.0 | 1.270 | 8.00 | 32.2 | 5.4 | 14.8% |
| Moderate | RETAIN_ABOVE_D | 34.5 | 1.250 | 15.41 | 48.5 | 8.1 | 25.3% |
| Moderate | LT4_50 | 22.0 | 1.250 | 4.00 | 17.9 | 3.0 | 7.9% |
| Moderate | LT6_50 | 22.0 | 1.250 | 6.00 | 25.4 | 4.2 | 11.3% |
| Moderate | LT8_50 | 22.0 | 1.250 | 8.00 | 32.2 | 5.4 | 14.8% |
| Low | RETAIN_ABOVE_D | 31.0 | 1.300 | 15.59 | 49.4 | 8.2 | 25.8% |
| Low | LT4_50 | 16.0 | 1.300 | 4.00 | 17.9 | 3.0 | 7.9% |
| Low | LT6_50 | 16.0 | 1.300 | 6.00 | 25.4 | 4.2 | 11.3% |
| Low | LT8_50 | 16.0 | 1.300 | 8.00 | 32.2 | 5.4 | 14.8% |

Interpretation:

- The split policies meet the total BA target (Low/Moderate exactly; High
  27–28 vs 29) while holding the large-tree BA at 4/6/8.
- `RETAIN_ABOVE_D` leaves much more total BA, especially at Low, because it
  protects every tree above D. It is the highest large-tree retention and the
  highest residual BA. The High mean is from one after-treatment tree list;
  the second High case had no cut and no after-treatment list, so its large-tree
  metrics are not in the mean.
- The q factor is close to Table 29 for all policies; the High LT4 case is
  slightly above at 1.322.
- Clump count and crown-cover proxy scale with the large-tree target. These are
  **post-processing proxies**, not a spatial clump design or a snow model.

## Clump geometry scenarios

`clump_scenarios.csv` and `clump_scenario_summary.csv` add a spatial geometry
layer. The large-tree TPH from each transition is placed in **4, 6, 8 or 10**
tree clumps on a ring of 3, 5 or 7 m radius; within-clump cover is rasterized
at 0.25 m. GWM 10 requires 4–10 or more mature trees with interlocking crowns,
so 4–10 is the legal clump range. The maximum-diameter subgroup can still be
2–5 trees within the clump.

High regime, `LT8_50`, six-tree clumps:

| Clump radius | Clumps/ha | Mean spacing | Within-clump closure | Closed clumps | Total cover |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 3 m | 5.4 | 43.2 m | 0.931 | 100% | 7.5% |
| 5 m | 5.4 | 43.2 m | 0.863 | 100% | 12.3% |
| 7 m | 5.4 | 43.2 m | 0.725 | 100% | 17.9% |

High regime, `LT8_50`, 3 m clump radius, varying clump size:

| Clump size | Clumps/ha | Mean spacing | Within-clump closure | Closed clumps | Total cover |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 8.0 | 35.3 m | 0.855 | 100% | 11.1% |
| 6 | 5.4 | 43.2 m | 0.931 | 100% | 7.5% |
| 8 | 4.0 | 49.9 m | 0.959 | 100% | 5.7% |
| 10 | 3.2 | 55.8 m | 0.975 | 100% | 4.6% |

The previous 2–5 tree pilot was a misreading: 2–5 trees is the maximum-diameter
subgroup in MWP #3, not the whole clump. With the legal 4–10 tree clumps,
within-clump closure is high (0.86–0.98 at 3 m) even though total stand cover
is lower. The geometry is still a scenario, not an empirical clump
distribution, and the canopy openings required by GWM 10 are not yet
spatialized.

## What this does and does not establish

Establishes:

- A policy axis that varies large-tree retention independently of the total
  Table 29 B/q target.
- `THINABA` + `THINQFA` can produce a target large-tree BA and a target total B
  in the same entry.
- The trade-off between large-tree retention and total residual BA is visible.

Does not establish:

- an actual spatial clump layout, canopy-opening layout, or physical
  snow-interception model;
- a legal UWR compliance claim;
- KC calibration;
- a preferred policy. The policy levels are scenario axes for the user to
  review.

## Files

- `transitions.csv` — 24 policy transitions with large-tree metrics.
- `curves.csv` — 96 growth curves.
- `benchmark.csv` — the policy table above.
- `clump_scenarios.csv` — 276 clump geometry scenarios (4–10 tree clumps).
- `clump_scenario_summary.csv` — grouped clump geometry table.
- `manifest.json` — source, policies, run hashes, caveats.
- Generators: `runbooks/build_policy_pilot.py` and
  `runbooks/build_clump_scenarios.py`.
- Policy definitions: `config/retention_policies.yaml`.
- PSP stem-map limit note: `notes/reference/psp-stem-map-limits.md`.

## Reproduction

```bash
PYTHONPATH=/path/to/fresh-fvsbc/src \
  /path/to/fvsbc-build-venv/bin/python runbooks/build_policy_pilot.py \
  --sample data/psp/idf_cariboo_psp_conditional_stemlists.csv \
  --policies config/retention_policies.yaml \
  --out-dir ws4/policy_pilot_v0 \
  --runtime-dir runtime/policy_pilot_v0
python runbooks/build_clump_scenarios.py \
  --transitions ws4/policy_pilot_v0/transitions.csv \
  --out-dir ws4/policy_pilot_v0
```
