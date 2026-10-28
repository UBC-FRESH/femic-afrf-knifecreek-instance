FVS-BC configuration
====================

`regimes.yaml` holds the Knife Creek selection regimes. The default basis is
**GWM 2007** (Amended Order #U-5-001/2/3, Shallow and Moderate Snowpack). The
AFRF MWP #3 Table 29 regimes are a named alternative under
`afrf_table29_regimes`. The policy contract is in `../mdwr_regimes.yaml`; the
legal note is `../../notes/reference/mdwr-canopy-clump-requirements.md`.

Default GWM 2007 regimes
------------------------

The default is a split large/small cut. Surplus large trees above the legal
minimum are harvestable.

- `SEL_GWM_HIGH` — B 29 m²/ha, BA >37.5 ≥16, D ≥70, q 1.25;
- `SEL_GWM_MODERATE` — B 22, BA >37.5 ≥11, D ≥60, q 1.25; and
- `SEL_GWM_LOW` — B 16, BA >37.5 ≥6, D ≥50, q 1.30.

Each regime runs `THINABA` in the 37.5–D cm range to the large-tree minimum,
leaving trees above D as the reserve, then `THINQFA` on 0–37.5 cm to
`B − large-tree BA`. For High, the small-tree target is 13 m²/ha, or
56.63 ft²/ac. The Table 2 reserve above D is 0–2.9/0–2.2/0–1.6 m²/ha.

The first GWM pilot is in `../../ws4/gwm_pilot_v0/`. It passes 17/30
stand-structure checks. The D-protected split leaves the >D reserve and fails q
in most High/Moderate cases; a tree-level reserve/marking rule is needed to
harvest surplus above D without stripping the D floor.

A retain-all-above-D variant, `SEL_GWM_HIGH_RETAIN`, is a sensitivity. It is
not the default because it forgoes the surplus large-tree harvest.

Table 29 alternative
--------------------

`afrf_table29_regimes` keeps the AFRF management-plan comparison:

- `SEL_MDWR_HIGH` — B 29, D 60, q 1.25;
- `SEL_MDWR_MODERATE` — B 22, D 55, q 1.25; and
- `SEL_MDWR_LOW` — B 16, D 50, q 1.30.

These are not legal compliance. They use lower D and omit the legal BA >37.5
targets and reserve. Do not mix them with GWM states in one graph.

Keyword notes
-------------

`THINQFA` is the right keyword because it encodes BDq directly. `THINBTA` is
not a basal-area target; it is a thin-from-below to a trees-per-acre target.
`THINBBA`, `THINABA`, `THINDBH` and `THINQFA` are the relevant alternatives.
The policy does not justify a clearcut or an even-aged regime.

Resolved wrapper gap
--------------------

`fresh-fvsbc` P42.1 added `Keyword.supplemental` and
`SUPPLEMENTAL_KEYWORDS`, so the wrapper writes `THINQFA`'s one-line
residual-density-units record with no `END` terminator. The KC pin is
`d86e78b0fc31386684aae1a0a1a9a821c0ee2baf` (post-v0.12.0 main).

A synthetic pilot settled the entry year: cycle 2 with `TIMEINT=,30` and
`NUMCYCLE=2` applies the cut at year 30. The KC stem list remains the blocker.

THINQFA units in BC
-------------------

`canada/bc/initre.f` option 141 converts `THINQFA` fields 2 (minimum DBH), 3
(maximum DBH) and 6 (class width) from **centimetres to inches**. The keyword
guide's inches are the base variant's convention. The KC templates therefore
store those three fields in centimetres. The residual-density target is square
feet per acre: 56.63 is 13 m²/ha, 47.92 is 11 m²/ha, and 43.56 is 10 m²/ha.

`THINABA` field 2 is m²/ha and its DBH fields are cm. The synthetic pilot is
`../../notes/reference/fvsbc-thinqfa-pilot.md`.

Benchmark
---------

The default legal targets are in `../../data/benchmarks/mdwr_gwm2007_targets.csv`,
`..._clump.csv` and `..._knife_creek_hmz.csv`.

`data/benchmarks/mwp3_figure11_target_stand_structure.csv` is the recovered
Figure 11 target diameter distribution. Use it for the AFRF Table 29 shape
comparison, not the legal curve. The recovered basal-area sums are
17.02/22.96/30.17 m²/ha for Low/Moderate/High, slightly above the Table 29
targets; report the difference rather than rescaling the figure.

The growth engine is pinned in `../toolchain.yaml`:

- `fresh-fvsbc` at commit `d86e78b0fc31386684aae1a0a1a9a821c0ee2baf`;
- package version 0.12.0, post-v0.12.0 main (the tag predates P42.1).

The wrapper's keyword and output contracts are at
<https://ubc-fresh.github.io/fresh-fvsbc/>. Read the keyword page before adding
a new keyword: the wrapper validates the name, and the parameter fields are ten
columns wide.
