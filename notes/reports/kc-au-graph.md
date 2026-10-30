# KC AU BA/QMD state graph

Status: extracted and compiled, but not ready for even-flow use.

## Graph data

Per-plot residual states from the six-entry FVS runs were binned into BA/QMD
classes.

- Low regime: 82 state nodes, 79 majority edges
- Moderate regime: 74 state nodes, 69 majority edges
- BA bins: 0–15, 15–20, 20–25, 25–30, 30–35, 35–40, 40+
- QMD bins: 0–20, 20–25, 25–30, 30–35, 35–40, 40+

Files:

- `data/kc_au_state_graph/low/`
- `data/kc_au_state_graph/moderate/`

## Compiled graph model

- `data/kc_ws4_recipe_au_graph/forestmodel.xml`
- `ws4/dataset_kc_au_graph_v1`
- 160 blocks, 83 tracks, 84 treatments, 498 feature rows, 84 product rows
- `ws4 validate` passes

## Problem found

A 5,000-iteration even-flow probe fails from period 7 onward. The main reason is
that the graph collapses multiple plots into a state and then uses a single
majority next-state edge. That loses the state-specific transitions the
optimizer needs.

This graph is recorded as an intermediate artifact. Do not treat it as the
production model.

## Next

Preserve the per-plot transition support and avoid collapsing a state to one
majority edge, or use a state graph keyed more finely so each state has a stable
next state.
