FVS-BC configuration
====================

`regimes.yaml` holds the Knife Creek selection regimes. The residual-structure
targets now come from the AFRF Management and Working Plan #3, Table 29; the
policy contract is in `../mdwr_regimes.yaml` and the context note is
`../../notes/reference/mwp3-kc-management-direction.md`.

The three regimes are:

- `SEL_MDWR_HIGH` — B 29 m²/ha, D 60 cm, q 1.25, 30-year cycle;
- `SEL_MDWR_MODERATE` — B 22 m²/ha, D 55 cm, q 1.25, 30-year cycle; and
- `SEL_MDWR_LOW` — B 16 m²/ha, D 50 cm, q 1.30, 30-year cycle.

They are reviewed policy targets but they are **not yet runnable**. The pilot
must resolve:

1. the KC stem list; and
2. whether a full-range BDq cut or the small-tree variant better matches the
   plan's “concentrate below 37.5 cm DBH” wording.

`THINQFA` is the right keyword because it encodes BDq directly. `THINBTA` is
not a basal-area target; it is a thin-from-below to a trees-per-acre target.
`THINBBA`, `THINABA`, `THINDBH` and `THINQFA` are the relevant alternatives.
The policy does not justify a clearcut or an even-aged regime.

Resolved wrapper gap
--------------------

`fresh-fvsbc` P42.1 added `Keyword.supplemental` and
`SUPPLEMENTAL_KEYWORDS`, so the wrapper now writes `THINQFA`'s one-line
residual-density-units record with no `END` terminator. The KC pin is
`d86e78b0fc31386684aae1a0a1a9a821c0ee2baf` (post-v0.12.0 main). The
supplemental record is no longer the blocker.

A synthetic pilot settled the entry year: cycle 2 with `TIMEINT=,30` and
`NUMCYCLE=2` applies the cut at year 30. The full-range vs small-tree choice
and the KC stem list remain.

THINQFA units in BC
-------------------

`canada/bc/initre.f` option 141 converts `THINQFA` fields 2 (minimum DBH), 3
(maximum DBH) and 6 (class width) from **centimetres to inches**. The keyword
guide's inches are the base variant's convention. The KC templates therefore
store those three fields in centimetres. The residual-density target is square
feet per acre: 126.32 is 29 m²/ha, 95.83 is 22 m²/ha, and 69.70 is 16 m²/ha.

The synthetic pilot is `../../notes/reference/fvsbc-thinqfa-pilot.md`.

Benchmark
---------

`data/benchmarks/mwp3_figure11_target_stand_structure.csv` is the recovered
Figure 11 target diameter distribution. Use Table 29 for the residual B/D/q
contract and Figure 11 for the shape. The recovered basal-area sums are
17.02/22.96/30.17 m²/ha for Low/Moderate/High, slightly above the Table 29
targets; report the difference rather than rescaling the figure.

The growth engine is pinned in `../toolchain.yaml`:

- `fresh-fvsbc` at commit `d86e78b0fc31386684aae1a0a1a9a821c0ee2baf`;
- package version 0.12.0, post-v0.12.0 main (the tag predates P42.1).

The wrapper's keyword and output contracts are at
<https://ubc-fresh.github.io/fresh-fvsbc/>. Read the keyword page before adding
a new keyword: the wrapper validates the name, and the parameter fields are ten
columns wide.
