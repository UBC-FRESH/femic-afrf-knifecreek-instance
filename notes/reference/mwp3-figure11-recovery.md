# MWP #3 Figure 11 recovery

## Purpose

Figure 11 of the Alex Fraser Research Forest *Management and Working Plan #3*
is the only public quantitative statement of the target diameter structure for
the Knife Creek mule-deer winter range. It complements Table 29, which gives the
residual basal area, maximum DBH, q-factor and cutting cycle for each habitat
class. The recovered table is a public benchmark for the FVS-BC selection
regimes and the ws4 state-transition library; it is not a legal order and it is
not observed plot data.

## Source

- Document: Alex Fraser Research Forest, *Management and Working Plan #3*,
  January 1, 2007.
- PDF: `reference/AFRF-management-working-plan-3-2007.pdf`.
- SHA-256: `9bfd8b8f0449f45fb97fcf529236640ace09b73ba74f77001f677eee7307ff6a`.
- Figure: Figure 11, PDF page 97, printed page 89.
- Caption: “Target stand structures by habitat class for the Knife Creek Mule
  Deer Winter Range, comparing density (stems/ha on left, basal area on right
  axis) by diameter class.”
- Policy table: Table 29, same page. High 29 m²/ha, D 60 cm, q 1.25; Moderate
  22 m²/ha, D 55 cm, q 1.25; Low 16 m²/ha, D 50 cm, q 1.30; 30-year cycle.

## Figure content

The chart has three density series (trees/ha, left axis, 0–140) and three basal
area series (m²/ha, right axis, 0.0–4.0), all by 5 cm DBH class from 5 to
70 cm:

| Habitat class | Density series | Basal-area series | Published maximum DBH |
| --- | --- | --- | --- |
| Low | yellow bars | magenta squares | 50 cm |
| Moderate | blue bars | cyan crosses | 55 cm |
| High | purple bars | dark-red circles | 60 cm |

The density bars are grouped around each class centre; the leftmost bar is Low,
the middle bar Moderate and the rightmost bar High. The basal-area lines use the
same class centres. There are no trees above each class maximum DBH, so the
recovered table records zeros there explicitly rather than treating the missing
bars as omissions.

## Method

1. Render page 97 at 300 dpi with PyMuPDF.
2. Crop the chart at pixel box `(300, 1550, 2200, 2400)`.
3. Mask the legend swatches at `(1345, 400, 1615, 610)`; the bars at the maximum
   DBH classes sit below the legend and remain visible.
4. Calibrate the plot frame at left 224, right 1802, top 88, bottom 716 px.
   The x-axis runs from 2.5 to 72.5 cm, with class labels at 5, 10, …, 70 cm.
5. Extract the three bar series with `figrecover` bar mode (yellow `#ffff00`,
   blue `#0000ff`, purple `#5f0080`).
6. Extract the three basal-area lines with `figrecover` line mode (magenta
   `#ff00ff`, cyan `#00ffff`, dark red `#800000`), then take the median y value
   within ±1.2 cm of each class centre.
7. Assign each bar to the nearest 5 cm class. Record zero beyond the published
   maximum DBH for that habitat class.
8. Inspect the figrecover overlay; accept only after the points follow the
   plotted bars and lines.

The extraction tool is `figrecover 0.1.0a1`. The reproduction script is
`runbooks/recover_mwp3_figure11.py`; it writes the reviewed tables and the
review manifest. Crops and overlays stay under `tmp/figrecover/`.

## Recovered table

The reviewed wide table is
`data/benchmarks/mwp3_figure11_target_stand_structure.csv`. The long table is
`data/benchmarks/mwp3_figure11_target_stand_structure_long.csv`; the metadata
and review records are beside them.

Recovered basal-area sums:

| Habitat class | Recovered sum (m²/ha) | Table 29 target (m²/ha) | Difference |
| --- | ---: | ---: | ---: |
| Low | 17.02 | 16 | +6.4% |
| Moderate | 22.96 | 22 | +4.4% |
| High | 30.17 | 29 | +4.0% |

The density distribution also implies a q-factor. Fitting a log-linear
density-diameter model over the published classes gives:

| Habitat class | Recovered q | Table 29 q |
| --- | ---: | ---: |
| Low | 1.306 | 1.30 |
| Moderate | 1.254 | 1.25 |
| High | 1.253 | 1.25 |

The q agreement is close. This is a shape check on the figure, not a
recalibration. The basal-area totals are slightly above Table 29 (about 4–6%),
but the relative diameter distribution and q are consistent with the policy
table.

Do not force the figure to close to Table 29. Table 29 is the AFRF
management-plan interpretation; GWM 2007 is the legal default. Figure 11 is the
published relative diameter distribution; it is slightly above the Table 29
totals, probably because the figure is a target schematic rather than a
normalized yield table. Use Table 29 for the AFRF comparison and Figure 11 for
the shape; report both when comparing FVS-BC output.

## Use in the model

- The default GWM 2007 cut sets the large-tree target from the legal order and
  the small-tree target from `B − large-tree BA`; Table 29 is the AFRF
  alternative. Neither uses the recovered sums as a target.
- The recovered per-class distribution is a benchmark for the post-treatment
  diameter distribution: compare the simulated residual trees/ha and basal
  area per 5 cm class with Figure 11.
- The maximum DBH and q-factor are checked against Table 29 and the shape of the
  recovered series.
- The figure does not test growth, ingrowth or mortality. It tests structure
  only. Growth and yield still require the AFRF CFI/private data or an approved
  VRI plus `nemora` reconstruction.

## Caveats

- The figure is a target diagram, not observed plot data.
- The chart has no uncertainty bands; recovered values are approximate to the
  plotted line and bar resolution.
- The legend obscures part of the plot area. The legend swatches were masked;
  the bars at the maximum DBH classes are below the legend and remain visible.
- The published figure is not normalized to Table 29. The differences are
  recorded, not corrected.
- The MWP #3 map on page 162 is a schematic planning map with a scale bar and
  north arrow but no coordinate grid. It is not the site-series map and it was
  not used to georeference this table.
- The legal UWR order text and the 2003 transition plan are acquired; the
  spatial UWR/HMZ layer remains outstanding. This table is public
  management-plan evidence, not a legal constraint. GWM 2007 is the default
  basis; Table 29 is the AFRF alternative.

## Verification

```bash
python runbooks/recover_mwp3_figure11.py --artifacts
python -m ruff check runbooks/recover_mwp3_figure11.py
```

The script should print basal-area sums of 17.02 / 22.96 / 30.17 m²/ha. Inspect
`tmp/figrecover/mwp3-figure11/overlay-density.png` and
`overlay-basal-area.png` before accepting a rerun.
