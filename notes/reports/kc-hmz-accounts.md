# KC HMZ-specific feature accounts

Status: structural account layer; not a legal-compliance determination.

## What was added

The AU stage recipe now emits group-specific feature labels in addition to the
aggregate labels:

- `feature.habitat.large_tree_ba.<AU>.<HMZ>`
- `feature.habitat.reserve_ba.<AU>.<HMZ>`
- group-specific yield/area labels as well

The 13 populated AU/HMZ groups are recorded in
`ws4/targets_kc_mdwr_hmz.yaml`.

## Targets

`ws4/targets_kc_mdwr_hmz.yaml` carries final-period structural large-tree floors:

- HMZ M: 11 m²/ha
- HMZ L: 6 m²/ha
- HMZ U: 0

The reserve account is wired at a zero minimum; the legal reserve constraint is
a maximum and is not represented by this file yet.

## Verification

- `ws4/dataset_kc_au_stages_v1` validates.
- 115 tracks, 1840 feature rows, 112 feature labels.
- HMZ target probe resolves all 26 targets.
- Web API exposes 124 accounts including the 13 large-tree and 13 reserve group
  labels.

## Limits

The reserve curve uses the non-spatial DBH-ranked six-tree proxy, not the legal
spatial 4–10-tree clump rule. No calibration or legal-compliance claim.
