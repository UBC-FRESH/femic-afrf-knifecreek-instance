# Knife Creek management direction from MWP #3

## Source

Alex Fraser Research Forest, *Management and Working Plan #3*, January 1, 2007.
The plan is a public UBC AFRF planning document. It is committed at
`reference/AFRF-management-working-plan-3-2007.pdf` with SHA-256
`9bfd8b8f0449f45fb97fcf529236640ace09b73ba74f77001f677eee7307ff6a`.

The plan is the public AFRF statement of the Knife Creek mule-deer winter-range
(MDWR) management direction. It is not the legal Ungulate Winter Range order.
The 2007 shallow/moderate GWM order and the 2003 Knife Creek transition plan
have since been acquired; see `mdwr-canopy-clump-requirements.md` and
`mdwr-source-index.md`. The legal spatial UWR/HMZ GIS layer is still missing.

## Working circle

- Name: Knife Creek Mule Deer Winter Range.
- Gross area in Table 26: 3,333 ha, plus 152 ha reserves.
- Net productive area in Table 32: 3,117 ha.
- Appendix 9 compartment table: gross 3,485.6 ha, net 3,162.3 ha, after 48.3 ha
  non-productive, 125.5 ha environmentally sensitive, 64.4 ha reserve, and
  84.1 ha permanent OGMA.
- The public SUP legal boundary is 3,533.1341 ha. The differences among these
  figures are real vintage/boundary differences; do not reconcile them silently.
- Primary objective: mule-deer winter habitat on all compartments in the
  working circle.
- Silvicultural system: uneven-aged clumpy single-tree selection. GWM 10
  requires clumps of 4–10 or more mature trees with interlocking crowns; the
  maximum-diameter class is distributed in groups of 2–5 within those clumps.
  Cutting cycle: 30 years or more.
- BDq regulation: residual basal area (B), maximum DBH (D), and diminution
  quotient (q) by habitat class.
- Harvest opportunities are limited to Douglas-fir bark-beetle salvage and
  thinning, concentrating on trees below 37.5 cm DBH. Thinning treatments
  typically produce about 50 m³/ha.
- The plan intends a clumpy structure: the maximum diameter class is
  distributed among groups of 2–5 trees **within** the legal 4–10-tree mature
  clump. FVS-BC is distance-independent and cannot enforce the spatial
  grouping; that is a ws4/operability check or a post-processing constraint,
  not a tree-list keyword.

## Table 29 target structures

**Table 29 is an AFRF interpretation, not the legal GWM curve.** The legal order
requires D ≥70/60/50 cm and BA in stems ≥37.5 cm ≥16/11/6 m²/ha for
High/Moderate/Low. Table 29 uses D 60/55/50 and omits the legal large-tree
reserve. See `mdwr-canopy-clump-requirements.md` before treating these values
as compliance targets.

| Habitat class | Residual B (m²/ha) | Maximum DBH (cm) | q (5 cm classes) | Cutting cycle (years) |
| --- | ---: | ---: | ---: | ---: |
| High | 29 | 60 | 1.25 | 30 |
| Moderate | 22 | 55 | 1.25 | 30 |
| Low | 16 | 50 | 1.30 | 30 |

Figure 11 on the same page gives the relative diameter distribution by 5 cm
class for the same three classes. The recovered table is
`data/benchmarks/mwp3_figure11_target_stand_structure.csv`; its basal-area sums
are 17.02/22.96/30.17 m²/ha for Low/Moderate/High, slightly above the Table 29
targets. Use Table 29 for the residual target and Figure 11 for the shape, and
report both when comparing FVS-BC output.

## Area-based allowable cut

Table 35 gives the Knife Creek MDWR AAC:

- single-tree selection: 82.0 ha/year;
- salvage: 11.2 ha/year;
- total: 93.2 ha/year.

The 2001–2005 actual average was 44.3 ha/year partial cut plus 31.2 ha/year
salvage, total 76.1 ha/year, against an AAC of 93.2 ha/year. The plan attributes
the shortfall to the transition period and to the limited harvest opportunities.

The 82.0 ha/year selection AAC over 3,117 ha net is consistent with a 30-year
cycle (3,117 / 30 = 103.9 ha/year before constraints; the plan's AAC is lower
because of the MDWR constraints). Use 82.0 ha/year as the public policy
benchmark, not a CMAI-derived estimate.

## CCLUP compliance

Table 5 contrasts the CCLUP target with the plan's intended outcome for the
Knife Creek block:

| Harvest class | CCLUP target | Plan outcome |
| --- | ---: | ---: |
| Conventional harvest | 45% | 0% |
| Modified harvest | 50% | 95% |
| No harvest | 5% | 5% |

This is the public policy basis for the “no clearcut, continuous cover” rule.
It is a plan intention, not a legal order.

## Compartments

Appendix 9 (page 162 of the PDF, printed page 150) maps KC01–KC11 plus RD05–
RD07 and gives a compartment area table. The table is transcribed at
`data/benchmarks/mwp3_kc_compartments.csv`. The map is schematic: it has a north
arrow and a scale bar but no coordinate grid, so it is not a georeferenced GIS
layer. The compartment areas are useful for defining state-transition
aggregation units and for checking the net area; they are not a substitute for
the AFRF spatial data.

## What is still missing

1. The legal UWR boundary, stand-structure habitat classes and HMZ spatial GIS
   layer. The order and HMZ matrix text are acquired; the spatial layer is not.
2. The AFRF site-series map / CD-ROM GIS layer.
3. The AFRF CFI or an approved VRI plus `nemora` stem-list reconstruction.

The model may represent the public management direction and test structural
scenarios, but it must not claim legal policy compliance without (1) and the
current approved order.

## Maps at the back of the plan

The landscape-format appendix pages are public planning maps. They are useful
for compartment and harvest-unit context, but they are not georeferenced GIS
layers.

| PDF pages | Appendix | Content | Knife Creek page |
| --- | --- | --- | --- |
| 149–150 | 3 | Forest cover by leading species | 150 |
| 157–158 | 7 | Seral stage distribution | 158 |
| 161–162 | 9 | Compartments and planned harvest units | 162 |
| 163–164 | 10 | Timber harvest priorities | 164 |
| 165–166 | 11 | Road master plan | 166 |
| 167–168 | 12 | Research projects | 168 |

The Knife Creek page 162 map shows KC01–KC11, RD05–RD07, the MDWR habitat
classes (High/Moderate/Low/ESA), deferred areas, and the MDWR management zone.
It has a north arrow and a 0–3,000 m scale bar, but **no coordinate grid or
coordinate labels**. It cannot be georeferenced from the page alone without
control points from a known layer.

A defensible georeference would need at least:

- the SUP S15382 boundary as the outer control;
- road intersections or the lake shoreline as interior controls;
- the VRI polygon boundaries or cutblock corners as additional controls; and
- an explicit error report (control-point residuals and overlay review).

Until then, the page-162 table is transcribed in
`data/benchmarks/mwp3_kc_compartments.csv` and the map is treated as a
schematic planning figure. Do not present a warped page-162 raster as a
compartment or habitat layer.
