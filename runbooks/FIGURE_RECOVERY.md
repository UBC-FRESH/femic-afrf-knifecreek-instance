# Figure recovery runbook

Use `figrecover` only for figures whose source table was not published. The
result is an approximate recovery with explicit provenance, not a precision
measurement. Review the overlay before any value enters a model input.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install 'figrecover[pdf,cv]'
```

`figrecover` is a public UBC-FRESH package. The current repository does not
make it a runtime dependency; the recovery script is an optional reference
workflow.

## Recover MWP #3 Figure 11

```bash
python runbooks/recover_mwp3_figure11.py --artifacts
```

The script:

1. renders page 97 of
   `reference/AFRF-management-working-plan-3-2007.pdf` at 300 dpi;
2. crops Figure 11 and masks the legend;
3. calibrates the plot frame and runs figrecover bar and line extraction;
4. writes the wide and long tables, metadata, and review manifest under
   `data/benchmarks/`;
5. writes the crop and overlays under `tmp/figrecover/mwp3-figure11/` when
   `--artifacts` is set.

Inspect both overlays. The recovered points should sit on the bar tops and on
the plotted lines. Do not mark a table accepted if the overlay is shifted, if a
series is missing, or if the legend has been treated as data.

## Review rules

- Prefer a published table over a figure. Figure 11 is a target diagram; Table
  29 is the authoritative residual basal-area/D/q contract.
- Record the source document, page, figure, calibration, extraction tool and
  version, crop box, legend mask, and review status.
- Record zeros beyond a published maximum DBH explicitly; do not leave them
  blank and do not infer them from the absence of a bar.
- If the recovered values do not close to a published total, record the
  difference. Do not silently rescale the figure.
- Keep crops, rendered pages, overlays, and raw review bundles under `tmp/`.
  Commit only the reviewed table, metadata, review manifest, and note.
- Do not use a schematic map without a coordinate grid as a georeferenced GIS
  layer. Treat it as a planning-map transcription until control points from a
  known layer are available.

## Other candidate figures

The AFRF Management and Working Plan #3 also contains harvest-area and harvest-
volume charts (Figures 5, 12, 13 and 14). They are forest-wide or working-circle
summaries; the text tables (Tables 32, 35 and 36) already give the KC/GL AAC
values. Prefer the tables for model targets and use the figures only as a
visual cross-check. The Klinka 2004 report's quantitative content is in its
site-index tables (8.2.1–8.2.4), not in its photo figures; those tables are
transcribed in `data/site_index/klinka_2004_site_index.csv`.
