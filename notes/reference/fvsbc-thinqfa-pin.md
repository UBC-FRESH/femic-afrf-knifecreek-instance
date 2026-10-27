# FVS-BC THINQFA pin

The KC `SEL_MDWR_HIGH/MODERATE/LOW` regimes need `THINQFA`, and `THINQFA`
needs a one-line supplemental record that selects the residual-density unit.
`fresh-fvsbc` P42.1 added that support:

- commit: `d86e78b0fc31386684aae1a0a1a9a821c0ee2baf`
- version: `0.12.0`, post-`v0.12.0` main
- keyword model: `Keyword.supplemental` and `SUPPLEMENTAL_KEYWORDS = {"THINQFA"}`
- source: `canada/bc/initre.f` option 141; `READ(IREAD,'(I1)')ISETQFA`
- unit mapping: `0` basal area per acre, `1` trees per acre, `2` SDI

The KC pin is updated in `config/toolchain.yaml`. The wrapper gap and the
entry-year question are marked resolved in `config/fvsbc/regimes.yaml`.

## BC unit rule

`canada/bc/initre.f` converts `THINQFA` fields 2 (minimum DBH), 3 (maximum DBH)
and 6 (diameter-class width) from **centimetres to inches**. The keyword guide's
inches are the base variant's convention. The KC templates therefore store
those three fields in centimetres:

- minimum DBH: `0.0` cm
- maximum DBH: `60.0` / `55.0` / `50.0` cm
- class width: `5.0` cm
- residual density: `126.32` / `95.83` / `69.70` ft²/ac

Passing inches (`23.62`, `1.97`) shortens the range to about 23.6 cm and can
cancel the activity. See `fvsbc-thinqfa-pilot.md` for the failure.

## Entry cycle

A synthetic pilot confirmed:

- cycle 1 applies at year 0;
- `TIMEINT=,30`, `NUMCYCLE=2`, cycle 2 applies at year 30; and
- `TIMEINT=,10`, `NUMCYCLE=4`, cycle 4 also applies at year 30.

The KC template uses `year_or_cycle: 2` with `TIMEINT=,30` and `NUMCYCLE=2`.

## Render check

The High regime renders as a keyword record, then the unit record, with no
`END`:

```text
THINQFA   2         0.0       60.0      0         1.25      5.0       126.32
0
```

A set without the record is refused before a run. This is a structural check;
the synthetic pilot ran, but no KC stem list or calibrated case exists yet.

## Verification snippet

```python
from fresh_fvsbc.keywords import Keyword, render_keyword

fields = ("2", "0.0", "60.0", "0", "1.25", "5.0", "126.32")
print(render_keyword(Keyword("THINQFA", fields, supplemental=("0",))))
```

The last line must be `0` and the text must not contain `END`.
