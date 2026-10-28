# KC state-transition library v0

Status: **legacy Table 29 structural pilot**. This is a transition library, not
a compiled ws4 dataset and not the default GWM 2007 basis. The legal default is
GWM 2007; see `../../notes/adr/0005-mdwr-legal-basis.md`. The next library is
`state_library_v1` with `basis=GWM_2007`.

## What is here

| File | Purpose |
| --- | --- |
| `states.csv` | Initial and residual structural states. |
| `transitions.csv` | 48 selection entries: 8 initial states × 3 regimes × 2 entries. |
| `curves.csv` | 192 interval curves: BA, QMD, TPH, volume, canopy CCF. |
| `graph.json` | Nodes and edges for the v0 graph. |
| `benchmark.csv` | Residual BA, q, maximum DBH and cut yield by regime. |
| `manifest.json` | Provenance, run hashes, counts and caveats. |

## Source states

Eight PSP-derived IDF Cariboo stands spanning BA 20.8–38.5 m²/ha and QMD
16.8–22.2 cm. These are regional analogs, not Knife Creek data.

Regimes: `SEL_MDWR_HIGH`, `SEL_MDWR_MODERATE`, `SEL_MDWR_LOW`, from MWP #3
Table 29. These are the AFRF alternative, not the legal GWM curve. All entries use the corrected BC `THINQFA` units (cm for DBH fields,
ft²/ac for residual density) and two 30-year entries (`TIMEINT=,10`,
`NUMCYCLE=10`, `THINQFA` at cycles 4 and 7).

## Benchmark result

| Regime | Target post BA | Mean post BA | Mean abs BA error | Within ±2 | Target q | Mean post q |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| High | 29 | 33.31 | 4.31 | 6/16 | 1.25 | 1.284 |
| Moderate | 22 | 29.19 | 7.19 | 3/16 | 1.25 | 1.255 |
| Low | 16 | 25.94 | 9.94 | 0/16 | 1.30 | 1.296 |

The q values are close to the Table 29 targets. The residual BA is **above**
the targets, especially for Low. The mean residual maximum DBH is about
73.6 cm, above the 60/55/50 cm target, because `THINQFA` removes only trees up
to the specified maximum DBH and the source stands contain larger trees. This
is a structural limitation of applying Table 29 to these PSP stands, not
evidence that Table 29 is wrong.

## What this does and does not establish

Establishes:

- FVS-BC can run the three reviewed selection regimes on PSP-derived stands.
- Cut lists, after-treatment lists and summary curves are populated for two
  30-year entries.
- The q factor of the residual stands is close to Table 29.
- Residual BA and maximum DBH can exceed the targets; the benchmark records
  the gap.

Does not establish:

- a closed state graph; the six residual states are terminal in v0;
- a compiled ws4 dataset (`fragments`, `blocks`, `tracks`, `treatments`,
  `features`, `products` are not built);
- KC calibration, legal UWR compliance, or spatial habitat assignment;
- that Table 29 is achieved from these starts.

## Reproduction

```bash
PYTHONPATH=/path/to/fresh-fvsbc/src \
  /path/to/fvsbc-build-venv/bin/python runbooks/build_state_library.py \
  --sample data/psp/idf_cariboo_psp_stemlist_sample.csv \
  --out-dir ws4/state_library_v0 \
  --runtime-dir runtime/state_library_v0
```

The raw FVS run directories stay under `runtime/` and are not committed.
