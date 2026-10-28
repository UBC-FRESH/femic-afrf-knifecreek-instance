# THINQFA synthetic pilot

## Purpose

Settle the `THINQFA` entry-cycle semantics and check the BC unit convention
before the KC stem list exists. This is a synthetic structural test, not a KC
growth-and-yield calibration.

## Environment

- `fresh-fvsbc` `0.12.0`, commit `d86e78b0fc31386684aae1a0a1a9a821c0ee2baf`.
- Built `FVSbc` variant from the PyFVS fork, `pyfvs.list_variants()` reports
  `{'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}`.
- One plot, one stand, 400 trees: 100 each at 22, 32, 42 and 52 cm DBH.
- Height `1.3 * DBH^0.55` m, crown ratio 0.45, tree age 60.
- `SITECODE=FD,60`; `THINQFA` target `126.32` ft²/ac (29 m²/ha), maximum DBH
  60 cm, q 1.25, class width 5 cm, supplemental unit `0` (BA/ac).
- `TIMEINT=,30`, `NUMCYCLE=2`, `THINQFA` at cycle 2.
- Output block: `DSNOut`, `FVSOut.db`, `TreeLIDB`, `CutLIDB`, `ATRTLIDB`,
  `Summary`.

## Result: cycle 2 cuts at year 30

`FVS_Summary_Metric`:

| Year | TPH | BA (m²/ha) | ATBA (m²/ha) | Removed TPH | Removed m³/ha |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 400 | 46 | 46 | 0 | 0 |
| 30 | 358 | 53 | 35 | 91 | 93 |
| 60 | 247 | 40 | 40 | 0 | 0 |

`FVS_CutList_Metric` has one cut year, **30**, with 90.47 trees/ha removed at a
mean DBH of 46.96 cm. Cycle 2 with a 30-year period is therefore the entry
after the first 30-year growth interval; cycle 1 is the year-0 entry.

A second run with `TIMEINT=,10` and `NUMCYCLE=4`, `THINQFA` at cycle 4, also
cuts at year 30 (pre-cut BA 53 m²/ha, post-cut 31 m²/ha). The cycle number is
the start of the named cycle, not a lag from the previous entry.

## Result: inches do not work in BC

The same run with the diameter fields written as inches
(`max 23.62`, `class width 1.97`) was cancelled. `run.out` reports:

```text
THINQFA    DATE/CYCLE=    1; MINIMUM      0.0; MAXIMUM     23.6
...
SUMINV,CTAR,LDELQFA=    13.6850300       126.320000     F
...
BASE     THINQFA      1  DELETED OR CANCELED
```

The BC variant's `initre.f` multiplies fields 2, 3 and 6 by `CMtoIN` before the
cut. `23.62` was therefore read as 23.62 cm, or 9.30 in, which excluded the
30–52 cm trees; the eligible BA was 13.685 ft²/ac, below the 126.32 target, and
the activity was cancelled. The KC templates now store those three fields in
centimetres.

## Figure 11 High shape

A second synthetic stand used the recovered Figure 11 High density by 5 cm
class (593 trees/ha, initial BA 29 m²/ha). After 30 years the stand was
37 m²/ha; `THINQFA` removed 5.7 trees/ha and left 36 m²/ha, not the 29 m²/ha
target. The uniform/q-deficit shape in the grown stand limits what the
q-target can remove. This is a real structural caveat: the target is not
guaranteed from every initial distribution. It is not evidence that the KC
target is wrong.

## What this does and does not establish

Establishes:

- the BC unit convention for fields 2, 3 and 6;
- the entry cycle: 1 = year 0, 2 with a 30-year period = year 30;
- that a `THINQFA` set without the supplemental record is refused by the
  wrapper before FVS sees it.

Does not establish:

- a KC growth-and-yield calibration;
- that the GWM 2007 or Table 29 residual B is achieved from a real KC stand;
- the correct state classes or the full-range vs small-tree choice;
- anything about the 4–10-tree mature clumps (or the 2–5 maximum-diameter
  subgroup), which FVS cannot model.

The KC model still needs a measured or reviewed stem list.

## Reproduction

The pilot scripts are local working material under `/tmp/opencode/` and are not
committed. The commands use the built variant from
`/srv/shared-data/gep/gandy/fresh-fvsbc/tmp/build-venv` and
`PYTHONPATH=src` from the `fresh-fvsbc` checkout. Re-run them against the KC
stem list when it exists, not against this synthetic stand, for a model result.
