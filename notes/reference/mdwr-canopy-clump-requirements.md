# MDWR canopy-closure and clump requirements

Status: source review. This note replaces the earlier assumption that the
Knife Creek clump target was 2–5 trees. The legal clump target is **4–10 or
more mature trees with interlocking crowns**. The 2–5 figure in MWP #3 refers
to the maximum-diameter class, not to the whole clump.

## Sources

Local source set: `/srv/shared-data/gep/ws4/sources/afrf-mule-deer/`.
The repo keeps citations and extracted requirements; the PDFs stay outside git.

- **GWM order**: *Amended Order #U-5-001, U-5-002 and U-5-003 — Ungulate
  Winter Ranges, Cariboo Chilcotin Land Use Plan, Shallow and Moderate
  Snowpack* (signed February 2007), 15 pp. Knife Creek is U-5-002 `dwl_50`.
- **Part 1a**: Dawson et al. 2007, *Management Strategy for Mule Deer Winter
  Ranges in the Cariboo-Chilcotin, Part 1a: Management Plan for Shallow and
  Moderate Snowpack Zones*, LMH 60, 58 pp.
- **Part 1b**: Dawson et al. 2006, *Part 1b: Management Plan for Transition and
  Deep Snowpack Zones*, LMH 59, 44 pp.
- **Part 3**: CCLUP Mule Deer Strategy Committee 2003, *Part Three: Transition
  Period Harvest Opportunities: Knife Creek*, 2 pp.
- **EN25A**: Dawson and Armleder 2000, *Structural Definitions for Management
  of Mule Deer Winter Range Habitat in the Interior Douglas-fir Zone*,
  Extension Note #25A, 8 pp.
- **LMH 13**: Armleder, Dawson and Thomson 1986, *Handbook for Timber and Mule
  Deer Management Co-ordination on Winter Ranges in the Cariboo Forest
  Region*, 108 pp.
- **MWP #3**: AFRF *Management and Working Plan #3*, January 1, 2007, 168 pp.
- **FSP 2007**: AFRF *Forest Stewardship Plan 2007–2012*, 55 pp.

## 1. The legal clump requirement

GWM 10, Schedule 1, p. 5:

> A clumpy distribution of Douglas-fir trees, with clumps containing 4–10 or
> more mature trees with interlocking crowns.

The same measure requires small canopy openings with a diameter of 0.3–1.0
times the height of mature trees, average 0.5 times mature tree height, a
minimum 30-year cutting cycle, no material adverse damage to residual trees,
and skid trails covering no more than 10% of the net harvested area in high or
moderate stands.

Part 1a p. 12 states the same management objective:

> Clumps would ideally contain four to 10 or more mature trees with
> interlocking crowns.

This is the legal/management clump unit. It is **not** 2–5 trees.

### Why MWP #3 says 2–5

MWP #3 p. 87 says:

> We intend to manage the stands in a clumpy fashion, such that the maximum
> diameter class is distributed amongst groups of 2–5 trees.

That is a statement about the **maximum-diameter class**, not the whole
residual clump. It is compatible with a 4–10-tree mature clump: the largest
trees are grouped 2–5 within the larger interlocking-crown clump. The model
must not reduce the whole clump to 2–5 trees.

## 2. Stand-level basal-area targets

GWM 10, Tables 1 and 2, pp. 6–7; EN25A Tables 2 and 3, pp. 3–6.

| Habitat class | Total BA ≥12.5 cm (m²/ha) | BA in stems ≥37.5 cm (m²/ha) | D (cm) | q (5 cm classes) | Large-tree reserve >D (m²/ha) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Low | ≥16 | ≥6 | ≥50 | 1.25–1.40 | 0–1.6 |
| Moderate | ≥22 | ≥11 | ≥60 | 1.25–1.35 | 0–2.2 |
| High | ≥29 | ≥16 | ≥70 | 1.20–1.35 | 0–2.9 |

These are the IDFdk3/IDFdw values; IDFxm/xw has a lower high-class total
(`≥27`) and D (`≥65`). Knife Creek is IDFdk3/IDFdw, so use the IDFdk row.

Important consequences:

- The large-tree target is **≥37.5 cm DBH**, not 50 cm.
- High and moderate **D** are ≥70 and ≥60 cm in the legal order.
- The legal targets allow a large-tree reserve of trees above D, outside the
  BDq curve.
- Crown closure is not the stand-level defining attribute. EN25A p. 2 says
  explicitly that at the stand level the descriptors are total BA, BA >37.5 cm,
  percent Douglas-fir, and BDq/stand-structure. Crown closure is a
  regional/landscape descriptor.

## 3. Landscape crown-closure classes

LMH 13 pp. 24–25 defines crown closure using trees >10.4 m tall and older age
classes:

| Habitat class | Crown closure |
| --- | ---: |
| Low | 16–35% |
| Moderate | 36–65% |
| High | >65% |

