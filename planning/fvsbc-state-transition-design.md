# FVS-BC state-transition design

Date: 2026-10-26
Status: design, not implemented

## Purpose

Turn individual-tree FVS-BC selection-cut runs into a finite state-transition
library that ws4 can schedule and optimize.

## Why a state graph

ws4 reads a compiled matrix of tracks, treatments, and curves. A track is a
succession pathway. A continuous-cover selection regime is not a single age
sequence; it is a set of stand structures and the transitions between them.

The state graph makes the structure explicit:

- a state is a stand condition at an entry;
- a regime moves the state to a residual state;
- the growth curve describes the interval; and
- the next entry starts from the residual state.

## State key

Initial proposal:

```text
state_id = <au_id>__<species_group>__<ba_class>__<qmd_class>__<origin>
```

Where:

- `au_id` is the analysis unit (BEC/site/species class);
- `species_group` is the leading species group, such as `FD`, `FD-PL`, `SX`;
- `ba_class` is a basal-area class, such as `BA10_20`, `BA20_30`, `BA30_40`;
- `qmd_class` is a quadratic-mean-diameter class, such as `QMD20_35`,
  `QMD35_50`; and
- `origin` is `natural`, `burned`, or `planted` where it changes the growth
  assumption.

The classes are reviewed after the pilot. They are not policy.

## Regime key

```text
regime_id = SEL_MDWR_<HABITAT>
```

The first regimes come from AFRF MWP #3 Table 29:

- `SEL_MDWR_HIGH`: B 29 m2/ha, D 60 cm, q 1.25, 30-year cycle;
- `SEL_MDWR_MODERATE`: B 22 m2/ha, D 55 cm, q 1.25, 30-year cycle; and
- `SEL_MDWR_LOW`: B 16 m2/ha, D 50 cm, q 1.30, 30-year cycle.

The FVS-BC keyword is `THINQFA` (BDq). `THINBTA` is a trees-per-acre target,
not a basal-area target. A design variant, `SEL_MDWR_SMALL_TREE`, thins only
the 0-37.5 cm component and computes its residual density per state as Table 29
B minus the retained large-tree basal area.

The regimes are reviewed policy, but they are not yet runnable. `fresh-fvsbc`
0.11.0 does not model the `THINQFA` supplemental residual-density-units record,
and the entry-year/cycle semantics need a controlled pilot.

## Run sequence

For each `state` and `regime`:

1. **Pre-cut run.** Grow the state from its entry condition for the cutting
   cycle. Request `FVS_TreeList_Metric`, `FVS_Summary_Metric`,
   `FVS_StrClass_Metric`, and `FVS_Carbon_Metric` if needed.
2. **Cut run.** Apply the selection keyword at the end of the cycle. Request
   `FVS_CutList_Metric`, `FVS_ATRTList_Metric`, and `FVS_TreeList_Metric`.
3. **Residual key.** Derive the residual basal area, QMD, species composition,
   and large-tree structure from the after-treatment list. Map to a reviewed
   residual state.
4. **Growth curve.** Use the pre-cut summary and tree list to build the
   interval curve for volume, basal area, QMD, and habitat indicators.
5. **Transition.** Record `state -> regime -> residual_state` with the cut
   yield and the growth curve.
6. **Repeat.** Grow the residual state for the next cycle until the graph
   closes or the cycle cap is reached.

## Canonicalization

A raw residual state rarely matches a reviewed state exactly. Canonicalize by:

- rounding basal area and QMD to the class bounds;
- assigning the leading species group by volume share;
- preserving origin when it changes the growth assumption; and
- recording the raw values beside the canonical key.

If a residual state falls outside the reviewed classes, add a state or flag the
transition as unresolved. Do not silently snap it to a distant state.

## Graph closure

Stop when:

- every reachable state has a transition for every reviewed regime;
- the cycle cap is reached; or
- a state repeats, which closes a cycle.

A repeated state is a success, not an error. It means the regime is sustainable
in the model.

## ws4 export

| Library | ws4 |
| --- | --- |
| State | `tracks` row |
| Years since entry | `strata.offset` and `strata.next_age` |
| Selection regime | `treatments.treatment` |
| Residual state | `treatments.new_track` |
| Cutting cycle | `treatments.begin` |
| Growth curve | `curves` rows |
| Habitat indicator | `features` rows |
| Cut yield | `products` rows |
| Block assignment | `fragments.track_id` |

The `treatments.offset` is 0 because the residual state starts a new entry
clock. The `treatments.retain` is 0 because the residual structure is in the
new track, not in a compile-time area split.

## Validation

The first library is acceptable when:

- every state has a tree list or a distribution summary;
- every transition has a cut list and an after-treatment list;
- the residual state key is reproducible from the cut list;
- the growth curve is monotonic in the attributes where it should be;
- the graph has no orphan states;
- the ws4 export validates; and
- the run manifest records the FVS-BC commit, keyword hash, and stem-list hash.

## Public benchmark

MWP #3 Figure 11 was recovered with `figrecover` into
`data/benchmarks/mwp3_figure11_target_stand_structure.csv`. Use Table 29 for
the residual B/D/q target and Figure 11 for the relative 5 cm diameter
distribution. The recovered basal-area sums are 17.02/22.96/30.17 m2/ha for
Low/Moderate/High; report the difference from the 16/22/29 targets rather than
rescaling.

## Open questions

1. Which stem-list source is available?
2. How many basal-area and QMD classes are enough?
3. Does the mule-deer constraint act on basal area, canopy cover, large-tree
   density, or a combination? The plan's Table 29 is the public starting point.
4. Should the state include a years-since-entry dimension, or is the offset
   clock enough?
5. How should a regime portfolio be represented: one treatment per regime, or
   a nested choice?
6. How should the model handle the 2013 burn area as a distinct origin?
7. Do we use the full-range BDq cut or the 0-37.5 cm small-tree variant?

## Next experiments

1. Add `THINQFA` supplemental-record support to `fresh-fvsbc`.
2. Build one synthetic FD stand and run a single `THINQFA` selection cut.
3. Confirm the cut list and after-treatment list are populated.
4. Compare the residual B, D, q and 5 cm distribution with Table 29 and
   Figure 11.
5. Build a two-cycle graph from the residual state.
6. Export the two-state graph to ws4 and validate the dataset.
7. Add a mule-deer feature account and report it.
