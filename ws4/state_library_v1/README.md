# KC state-transition library v1

Status: **provisional GWM 2007 clump-reserve library**. Not a compiled ws4
dataset, not KC-calibrated, and not a legal-compliance product.

## What is here

| File | Purpose |
| --- | --- |
| `states.csv` | 72 initial and residual states; state IDs carry the regime and entry. |
| `transitions.csv` | 48 entries: 8 initial stands × 3 GWM classes × 2 entries. |
| `curves.csv` | 192 interval curves: BA, QMD, TPH, volume, canopy CCF. |
| `benchmark.csv` | Post-mark BA, large-tree BA, reserve, q, max DBH and pass count. |
| `graph.json` | 72 nodes and 48 edges; residual states are terminal. |
| `manifest.json` | Provenance, run hashes, counts and caveats. |

## Method

1. Run a GWM full-range BDq cut at year 30 (`THINQFA` to D and B).
2. Apply the selected clump-reserve marking rule to the after-treatment list:
   group trees ≥37.5 cm into DBH-ranked chunks of six, reserve the largest
   three above D, and harvest the remaining trees above D.
3. Resample the weighted residual list to a one-hectare population.
4. Grow the residual population for a second 30-year entry and repeat.

The clump proxy is **non-spatial**. It is a placeholder for a real spatial
4–10-tree clump when KC stem maps or CFI arrive.

## Benchmark

| Regime | n | Mean post BA | Mean large BA | Mean reserve >D | Mean q | Mean max DBH | Mean clump removal | Pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| High | 16 | 29.43 | 16.60 | 0.43 | 1.271 | 72.8 | 0.37 | 10/16 |
| Moderate | 16 | 24.10 | 13.73 | 2.14 | 1.279 | 73.0 | 2.01 | 11/16 |
| Low | 16 | 20.42 | 10.55 | 4.51 | 1.323 | 73.1 | 4.36 | 12/16 |

**33/48 stand-structure checks pass.** The library is a structural pilot; the
failures are retained as evidence, not hidden.

## What this establishes

- The selected clump-reserve rule can be carried through two GWM entries.
- The residual list can be resampled and grown again in FVS-BC.
- The GWM basis, target checks and clump metadata are recorded per transition.

## What it does not establish

- Legal compliance. `legal_compliance` is false on every row.
- A spatial clump or canopy-opening layout.
- KC calibration or KC field-condition performance.
- A closed state graph. The 72 state IDs are per stand/regime/entry; they are
  not canonical shared states.
- Anything about the HMZ spatial matrix.

## Canonical graph

`canonical/` maps the 72 per-chain states to 23 shared BA/QMD/large-tree/reserve
classes: 25 aggregated transitions, 500 curve rows, 6 terminal states and 0
cycles. The graph is terminal-closed, not cycle-closed. See
`canonical/README.md`.

## Next

1. Compile a synthetic ws4 dataset from the canonical graph and run
   `ws4 validate`.
2. Replace the DBH-ranked six-tree proxy with a spatial clump rule when KC stem
   maps or CFI arrive.
3. Add the HMZ spatial constraint.
4. Replace the synthetic dataset with a KC-calibrated compile.