LMH 13 p. 31 gives approximate winter-range proportions:

| Snowpack zone | Low | Moderate | High |
| --- | ---: | ---: | ---: |
| Shallow | ~40% | ~40% | ~20% |
| Moderate | ~33% | ~33% | ~33% |
| Deep | ~33% | 0% | ~66% |

These are landscape/regional composition targets, not a per-stand canopy
closure prescription. Do not turn “high habitat” into a simple 65% crown-cover
target at the stand scale; the legal stand-level test is the BA table plus the
4–10-tree clump and canopy-opening pattern.

## 4. Knife Creek transition and habitat-management zones

Part 3 (2003) is the Knife Creek transition plan. It is 2 pp and refers to
Part 1a Table 4.2 for stand-level objectives. The legal order Table 3, p. 7,
gives the Knife Creek row for U-5-002 `dwl_50`:

| Habitat management zone | 1 | 2 | 3 | 4 | 5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Knife Creek `dwl_50` | M | L | M | M | A |

Codes: `L` = potential harvest only in areas designated Low; `M` = Low or
Moderate; `A` = all areas, managed to the designated High/Moderate/Low
objective; `X` = no harvest; `P` = park/protected.

Thus HMZ 2 is Low-only, HMZ 1/3/4 are Low-or-Moderate, and HMZ 5 is all
classes. The model must carry the HMZ as a spatial constraint; a stand-level
BDq run alone cannot establish legal compliance.

The order also states, at p. 2 para. 5, that the GWMs do not apply to primary
forest activities over >10 ha in the Moderate Snowpack zone where ≥70% of the
area is north-facing (315°–60°) with slope >20%, in listed UWRs including
Knife Creek. This is a potential exemption, not a default. It requires the
spatial order/GIS layer and an explicit area test.

## 5. Transition-period harvest limits

GWM 13, p. 7: before 2026, GWM 10 harvesting must retain at least **80% of the
pre-harvest merchantable Douglas-fir basal area**. Part 1a Table 1 (Harvest
Type 5) repeats the 80% rule and a minimum 30-year cutting cycle. The legal
order also requires clumpy single-tree selection, 4–10-tree clumps, small
openings, and ≤10% skid-trail area in high/moderate stands.

The 2007 FSP adds the AFRF operational interpretation: single-tree selection
removes ≤20% of pre-harvest BA; residual leave trees are distributed throughout
the standards unit but in a clumpy pattern; and the maximum-diameter class is
left in groups of 2–5 trees.

## 6. Discrepancy with MWP #3 Table 29

MWP #3 Table 29 uses:

| Habitat class | B (m²/ha) | D (cm) | q |
| --- | ---: | ---: | ---: |
| High | 29 | 60 | 1.25 |
| Moderate | 22 | 55 | 1.25 |
| Low | 16 | 50 | 1.30 |

The total BA values match the legal minima, but the **D values do not**:
the order Table 2 values are High D ≥70, Moderate D ≥60, Low D ≥50, and GWM 10
requires the residual curve to be consistent with Table 2. Table 29 also omits
the legal large-tree reserve and the ≥16/11/6 m²/ha BA >37.5 cm targets.

Therefore:

- Table 29 is the AFRF management-plan interpretation, not the legal GWM
  contract.
- A model run using Table 29 must be labelled an AFRF interpretation, not a
  legal-compliance scenario.
- A legal-basis run should use GWM Table 1/2: B 29/22/16, BA >37.5 ≥16/11/6,
  Table 2 D ≥70/60/50, q 1.20–1.35/1.25–1.35/1.25–1.40, reserve
  0–2.9/0–2.2/0–1.6.

This discrepancy is a model decision for the user: preserve Table 29 as the
AFRF target, add a separate legal GWM regime set, or make the basis an explicit
scenario axis.

## 7. What the model should expose

At minimum:

- `policy_basis`: `GWM_2007` or `AFRF_MWP3_TABLE29`;
- `large_tree_min_dbh_cm`: 37.5 for GWM, 50 for the current policy pilot;
- `large_tree_ba_m2_ha`: legal minima 6/11/16 at 37.5 cm;
- `B`, `D`, `q`: separate GWM and Table 29 sets;
- `large_tree_reserve_m2_ha`: 0–2.9 above D;
- `clump_min_trees`: 4; `clump_max_trees`: 10+; `max_dbh_group_size`: 2–5;
- `opening_diameter_tree_heights`: 0.3–1.0, mean 0.5;
- `cutting_cycle_years`: ≥30;
- `transition_ba_retention`: ≥0.80 before 2026;
- `hmz` and `hmz_harvest_class`: L/M/A/X/P, with the Knife Creek matrix.

The earlier `policy_pilot_v0` used a 50 cm large-tree threshold and 2–5 tree
clumps. It remains a useful structural pilot, but it is **not** the legal GWM
clump geometry. New scenarios should use 4–10+ mature trees and should report
the max-D subgroup separately.
