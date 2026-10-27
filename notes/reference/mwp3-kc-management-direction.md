# Knife Creek management direction from MWP #3

## Source

Alex Fraser Research Forest, *Management and Working Plan #3*, January 1, 2007.
The plan is a public UBC AFRF planning document. It is committed at
`reference/AFRF-management-working-plan-3-2007.pdf` with SHA-256
`9bfd8b8f0449f45fb97fcf529236640ace09b73ba74f77001f677eee7307ff6a`.

The plan is the best public statement of the Knife Creek mule-deer winter-range
(MDWR) management direction. It is not the legal Ungulate Winter Range order,
and it is not the 2003 Knife Creek transition strategy. Those remain outstanding
in P1.2a.

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
- Silvicultural system: uneven-aged single-tree selection, with small groups of
  2–5 trees at the maximum diameter. Cutting cycle: 30 years.
- BDq regulation: residual basal area (B), maximum DBH (D), and diminution
  quotient (q) by habitat class.
- Harvest opportunities are limited to Douglas-fir bark-beetle salvage and
  thinning, concentrating on trees below 37.5 cm DBH. Thinning treatments
  typically produce about 50 m³/ha.
- The plan intends a clumpy structure: the maximum diameter class is distributed
  among groups of 2–5 trees. FVS-BC is distance-independent and cannot enforce
  the spatial grouping; that is a ws4/operability check or a post-processing
  constraint, not a tree-list keyword.

## Table 29 target structures

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

1. The approved Ungulate Winter Range boundary and the legal mule-deer
   objective/order.
2. The CCLUP Mule Deer Strategy Committee (2003) *Transition period harvest
   opportunities: Knife Creek* (3 pp), which the plan cites for the transition
   strategy.
3. The AFRF site-series map / CD-ROM GIS layer.
4. The AFRF CFI or an approved VRI plus `nemora` stem-list reconstruction.

Until (1) and (2) are obtained, the model may represent the public management
direction and test structural feasibility, but it must not claim legal policy
compliance.
