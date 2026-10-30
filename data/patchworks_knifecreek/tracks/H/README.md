# Knife Creek H matrix scaffold

Status: **scaffold; curves cover 30 years, not 300.**

Generated from `ws4/dataset_kc_spatial_v3`.

## Tables

- 160 blocks
- 92 tracks
- 49 treatments
- 174 curves, 549 points
- 147 feature rows
- 49 product rows
- empty accounts/protoaccounts (P3.4)
- 160 groups

`ws4 ingest --matrix data/patchworks_knifecreek/tracks/H --fragments data/patchworks_knifecreek/fragments.csv` succeeds, and `ws4 validate` passes.

## Limits

- Curves are years 0–30 only. The 300-year extension is not generated and is
  not simulated by repeating the 30-year curve.
- Product and feature accounts are not yet wired.
- No roads, patch accounts, pin or ForestModelXML.
- No clearcut treatment.
- The source library is structural and PSP-derived, not KC-calibrated.

## Generator

`runbooks/build_kc_patchworks_h.py`
