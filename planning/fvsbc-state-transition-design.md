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
regime_id = SEL_GWM_<HABITAT>       # default
regime_id = SEL_MDWR_<HABITAT>      # AFRF Table 29 alternative
```

The default regimes are GWM 2007 (Amended Order U-5-001/2/3):

- `SEL_GWM_HIGH`: B 29, BA >37.5 ≥16, D ≥70, q 1.25;
- `SEL_GWM_MODERATE`: B 22, BA >37.5 ≥11, D ≥60, q 1.25; and
- `SEL_GWM_LOW`: B 16, BA >37.5 ≥6, D ≥50, q 1.30.

The default cut is split: `THINABA` above 37.5 cm to the large-tree minimum,
then `THINQFA` on 0–37.5 cm to `B − large-tree BA`. Surplus large trees above
the minimum are harvestable. `THINBTA` is a trees-per-acre target, not a
basal-area target.

The AFRF MWP #3 Table 29 regimes (`SEL_MDWR_HIGH/MODERATE/LOW`) are a named
alternative: B 29/22/16, D 60/55/50, q 1.25/1.25/1.30. They are not legal
compliance and must not be mixed with GWM states.

The regimes are reviewed policy, but they are not yet runnable on KC.
`fresh-fvsbc` P42.1 supports the `THINQFA` supplemental residual-density-units
record. A synthetic pilot settled the entry cycle: cycle 1 is year 0, and cycle
2 with `TIMEINT=,30` is year 30. The BC variant reads fields 2, 3 and 6 in
centimetres; see `notes/reference/fvsbc-thinqfa-pilot.md`.

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
`data/benchmarks/mwp3_figure11_target_stand_structure.csv`. Use the GWM 2007
targets for the legal default and Figure 11 for the relative 5 cm diameter
distribution. Table 29 is the AFRF alternative. The recovered basal-area sums
are 17.02/22.96/30.17 m2/ha for Low/Moderate/High; report the difference from
the 16/22/29 Table 29 totals rather than rescaling.

## Open questions

1. Which stem-list source is available?
2. How many basal-area and QMD classes are enough?
3. The legal constraint is now explicit: BA >37.5 cm, 4–10-tree clumps,
   canopy openings, and the HMZ matrix. What remains is the spatial UWR/HMZ
   layer and a decision on how to report canopy-opening layout.
4. Should the state include a years-since-entry dimension, or is the offset
   clock enough?
5. How should a regime portfolio be represented: one treatment per regime, or
   a nested choice?
6. How should the model handle the 2013 burn area as a distinct origin?
7. The default is the GWM split cut. The retain-all-above-D variant remains a
   sensitivity, not the default.

## Next experiments

1. Run one real KC AU through a single GWM split cut once the stem list
   exists.
2. Confirm the cut list and after-treatment list are populated.
3. Compare the residual B, BA >37.5, D, q and 5 cm distribution with GWM 2007
   and Figure 11; run Table 29 as the AFRF comparison.
4. Build a two-cycle graph from the residual state.
5. Export the two-state graph to ws4 and validate the dataset.
6. Add a mule-deer feature account and report it.
