# GWM 2007 legal-basis pilot v0

Status: **stand-structure feasibility test**, not a legal-compliance test and
not a compiled ws4 dataset.

## Purpose

Test the 2007 GWM legal targets on the five PSP-derived conditional stands. The
default GWM cut removes surplus large trees in the 37.5–D cm range to the legal
large-tree minimum, leaves trees above D as the reserve, and then thins 0–37.5
cm to `B − large-tree BA`. The retain-all-above-D method is a sensitivity.

The UWR/HMZ spatial layer is not tested. `legal_compliance` is false for every
row.

## Runs

Five stands × three GWM classes × two methods = 30 transitions, 120 curves.
One 30-year entry at cycle 4 (`TIMEINT=,10`, `NUMCYCLE=4`).

The default split cut for High is:

```text
THINABA  4, 16.0, 1.0, 37.5, 70.0, 0.0, 999.0
THINQFA  4, 0.0, 37.5, 0, 1.25, 5.0, 56.63
```

Low/Moderate use the same pattern with their own B, large-tree minimum, D and
q. The small-tree targets are 13/11/10 m²/ha, or 56.63/47.92/43.56 ft²/ac.

## Result

From `benchmark.csv`:

| Regime | Method | Mean post BA | Mean large BA | Mean large TPH | Mean q | Mean max DBH | Mean reserve >D | Pass |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| High | retain above D | 31.0 | 18.24 | 88.2 | 1.269 | 88.8 | 2.62 | 3/5 |
| High | split 37.5–D | 30.4 | 17.82 | 90.6 | 1.383 | 88.8 | 2.62 | 1/5 |
| Moderate | retain above D | 27.2 | 16.97 | 79.7 | 1.250 | 88.8 | 5.75 | 5/5 |
| Moderate | split 37.5–D | 27.2 | 16.75 | 84.8 | 1.444 | 88.8 | 5.75 | 0/5 |
| Low | retain above D | 26.2 | 16.42 | 74.7 | 1.300 | 88.8 | 10.67 | 5/5 |
| Low | split 37.5–D | 26.2 | 16.67 | 80.2 | 1.369 | 88.8 | 10.67 | 3/5 |

Overall: **17/30** pass the four stand-structure checks (total BA, large-tree
BA, max DBH, q). Retain above D passes 13/15; the D-protected split passes
4/15.

The failures are informative:

- High `PSP-REG-001` has only 12.4 m²/ha above 37.5 cm and max DBH 65.7 cm.
  It fails the High large-tree and D targets under both methods. The starting
  stand cannot meet the High legal structure.
- High `PSP-REG-002` has 15.7 m²/ha above 37.5 cm under retain, just below 16.
- The D-protected split preserves max DBH but leaves the >D reserve. That
  reserve makes the residual q too high in most Moderate and High cases:
  mean 1.44 and 1.38 against upper limits 1.35.
- A full-range split (removing above D) was tested earlier. It can meet q and
  B, but it strips the largest trees and leaves max DBH below the legal D
  floor. That is not acceptable for a legal-basis run.
- The mean reserve above D is 2.62/5.75/10.67 m²/ha, above the Table 2
  recommended ranges 0–2.9/0–2.2/0–1.6. The source stands carry more >D
  structure than the legal curve assumes.

## Interpretation

The FVS keyword set can preserve D or harvest surplus large trees, but not
selectively retain a small number of >D reserve trees while harvesting the
rest. That requires a tree-level reserve/marking rule in the treatment design,
or a post-processing step that assigns a reserve before the FVS cut. A simple
`THINABA` above 37.5 cm cannot do it.

Do not compile this pilot as a legal-compliant state library. The next step is
a treatment design with an explicit **D reserve** (for example, retain the
largest 2–5 trees per clump or a prescribed >D BA) and then test the q and
total-B outcomes.

## Files

- `transitions.csv` — 30 stand-structure transitions.
- `curves.csv` — 120 growth curves.
- `benchmark.csv` — grouped result table.
- `manifest.json` — source, runs, caveats.
- Generator: `runbooks/build_gwm_pilot.py`.
- Legal target contract: `config/mdwr_regimes.yaml`, `config/fvsbc/regimes.yaml`.
