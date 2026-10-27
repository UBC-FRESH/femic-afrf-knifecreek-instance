# FVS-BC THINQFA pin

The KC `SEL_MDWR_HIGH/MODERATE/LOW` regimes need `THINQFA`, and `THINQFA`
needs a one-line supplemental record that selects the residual-density unit.
`fresh-fvsbc` P42.1 added that support:

- commit: `d86e78b0fc31386684aae1a0a1a9a821c0ee2baf`
- version: `0.12.0`, post-`v0.12.0` main
- keyword model: `Keyword.supplemental` and `SUPPLEMENTAL_KEYWORDS = {"THINQFA"}`
- source: `canada/bc/initre.f` option 141; `READ(IREAD,'(I1)')ISETQFA`
- unit mapping: `0` basal area per acre, `1` trees per acre, `2` SDI

The KC pin is updated in `config/toolchain.yaml`. The wrapper gap is marked
resolved in `config/fvsbc/regimes.yaml`; the entry-year/cycle semantics remain
a pilot question.

## Render check

The High regime renders as a keyword record, then the unit record, with no
`END`:

```text
THINQFA   1         0.0       23.62     0         1.25      1.97      126.32
0
```

A set without the record is refused before a run. This is a structural check
only; no FVS-BC case has been run, because the KC stem list is still P1.3/P1.4.

## Verification snippet

```python
from fresh_fvsbc.keywords import Keyword, render_keyword

fields = ("1", "0.0", "23.62", "0", "1.25", "1.97", "126.32")
print(render_keyword(Keyword("THINQFA", fields, supplemental=("0",))))
```

The last line must be `0` and the text must not contain `END`.
