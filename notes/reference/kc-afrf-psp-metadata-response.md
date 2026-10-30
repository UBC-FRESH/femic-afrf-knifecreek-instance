# AFRF KC PSP metadata response

Source: P. Marshall, pers. comm., 2026-10-29. This is a public-safe summary; the
raw correspondence is not tracked.

## Confirmed

- Plot area 0.05 ha; expansion 20 for `P = I`.
- `P = I` is the plot population; `P = B` is the buffer/border population.
- The plot population is living trees >1.3 m tall.
- DBH is cm; height and crown dimensions are m.
- `X` and `Y` are **metres from the plot centre**, not feet.
- `V = 0` is dead; `V = 1/2/3` is low/moderate/good vigor. Vigor was not used
  in Marshall's analyses.
- `LC1–4` are live-crown base heights in four quarters; crown ratio is
  `(HT - mean(LC)) / HT` after a range check.
- `CW1`/`CW2` are perpendicular crown diameters.
- 2013 is post-growing-season; earlier measurements are pre-growing-season.
  Growth intervals are 4, 7, 4 and 5 years.
- A 2024 remeasurement exists but was not in the supplied workbook.
- The 2020 paper uses 16 Block C/D plots because it focuses on conifer growth;
  Block B is mainly Douglas-fir.
- `TS` and `TC` are 2013 Ministry of Forests codes; Marshall does not have a
  current definition. They can be ignored for this analysis.
- `HT13` is 2013 tree height in m.
- `CW1-93.1` is a typo for the first 1993 crown-width column.
- Trees that die in a growth period are not included in the measurements at the
  end of that period. Ingrowth appears in its first measured interval with a
  unique tree number and is included in both plot and buffer records.
- Only trees >10 cm DBH are included in the plot buffers.
- `W` means willow; there are only a few occurrences.
- GPS coordinates for plot centres should be available from AFRF. The block and
  treatment layout was run by AFRF and may also be available as a map or
  coordinates.
- Raw-workbook publication is not Marshall's decision.

## Still unresolved

- `D1`, `D2`, `DA`, `DS`, `WTA` definitions.
- Exact `TS`/`TC` code tables.
- Absolute plot centres, block polygons and treatment polygons.
- The 2024 remeasurement data.
- Raw-workbook publication clearance.

## Pipeline impact

- Remove the feet-to-metres conversion from the ingest.
- Stem-map distances can be used directly in metres once the centre is known.
- The 2013-only status codes are not a mortality source; DBH presence remains
  the working live-tree indicator.
- A future 2024 acquisition would add a 2013-2024 remeasurement and a stronger
  validation interval.
