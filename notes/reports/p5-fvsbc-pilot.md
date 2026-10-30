# FVS-BC dependency and smoke pilot

Status: regional structural smoke test. Not KC calibration and not a legal
compliance result.

Date: 2026-10-30

## Dependency

Added `requirements-fvsbc.txt`:

```text
fresh-fvsbc[fvs]==0.20.0
```

`requirements-dev.txt` includes it for local and CI environments.

The earlier clean-checkout report recorded `ModuleNotFoundError` because the
checkout had no FVS dependency install. The engine was available in the working
session through the checkout/PYTHONPATH; the clean environment did not have that
path.

The pinned `0.12.0` install was not usable for this pilot: it failed after a
successful FVS run because it expected an `FVS_Error` table that FVS did not
write. `0.20.0` handles the absent table and completed the run.

## Pilot command

```bash
python -m fresh_fvsbc \
  data/psp/idf_cariboo_psp_conditional_stemlists_population.json \
  --directory runtime/fvsbc/kc_pilot_check \
  --species FD --tree-age 60 \
  --block "DATABASE|DSNOut|FVSOut.db|TREELIDB|CUTLIDB|ATRTLIDB|Summary|STRCLSDB" \
  --keyword SITECODE=FD,100 \
  --keyword TIMEINT=,30 \
  --keyword NUMCYCLE=2 \
  --keyword THINBTA=1,18.0 \
  --keyword TREELIST \
  --keyword CUTLIST \
  --keyword ATRTLIST \
  --keyword STRCLASS \
  --keyword PROCESS \
  --keyword STOP
```

The `DATABASE` block must precede the stand setup. The exact option names are
`TREELIDB`, `CUTLIDB`, `ATRTLIDB`, `Summary` and `STRCLSDB`.

## Result

- Exit status: 0
- Warnings: 0
- Summary rows: 3
- `FVS_TreeList_Metric`: 3,657 rows
- `FVS_CutList_Metric`: 3,644 rows
- `FVS_ATRTList_Metric`: 7 rows
- `FVS_Summary_Metric`: 3 rows
- `FVS_StrClass_Metric`: 5 rows

Provenance:

- `fresh_fvsbc_version`: 0.20.0
- `pyfvs_commit`: e95172b
- `fvs_source_commit`: ef5fa847
- variant: BC

## Limits

- The population is the public IDF Cariboo conditional stem-list analog, not
  KC CFI.
- The run is a structural smoke test, not a reviewed KC selection prescription.
- The summary output shows a very high initial TPA because the conditional
  population is an expanded regional analog; do not read it as a KC stand.
- No calibrated-growth claim follows from this run.
