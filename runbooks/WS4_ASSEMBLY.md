# ws4 assembly runbook

Status: Phase 3 procedure. Not yet run for Knife Creek.

## Inputs

- the state-transition library manifest;
- the block-to-state and block-to-AU assignment;
- the block geometry and area;
- the topology; and
- the target and patch-account definitions.

## Table mapping

| Library field | ws4 table | Notes |
| --- | --- | --- |
| State | `tracks` | `track_id` and `name` |
| Years since entry | `strata` | `offset`, `next_age`, `cycle` |
| Selection regime | `treatments` | `treatment`, `new_track`, `begin`, `end` |
| Growth curve | `curves` | `curve_id`, `x`, `y` |
| Habitat indicator | `features` | `track_id`, `label`, `curve_id` |
| Cut yield | `products` | `track_id`, `treatment`, `label`, `curve_id` |
| Block assignment | `fragments` | `block_id`, `track_id`, `area_ha`, `age` |
| Block area | `blocks` | `block_id`, `track_id`, `offset`, `area_ha` |
| Accounts | `accounts` / `protoaccounts` | account definitions |
| Groups | `groups` | block grouping |

## Build

```bash
ws4 build \
  --xml path/to/knifecreek_recipe.xml \
  --fragments path/to/knifecreek_fragments.csv \
  --out ws4/runtime/knifecreek
ws4 validate --dataset ws4/runtime/knifecreek
```

If the state library is exported as a complete matrix rather than a recipe,
use `ws4 ingest` instead. The choice is a Phase 2 decision; the dataset
contract is the same.

## Baseline

1. Assign every block an initial state.
2. Set a cutting cycle in `treatments.begin`.
3. Build a selection-only schedule.
4. Run with the topology and patch accounts.
5. Report harvest, growing stock, habitat indicators, and entry frequency.

```bash
ws4 simulate \
  --dataset ws4/runtime/knifecreek \
  --schedule ws4/schedules/selection_baseline.csv \
  --years 300 \
  --out ws4/runtime/selection_baseline \
  --topology ws4/topology.csv \
  --patch-accounts ws4/patch_accounts.yaml
```

## Validation

The dataset is acceptable when:

- every block has a state and an AU;
- every state has a growth curve;
- every treatment points to a real residual track;
- the topology has no cross-block edges;
- the cutting cycle is enforced;
- no clearcut treatment exists; and
- the habitat accounts are present.

## Record

Write the dataset manifest, the schedule, the target report, and a short JSON
summary under `ws4/evidence/`. Generated runtime files stay under
`ws4/runtime/` and are ignored by Git.
