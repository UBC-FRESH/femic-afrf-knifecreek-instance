# Knife Creek Patchworks-compatible package

Status: **intermediate ws4 source tables; this is not a Patchworks model.**

## Contents

| File | Purpose |
| --- | --- |
| `spatial/fragments.shp` | 160 VRI blocks clipped to SUP S15382, EPSG:3005 |
| `fragments.csv` | Derived fragment attributes |
| `spatial/topo_fragments.csv` | Block pair distances and shared boundary lengths |
| `spatial/roads.gpkg` | 44 public BC Forest Tenure road sections, clipped to SUP |
| `analysis/patch_accounts.yaml` | Structural adjacency patch account |
| `../../ws4/targets_kc_smoke.yaml` | Runnable smoke targets |
| `../../ws4/targets_kc_gwm2007.yaml` | Draft GWM structural targets, not legal compliance |
| `tracks/H/` | 160 blocks, 92 tracks, 49 treatments, feature/product curves |

## Keys and features

- `RES_KEY` / `BLOCK` — stable block id, 1–160
- `TRACK` — initial ws4 state track
- `POLY_ID` — VRI polygon id
- feature curves: BA, QMD, TPH, canopy, volume, area
- product curves: area and point yield

## Limits

- Patches are currently based on managed area, not a seral/opening feature.
- No road route configuration or haul cost yet.
- Product yield curves are point estimates from the existing GWM runs.
- Feature curves are 100-year regional space-for-time FVS-BC projections, not KC chronology.
- No ForestModelXML; see `../../notes/reference/patchworks-forestmodelxml-format-spike.md`.
- No legal-compliance claim.
