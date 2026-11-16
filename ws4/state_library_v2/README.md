# KC GWM state-transition library v2

Status: **provisional 4-entry GWM 2007 clump-reserve library**. Not a
compiled ws4 dataset, not KC-calibrated, and not a legal-compliance product.

## What changed from v1

v1 stopped after two entries, so every residual state was terminal. v2 follows
each of the eight PSP stands through four 30-year entries and writes the
resulting state graph. The four-entry graph is the first graph in this instance
that contains repeated canonical states and cycles.

## Files

| File | Purpose |
| --- | --- |
| `states.csv` | 120 per-chain initial and residual states |
| `transitions.csv` | 96 entries: 8 stands x 3 GWM classes x 4 entries |
| `curves.csv` | 384 interval curves |
| `benchmark.csv` | Regime-level residual-structure summary |
| `graph.json` | 120 nodes and 96 edges |
| `manifest.json` | Provenance, counts, and caveats |
| `canonical/` | Shared BA/QMD/large-tree/reserve classes and the canonical graph |

## Method

This is the v1 method extended to four entries:

1. Run a GWM full-range BDq cut at year 30.
2. Apply the DBH-ranked six-tree clump-reserve proxy.
3. Resample the residual list to a one-hectare population and grow it for the
   next 30-year entry.
4. Repeat for four entries.

The residual population is a weighted resample, not a measured KC tree list.
The clump is non-spatial. The BEC used for the FVS-BC `STDINFO` record is the
regional IDFdk3 analog, not a site-specific KC BEC call. Crown ratios are capped
at 0.89 because the FVS-BC crown-class field accepts classes 1–9; this is a
representation limit, not a field measurement.

## Canonical graph

`canonicalize_state_library.py` maps the 120 per-chain states to 32 shared
BA/QMD/large-tree/reserve classes. The canonical graph has 40 edges, four
cycles, and one terminal state. The cycles are the evidence that the graph can
carry repeated entries; they are not a yield guarantee.

## Limits

- PSP-derived regional IDF Cariboo analog, not Knife Creek CFI data.
- GWM 2007 basis; not a legal-compliance product.
- Clump reserve is a DBH-ranked six-tree proxy, not a spatial 4-10-tree clump.
- Four entries per chain. The canonical policy screen enters a reserve cycle
  after about 120 years and does not sustain harvest through 300 years.
- The UWR/HMZ spatial layer is not tested here.
- No KC calibration; FVS-BC is used structurally.

## Reproduction

```bash
PYTHONPATH=/path/to/fresh-fvsbc/src:/path/to/pyfvs/site-packages \
  python runbooks/build_state_library_v2.py \
  --sample data/psp/idf_cariboo_psp_stemlist_sample.csv \
  --out-dir ws4/state_library_v2 \
  --runtime-dir runtime/state_library_v2 \
  --entries 4

python runbooks/canonicalize_state_library.py \
  --library ws4/state_library_v2 \
  --out-dir ws4/state_library_v2/canonical
```
