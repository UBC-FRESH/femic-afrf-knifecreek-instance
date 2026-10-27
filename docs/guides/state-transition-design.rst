State-Transition Design
=======================

Problem
-------

ws4 schedules treatments by block and reads growth from a compiled track. A
track is a succession pathway with an age offset. A continuous-cover selection
regime does not have a single age; it has a structure. The instance therefore
has to translate an individual-tree model into a finite state-transition graph
that ws4 can read.

State
-----

A state is a stand condition at a selection entry. The initial state key is:

.. code-block:: text

   AU + BEC/site class + species group + basal-area class + QMD class + origin

The state carries:

- a stem list or a distribution summary;
- basal area, QMD, density, and species composition;
- large-tree density and canopy cover;
- a growth curve from the entry to the next entry; and
- the habitat indicators that the mule-deer constraints read.

A state is not a single tree list for every block. It is a representative
condition for an analysis unit. Blocks are assigned to the nearest reviewed
state, and the assignment is recorded.

Regime
------

A regime is a selection rule:

- residual basal-area target or removal proportion;
- species preference and maximum diameter;
- cutting cycle and entry window;
- minimum retained structure; and
- the post-cut state key.

The first regimes come from AFRF MWP #3 Table 29 and are reviewed policy
targets, not placeholders:

- `SEL_MDWR_HIGH` — B 29 m²/ha, D 60 cm, q 1.25, 30-year cycle;
- `SEL_MDWR_MODERATE` — B 22 m²/ha, D 55 cm, q 1.25, 30-year cycle; and
- `SEL_MDWR_LOW` — B 16 m²/ha, D 50 cm, q 1.30, 30-year cycle.

The FVS-BC keyword is `THINQFA` (BDq: q-factor, maximum DBH, residual
basal-area density). `THINBTA` is not a basal-area target; it is a
thin-from-below to a trees-per-acre target. `fresh-fvsbc` P42.1 supports the
`THINQFA` supplemental record, and a synthetic pilot settled the entry year:
cycle 2 with a 30-year period cuts at year 30. The regimes are still not
runnable because the KC stem list is not available. See `config/fvsbc/regimes.yaml` and
`config/mdwr_regimes.yaml`.

A design variant, `SEL_MDWR_SMALL_TREE`, thins only the 0–37.5 cm component to
match the plan's operational wording. Its residual density is computed per
state as Table 29 B minus the retained large-tree basal area. Compare it with
the full-range BDq regime in the pilot.

Transition
----------

For a state and a regime, FVS-BC runs:

1. the pre-cut stand for the cutting cycle;
2. a selection cut at the end of the cycle;
3. the residual stand; and
4. the next cycle from the residual stand.

The run records:

- the pre-cut tree list;
- the cut list;
- the after-treatment list;
- the residual state key;
- the growth curve for the cycle; and
- the habitat indicators.

If the residual state does not match a reviewed state, it becomes a new state.
The graph is closed by canonicalizing states into the reviewed classes and by
capping the cycle count.

ws4 translation
---------------

============================  =================================================
State-transition concept      ws4 object
============================  =================================================
State                         ``tracks`` row; ``track_id`` is the state.
Years since entry             ``offset`` / ``age`` clock.
Selection regime              ``treatments`` row with ``treatment`` and
                              ``new_track``.
Cutting cycle                 ``treatments.begin`` (minimum years since entry).
Growth between entries        ``curves`` rows for volume, basal area, QMD, and
                              habitat attributes.
Cut volume and products       ``products`` rows at the treatment.
Habitat indicators            ``features`` rows and account definitions.
Block assignment              ``fragments`` row with the initial ``track_id``.
============================  =================================================

The treatment row for a selection entry has:

- ``begin`` = the minimum cutting cycle;
- ``end`` = the horizon;
- ``treatment`` = the regime name;
- ``new_track`` = the post-cut state;
- ``offset`` = 0, because the post-cut state starts a new entry clock; and
- ``retain`` = 0, because the residual structure is in the new track, not a
  compile-time area split.

Why not a compile-time retention split
--------------------------------------

ws4's compile-time retention rule splits an area into harvested and retained
portions. That is useful for a one-time partial harvest, but a selection regime
is a repeated entry on the same area. The state-transition form keeps the area
whole and moves it to a post-cut state, which is the correct representation of
a repeated selection cut.

Constraints
-----------

The ws4 model must enforce or report:

- no clearcut treatment;
- minimum years between entries (the cutting cycle);
- retained basal area or canopy cover floors;
- large-tree retention;
- maximum opening or disturbed-area limits where applicable; and
- even-flow or non-declining harvest targets.

If a constraint cannot be enforced in ws4 yet, the run report must say so. Do
not describe a constraint as met when it is only reported.

Open questions
--------------

1. The public mule-deer habitat-class layer is acquired; the legal UWR order is
   still blocked. Do not treat the public classes as the legal constraint.
2. The stem-list source is still unresolved: AFRF CFI/research plots or an
   approved VRI + `nemora` synthetic reconstruction.
3. How many states are needed before the graph is stable enough to optimize?
4. Does the block-level spatial constraint need a maximum selection-opening
   size, or is the stand-level retention enough?
5. `THINQFA` is the selected keyword; the wrapper's supplemental-record support
   is in P42.1, and cycle 2 with a 30-year period is the reviewed entry. See
   `config/fvsbc/regimes.yaml`.
6. Should the first public baseline be a single regime or a regime portfolio?
   The plan's AAC is area-based, so start with the High/Moderate/Low portfolio
   and report the area and volume by class.

See `planning/fvsbc-state-transition-design.md` for the working plan.
