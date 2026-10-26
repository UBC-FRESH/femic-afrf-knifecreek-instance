# ADR 0002: FVS-BC is the Knife Creek growth engine

Status: accepted
Date: 2026-10-26

## Context

Knife Creek is predominantly IDFdk3, with a small IDFxm component and an
eastern transition to SBPSmk. Interior Douglas-fir is relatively shade tolerant
there. Almost the whole block is under mule-deer winter-range constraints.
Even-aged clearcutting is therefore largely unavailable; the operating regime
is uneven-aged continuous cover selection.

VDYP and TIPSY are stand-level models. They produce average volume and yield for
a stand condition. They do not carry a residual diameter distribution through a
selection entry, and they do not report the removed and retained stems. A
selection regime depends on that residual structure.

`UBC-FRESH/fresh-fvsbc` wraps the BC variant of the USDA Forest Service Forest
Vegetation Simulator. It exposes the keyword set and the SQLite output tables,
including per-tree, cut-list, after-treatment, structural, and summary tables.

## Decision

Use FVS-BC through `fresh-fvsbc` as the primary growth engine for Knife Creek.
Pin it by repository and commit:

- repository: `https://github.com/UBC-FRESH/fresh-fvsbc`
- commit: `ca33d0e26a079a72add5108f1b182b798b0c4e3e`
- package version: `0.11.0`

VDYP and TIPSY remain available only for a documented even-aged sensitivity or
a volume cross-check. They are not the state engine.

The bridge to ws4 is a state-transition library:

1. FVS-BC runs a pre-cut stand and a selection cut.
2. The per-tree and cut-list outputs define the residual state.
3. The residual state is grown for the cutting cycle.
4. The cycle becomes a ws4 track; the entry becomes a ws4 treatment; the
   growth and habitat attributes become ws4 curves and features.

## Alternatives considered

- **VDYP/TIPSY age-class curves.** Rejected as the primary engine: they cannot
  carry the residual diameter distribution through repeated selection entries.
- **A custom stand-table projection.** Rejected for now: more bespoke code,
  less external validation, and no per-tree cut list.
- **FVS-BC with a VDYP curve calibration.** Deferred: possible later, but it
  does not remove the need for a tree list or a residual state.

## Consequences

- The instance needs a tree list for every analysis unit. VRI is polygon-level;
  the tree list comes from measured plots, a reviewed reconstruction, or
  `nemora`. A synthetic list is labelled as synthetic.
- The state space must be finite and canonicalized. The state key and the
  regime set are model contracts, not implementation details.
- FVS-BC is not calibrated for Knife Creek. The first runs are structural and
  policy experiments, not calibrated forecasts.
- The wrapper is pinned. Moving the pin requires re-running the pilot and
  updating the evidence.
- The mule-deer constraints are ws4-level constraints, not FVS-BC keywords.
  They must be mapped to accounts and checked in the estate model.
