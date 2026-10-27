Growth Engine
=============

Decision
--------

The primary growth engine for Knife Creek is **FVS-BC** through the
`UBC-FRESH/fresh-fvsbc` Python wrapper. VDYP and TIPSY are not the primary
engine for this instance.

Why not VDYP or TIPSY
---------------------

VDYP and TIPSY are stand-level models. They produce average volume and yield
for a stand condition. They do not carry a diameter distribution through a
selection cut, and they do not report the stems that were removed and the stems
that remain. A continuous-cover selection regime depends on exactly that
residual structure: the next entry grows from the post-cut trees, not from an
average age-class curve.

That does not make VDYP or TIPSY useless. They remain useful for:

- a documented even-aged sensitivity;
- comparison with the Gavin Lake legacy curves; and
- a coarse check on the FVS-BC volume level.

They are not the state engine.

What FVS-BC provides
--------------------

FVS-BC is an individual-tree, distance-independent growth model. The wrapper
exposes the keyword set and the SQLite output tables. The tables this instance
needs are:

- `FVS_TreeList_Metric` — one row per tree per period, including species, DBH,
  height, crown ratio, and volume attributes;
- `FVS_CutList_Metric` — the removed trees, with the same per-tree detail;
- `FVS_ATRTList_Metric` — the after-treatment listing, when a removal occurs;
- `FVS_Summary_Metric` — stand-level volume, basal area, and density by period;
- `FVS_StrClass_Metric` — structural stage and canopy attributes;
- `FVS_Stats_Species_Metric` — species composition; and
- `FVS_Carbon_Metric` — carbon pools, if the scenario needs them.

The per-tree and cut-list tables are the reason FVS-BC is the right engine. They
let the instance compute the residual state directly instead of assuming it.

Selection-cut keywords
----------------------

The Knife Creek regimes use `THINQFA` (THIN Q-Factor Approach), because the
AFRF plan specifies BDq: residual basal area, maximum DBH, and q-factor by
habitat class. `THINQFA` thins through a diameter range to a q-factor
distribution and a residual density. The FVS fields are:

- entry year or cycle;
- minimum DBH (in);
- maximum DBH (in);
- species code;
- q-factor;
- diameter-class width (in); and
- residual density, with a supplemental record selecting basal area per acre,
  trees per acre, or SDI.

`THINBTA` is **not** a basal-area target; it is a thin-from-below to a
trees-per-acre target. `THINBBA`, `THINABA`, `THINDBH` and `THINQFA` are the
relevant alternatives. The plan's values are in
`config/mdwr_regimes.yaml`; the keyword templates are in
`config/fvsbc/regimes.yaml`.

`fresh-fvsbc` 0.11.0 does not yet model the `THINQFA` supplemental record. Add
that wrapper support before running the regimes. The entry-year/cycle semantics
also need a controlled pilot.

A selection regime is a reviewed combination of:

- the residual basal-area target or the removal proportion;
- the species preference;
- the maximum diameter or the diameter range;
- the cutting cycle and the entry window; and
- the minimum retained structure.

The numbers are reviewed policy (Table 29), but the keyword sequence is not yet
validated by a run. Do not run a regime as a policy scenario until the pilot
and the wrapper gap are closed.

Stem lists
----------

FVS-BC needs a tree list. The VRI does not provide one. The options are:

1. measured CFI or research plots, if AFRF can provide them;
2. a reviewed reconstruction from VRI species, age, site index, and density;
   or
3. `nemora` synthetic populations fitted to available tallies.

Every stem list must record:

- its source and method;
- the species, DBH, height, and crown-ratio distributions;
- the stand or AU it represents;
- the generator and parameters; and
- the uncertainty that a synthetic list carries.

A synthetic list is not field data. Label it.

Known limits
------------

- FVS-BC is distance-independent. It does not model the spatial arrangement of
  retained trees within a stand. The plan's 2–5 tree maximum-diameter groups are
  a ws4/post-processing constraint, not an FVS keyword.
- `THINQFA` needs a supplemental residual-density-units record that
  `fresh-fvsbc` 0.11.0 does not yet expose. Do not hand-edit generated keyword
  files to work around it; add the wrapper support.
- The wrapper is at package version 0.11.0 and commit
  `ca33d0e26a079a72add5108f1b182b798b0c4e3e`. Pin it and re-run the pilot when
  it moves.
- The FVS-BC build recipe is in the wrapper's ADR 0004. This instance does not
  vendor the build.
- FVS-BC is not calibrated for Knife Creek. A calibration is a later decision,
  not an assumption.

References
----------

- `fresh-fvsbc` documentation: <https://ubc-fresh.github.io/fresh-fvsbc/>
- `fresh-fvsbc` repository: <https://github.com/UBC-FRESH/fresh-fvsbc>
- `nemora` repository: <https://github.com/UBC-FRESH/nemora>
