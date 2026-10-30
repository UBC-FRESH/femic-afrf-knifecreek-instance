# KC large-tree BA extraction

Status: extracted for the AU no-cut curve set; not yet wired into the compiled
stage graph.

## What was added

`data/psp/kc_au_200y/kc_au_yield_200y.csv` now carries:

- `large_ba_m2_ha` — live-tree BA for DBH >= 37.5 cm
- `large_tph` — live trees >= 37.5 cm

The values come from the FVS tree-list output, requested at each 10-year cycle.

## Result

- 6 AUs
- 126 curve rows
- 0–200 years
- large-tree BA at year 200: 46.5–64.5 m²/ha depending on AU

## Not done

- Large-tree BA is not yet a compiled `feature.habitat.large_tree_ba` account
  in the stage graph.
- Reserve BA is not yet added. It needs the clump-reserve marking rule applied
  to the after-treatment tree list; total large-tree BA is not reserve.

No KC calibration or legal-compliance claim.
