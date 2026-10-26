# Knife Creek ws4 instance

The ws4 dataset for Knife Creek is a **state-transition matrix**:

- a track is a stand state at a selection entry;
- a treatment is a selection regime that moves the block to a residual state;
- the entry clock is years since the last selection entry;
- the growth curve is the interval growth from FVS-BC;
- features carry the habitat indicators; and
- products carry the cut yield.

There is no clearcut treatment in the default model.

## Status

There is no runnable dataset yet. The contract is in
`state_transition_contract.md`; the target and patch-account files are
templates.

## Planned files

| File | Purpose |
| --- | --- |
| `state_transition_contract.md` | The table and identifier contract |
| `targets.template.yaml` | Harvest and habitat target template |
| `patch_accounts.template.yaml` | Selection-opening patch account template |
| `topology.csv` | Block topology, once the boundary exists |
| `schedules/` | Baseline and scenario schedules |
| `evidence/` | Small JSON evidence summaries |

## Relationship to Gavin Lake

Gavin Lake uses an age-class legacy matrix. Knife Creek uses a state-transition
matrix. Both compile to the same ws4 schema. The merged model is a later
project; see `notes/adr/0004-merged-afrf-model.md`.
