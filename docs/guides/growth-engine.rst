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

The FVS keyword table includes basal-area and thinning controls, including
`THINBTA`, `THINATA`, `THINBBA`, `THINABA`, `THINPRSC`, and `THINDBH`. A
selection regime is a reviewed combination of:

- the residual basal-area target or the removal proportion;
- the species preference;
- the maximum diameter or the diameter range;
- the cutting cycle and the entry window; and
- the minimum retained structure.

The exact keyword sequence and parameter values are not yet reviewed. They are
templates in `config/fvsbc/regimes.yaml`. Do not run a regime as a policy
scenario until it has a source and a review note.

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
  retained trees within a stand. ws4 handles block-level spatial constraints;
  FVS-BC handles the stand-level tree list.
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
