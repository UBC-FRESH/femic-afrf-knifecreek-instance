# Synthetic ws4 validation dataset

Status: **structural validation fixture**, not a Knife Creek operating dataset.

## What it is

A ws4 compiled dataset built from the canonical GWM 2007 graph:

- 4 synthetic 1 ha blocks, one per initial canonical state;
- 23 canonical tracks;
- 25 treatments;
- 575 curve rows;
- 4 fragments;
- GWM 2007 basis.

It exists to exercise the ws4 tables and validator. The spatial VRI/HMZ
structural dataset is in `../dataset_kc_spatial_v1/`.

## Validation

```bash
PYTHONPATH=/srv/shared-data/gep/ws4/ws4 \
  python -m ws4.cli validate --dataset ws4/dataset_v1_synthetic
```

Result: **Dataset is valid**.

## Tables

- `fragments.parquet`, `blocks.parquet` — 4 synthetic 1 ha blocks;
- `tracks.parquet` — 23 canonical states;
- `strata.parquet` — 30-year entry clock;
- `treatments.parquet` — 25 GWM selection transitions, no clearcut;
- `curves.parquet` — BA, QMD, volume, TPH, canopy CCF and constant large-tree
  BA/product curves;
- `features.parquet` — basal area, QMD, CCF and large-tree BA;
- `products.parquet` — managed yield;
- `accounts.parquet`, `protoaccounts.parquet`, `groups.parquet`,
  `messages.parquet` — empty placeholders.

## Limits

- The blocks are synthetic, not the KC boundary or inventory.
- The canonical states are structural bins, not calibrated KC states.
- The clump rule is a DBH-ranked six-tree proxy, not spatial.
- No HMZ/UWR spatial constraint.
- No legal-compliance claim.
- It is not an optimization-ready KC dataset.

## Generator

`../../runbooks/compile_ws4_dataset.py` reads
`../state_library_v1/canonical/` and writes this directory.
