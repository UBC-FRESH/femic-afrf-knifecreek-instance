# KC GWM state-transition library v3

Status: **provisional 8-entry GWM 2007 clump-reserve library**. Not a
compiled ws4 dataset, not KC-calibrated, and not a legal-compliance product.

## What changed from v2

v2 followed four entries and counted only the FVS `RTCuM` selection cut. The
post-FVS clump harvest removed trees from the residual list but was not added
to the reported cut. v3 fixes both points:

- eight 30-year entries per stand/regime; and
- `fvs_cut_m3_ha` includes the post-FVS clump harvest volume.

The omitted clump volume was material: it turned an apparent zero-yield reserve
cycle into a sustained GWM cycle under the legal HMZ matrix.

## Files

| File | Purpose |
| --- | --- |
| `states.csv` | 216 per-chain states |
| `transitions.csv` | 192 entries |
| `curves.csv` | 768 interval curves |
| `benchmark.csv` | Regime-level residual-structure summary |
| `graph.json` | 216 nodes and 192 edges |
| `manifest.json` | Provenance, counts, caveats |
| `canonical/` | 35 canonical states, 48 canonical transitions, 2 cycles |

## Method

The FVS-BC GWM full-range BDq cut is followed by the DBH-ranked six-tree
clump-reserve proxy. The largest three trees above D in each six-tree chunk are
reserved; the remaining above-D trees are harvested. The residual list is
resampled to a one-hectare population and grown for the next 30-year entry.

The v3 cut volume is:

```text
FVS RTCuM + sum(clump-harvest tree TCuM * TPH)
```

## Limits

- PSP-derived regional IDF Cariboo analog, not Knife Creek CFI data.
- GWM 2007 basis; not a legal-compliance product.
- Clump reserve is a DBH-ranked proxy, not a spatial 4-10-tree clump.
- BEC for FVS `STDINFO` is the regional IDFdk3 analog.
- Crown ratios are capped at 0.89 for the FVS crown-class field.
- No KC calibration; FVS-BC is used structurally.

## Reproduction

```bash
PYTHONPATH=/path/to/fresh-fvsbc/src:/path/to/pyfvs/site-packages \
  python runbooks/build_state_library_v3.py \
  --sample data/psp/idf_cariboo_psp_stemlist_sample.csv \
  --out-dir ws4/state_library_v3 \
  --runtime-dir runtime/state_library_v3 \
  --entries 8

python runbooks/canonicalize_state_library.py \
  --library ws4/state_library_v3 \
  --out-dir ws4/state_library_v3/canonical
```
