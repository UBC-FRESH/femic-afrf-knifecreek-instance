# Canonical GWM 2007 state graph

Status: **structural canonicalization of the provisional v1 library**. Not a
compiled ws4 dataset, not KC-calibrated, not legal compliance.

## What changed

The v1 state IDs were per stand/regime/entry (72 states). This graph maps them
to shared classes:

- BA: `<20`, `20–25`, `25–30`, `30–35`, `35–40`, `40+` m²/ha;
- QMD: `<20`, `20–25`, `25–30`, `30–35`, `35+` cm;
- large-tree BA (`≥37.5 cm`): `NA`, `<6`, `6–11`, `11–16`, `16+` m²/ha;
- reserve above D: `NA`, `<0.5`, `0.5–2`, `2+` m²/ha.

The initial states have no large-tree/reserve values and therefore carry
`LT_NA`/`RES_NA`.

## Counts

- 23 canonical states;
- 25 transitions;
- 500 curve rows (five attributes per edge-year);
- 6 terminal states;
- 0 cycles.

Duplicate `from-state + regime` transitions are collapsed to the modal target
state; the number of source transitions is retained in `n_sources`. Curves are
averaged by year across the contributing source transitions.

## Closure rule

The graph is **terminal-closed**, not cycle-closed. Six canonical states have no
outgoing treatment. They are listed in `graph.json` and marked `terminal` in
`states.csv`. No artificial self-loop is added.

## Limits

- The classes are structural bins, not calibrated states.
- The clump rule is still a DBH-ranked six-tree proxy, not spatial.
- The graph has no HMZ spatial constraint.
- The source library is PSP-derived, not KC data.
- No legal-compliance claim.

## Next

Use this graph to build the first synthetic ws4 dataset, then run
`ws4 validate`. A real KC dataset still needs the CFI, spatial clumps and the
UWR/HMZ layer.
