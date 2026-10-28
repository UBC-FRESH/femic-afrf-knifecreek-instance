# KC spatial structural ws4 dataset v1

Status: **spatial structural fixture**, not a KC operating model and not a
legal-compliance product.

## What it is

A ws4 compiled dataset built from:

- clipped VRI 2025 polygons as blocks;
- the canonical GWM 2007 graph;
- the Knife Creek HMZ layer;
- PSP-derived initial canonical states.

## Counts

- **160 blocks**; 3,481.77 ha after the VRI/BA filter;
- **92 tracks** — 23 canonical states × 4 HMZ groups;
- **49 treatments**;
- HMZ groups: **M 113 blocks, L 44 blocks, U 3 blocks**;
- no A-group blocks inside the filtered VRI set.

## HMZ enforcement

Track copies restrict the treatment offers:

- `M` (HMZ 1/3/4): `GWM_LOW`, `GWM_MODERATE`;
- `L` (HMZ 2): `GWM_LOW` only;
- `A` (HMZ 5): all classes;
- `U` (outside HMZ): no treatments.

A block is assigned to the HMZ group of its dominant HMZ area share. That is a
summary, not a legal interpretation.

## Validation

```bash
PYTHONPATH=/srv/shared-data/gep/ws4/ws4 \
  python -m ws4.cli validate --dataset ws4/dataset_kc_spatial_v1
```

Result: **Dataset is valid**.

## Limits

- Blocks are clipped VRI polygons, but the tree lists are still the PSP-derived
  regional analog, not KC CFI.
- Initial states are assigned by nearest BA/QMD class, not measured.
- The clump rule is a DBH-ranked six-tree proxy, not spatial.
- HMZ track offers enforce the matrix structurally, but do not verify the
  current approved order or the legal stand-structure map.
- Three blocks outside the HMZ polygons have no treatments.
- Not optimization-ready as a KC operating model.

## Generator

`../../runbooks/compile_kc_spatial_dataset.py`.
