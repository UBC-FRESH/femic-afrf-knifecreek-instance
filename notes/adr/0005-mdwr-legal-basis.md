# ADR 0005: GWM 2007 is the default Knife Creek MDWR basis

Status: accepted
Date: 2026-10-27
Issues: #35

## Context

The first Knife Creek structural work used MWP #3 Table 29: B 29/22/16 m²/ha,
D 60/55/50 cm, q 1.25/1.25/1.30, and clumps of 2–5 trees at the maximum
diameter. That was a public management-plan interpretation, not the legal
Ungulate Winter Range order.

The 2007 Amended Order #U-5-001/U-5-002/U-5-003, Shallow and Moderate
Snowpack, and the 2003 Knife Creek transition plan have now been acquired. The
legal order differs in three material ways:

1. GWM 10 requires clumps of **4–10 or more mature trees with interlocking
   crowns**. The 2–5 figure in MWP #3 is only the maximum-diameter subgroup.
2. The stand-level large-tree target is **BA ≥37.5 cm**, not ≥50 cm:
   High ≥16, Moderate ≥11, Low ≥6 m²/ha.
3. GWM 10 Table 2 uses **D ≥70/60/50 cm** for High/Moderate/Low and allows a
   large-tree reserve above D. Table 29 uses D 60/55/50 and no reserve.

The user decided that the legal basis should be the default, Table 29 should
remain a named AFRF alternative, and surplus large trees above the legal
minimum may be harvested.

## Decision

The Knife Creek model has one default policy basis, **`GWM_2007`**, and one
named alternative, **`AFRF_MWP3_TABLE29`**.

Default GWM 2007 contract:

- legal stand targets: B 29/22/16; BA >37.5 ≥16/11/6; D ≥70/60/50;
  q 1.20–1.35/1.25–1.35/1.25–1.40; reserve 0–2.9/0–2.2/0–1.6 above D;
- clumps of 4–10 or more mature trees with interlocking crowns;
- maximum-diameter subgroup of 2–5 trees within the clump;
- canopy openings 0.3–1.0 mature tree heights, mean 0.5;
- cutting cycle ≥30 years;
- before 2026, retain ≥80% of pre-harvest merchantable Douglas-fir BA;
- Knife Creek HMZ 1–5 = M, L, M, M, A;
- surplus large trees above the minimum large-tree BA are harvestable. The
  default treatment is a split cut: `THINABA` above 37.5 cm to the minimum
  large-tree BA, then `THINQFA` on 0–37.5 cm to `B − large-tree BA`.

The Table 29 alternative keeps B 29/22/16, D 60/55/50, q 1.25/1.25/1.30 and
the 2–5 maximum-diameter subgroup. It is an AFRF management-plan scenario and
must never be reported as legal compliance.

The basis is part of the state-transition contract. Do not mix GWM and Table 29
states in one graph or one optimization run without an explicit basis label.

## Consequences

- `config/mdwr_regimes.yaml` exposes `default_basis: GWM_2007` and
  `AFRF_MWP3_TABLE29` as an alternative.
- `config/fvsbc/regimes.yaml` puts the GWM split regimes first and the Table 29
  regimes under `afrf_table29_regimes`.
- The existing `ws4/state_library_v0` is a **legacy Table 29** library. It is
  not the default basis and must not be compiled as legal compliance.
- A new legal-basis library should be `state_library_v1` with `basis=GWM_2007`.
- Clump post-processing uses 4–10 trees; 2–5 is the maximum-diameter subgroup.
- The HMZ spatial layer is acquired and clipped to the SUP; the current
  approved order and legal stand-structure map still need verification for a
  compliance claim.

## Alternatives considered

- **Keep Table 29 as the default.** Rejected: it is not the legal order and
  understates the large-tree diameter requirement.
- **Use both bases as equal defaults.** Rejected: states would be mixed and the
  legal question would be ambiguous.
- **Retain every tree above D.** Rejected by the user's decision; surplus large
  trees above the legal minimum may be harvested. A retain-all variant remains
  available as a sensitivity.
