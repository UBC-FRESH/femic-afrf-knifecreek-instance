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

The first regimes are templates:

- `SEL_BA18` — retain 18 m²/ha;
- `SEL_BA25` — retain 25 m²/ha; and
- `SEL_BA30` — retain 30 m²/ha.

The numbers are illustrative until the mule-deer constraints and the FVS-BC
pilot are reviewed. They are not policy.

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

1. What is the authoritative mule-deer constraint layer, and what are its
   spatial classes?
2. Which stem-list source is available: CFI plots, research plots, or a
   nemora reconstruction?
3. How many states are needed before the graph is stable enough to optimize?
4. Does the block-level spatial constraint need a maximum selection-opening
   size, or is the stand-level retention enough?
5. Which FVS-BC keywords encode the reviewed regimes, and in what order?
6. Should the first public baseline be a single regime or a regime portfolio?

See `planning/fvsbc-state-transition-design.md` for the working plan.
