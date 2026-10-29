# KC PSP partial ws4 transition generator v1

Status: **partial generator**. It produces structural curves, not a compiled
ws4 dataset.

The generator starts from each 1993 PSP plot, applies the tree-level growth and
survival models for 30 years in five-year steps, and adds ingrowth from an
explicit block/treatment scenario.

## Outputs

- `transitions.csv` — 24 start states, end state at year 30, ingrowth scenario.
- `curves.csv` — 168 rows: 24 transitions × 7 points (years 0–30).
- `ingrowth_scenarios.json` — observed block/treatment counts and recruit-size
  summaries.
- `manifest.json` — scope and caveats.

Generated curves:

- BA (m²/ha)
- TPH
- QMD (cm)
- large-tree BA (m²/ha)

Not generated: volume, canopy cover, treatment response, products.

## Ingrowth

Ingrowth is not a fitted equation. The scenario file stores:

- expected recruits per five years by block/treatment;
- recruit mean and RMS DBH;
- the observed count of recruits used.

The generator adds the expected recruits as one weighted entry per five-year
step. This is a reconstruction scenario, not a transferable forecast.

## Limits

- No 30-year observed validation exists; the models were fitted to 4–7-year
  intervals and the 30-year projection is an extrapolation.
- The growth/survival models have only block-level transfer tests.
- The generator does not produce a complete ws4 curve set; volume and canopy
  are missing.
- No age or site index is assigned.
- No treatment response is generated.
- Raw tree records remain private.

## Files

- `transitions.csv`
- `curves.csv`
- `ingrowth_scenarios.json`
- `manifest.json`
- Generator: `runbooks/generate_psp_transitions.py`

## Next

Either supply the missing volume/canopy curves from an independent, documented
allometry, or use this as a structural scenario library only. Do not present it
as a compiled ws4 dataset.
