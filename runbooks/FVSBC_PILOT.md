# FVS-BC pilot runbook

Status: Phase 2 procedure. Not yet run for Knife Creek.

## Prerequisites

- A pinned `fresh-fvsbc` checkout or install at commit
  `d86e78b0fc31386684aae1a0a1a9a821c0ee2baf`.
- A built FVS-BC variant. See the wrapper's ADR 0004 for the build recipe.
- A stem population for one reviewed AU.
- A reviewed selection keyword sequence.

## Population shape

`fresh-fvsbc` reads a JSON list of stem records shaped like nemora output:

```json
[
  {"stand_id": "KC-AU01", "dbh_cm": 20.0, "height_m": 18.0, "crown_ratio": 0.5},
  {"stand_id": "KC-AU01", "dbh_cm": 26.0, "height_m": 22.0, "crown_ratio": 0.6}
]
```

The wrapper requires `--species` and `--tree-age`; it does not default them.

## Pilot command

This is a shape, not a reviewed run:

```bash
python -m fresh_fvsbc data/fvsbc/populations/AU01.json \
  --directory runtime/fvsbc/AU01_sel_ba18 \
  --species FD --tree-age 60 \
  --keyword SITECODE=FD,100 \
  --keyword NUMCYCLE=4 \
  --keyword THINBTA=1,18.0 \
  --keyword PROCESS \
  --block "DATABASE|DSNOut|FVSOut.db|TreeLIDB|CutLIDB|ATRTLIDB|Summary|StrClass" \
  --keyword STOP
```

Before running, read the wrapper's keyword and output contracts:

- <https://ubc-fresh.github.io/fresh-fvsbc/reference/keywords.html>
- <https://ubc-fresh.github.io/fresh-fvsbc/reference/outputs.html>

The `DATABASE` block must precede the stand setup. The per-tree and cut-list
tables need both the database option and the matching request keyword.

## Outputs to inspect

- `FVS_Cases` — run identity, variant, version, keyword file.
- `FVS_Error` — warnings and errors.
- `FVS_TreeList_Metric` — pre-cut and post-cut trees.
- `FVS_CutList_Metric` — removed trees.
- `FVS_ATRTList_Metric` — after-treatment list.
- `FVS_Summary_Metric` — stand-level volume, basal area, density.
- `FVS_StrClass_Metric` — structural stage.
- `provenance.json` — the wrapper's run record.

## Acceptance

The pilot is accepted when:

- the run exits 0;
- the cut list is non-empty;
- the after-treatment list shows the residual stand;
- the residual basal area is close to the regime target (record the
  difference);
- the summary shows growth over the cycle; and
- the run manifest records the stem-list hash, keyword hash, and FVS-BC
  commit.

## Failure signatures

- Empty cut list: the residual target is above the stand's basal area, so FVS
  cancels the removal.
- Missing tree or cut list: the database block or the request keyword is
  missing.
- `FVS_Error` row of severity `ERROR`: read the message before changing the
  keyword set.
- Wrong species or site code: the wrapper exits 2 before a run; fix the input.

## Record

Write a short report under `notes/reports/` with the command, the exit status,
the output table row counts, the residual basal area, and the known limits.
