# Public benchmarks

This directory holds reviewed public-document benchmarks for the Knife Creek
model. They are not field data. Most are management-plan benchmarks; the
`mdwr_gwm2007_*` tables are direct extracts of the 2007 legal order and are
labelled as such.

## MWP #3 Figure 11 — target stand structure

| File | Purpose |
| --- | --- |
| `mwp3_figure11_target_stand_structure.csv` | Wide table: density and basal area by 5 cm DBH class for Low/Moderate/High. |
| `mwp3_figure11_target_stand_structure_long.csv` | Long table with source, extraction and review provenance. |
| `mwp3_figure11_target_stand_structure.metadata.json` | Calibration, extraction settings, Table 29 targets, recovered sums and caveats. |
| `mwp3_figure11_review.jsonl` | figrecover review entries; both series are `accepted`. |

Source: Alex Fraser Research Forest, *Management and Working Plan #3* (2007),
Figure 11, PDF page 97 (printed 89). Recovered with `figrecover` 0.1.0a1. The
reproduction script is `../../runbooks/recover_mwp3_figure11.py`; the method note
is `../../notes/reference/mwp3-figure11-recovery.md`.

The recovered basal-area sums are 17.02/22.96/30.17 m²/ha for
Low/Moderate/High, versus Table 29 targets of 16/22/29. The recovered density
distribution implies q-factors of 1.306/1.254/1.253, versus Table 29 values of
1.30/1.25/1.25. Use Table 29 for the residual B/D/q contract and Figure 11 for
the relative diameter distribution. Do not rescale the figure silently.

## MWP #3 Appendix 9 — compartment table

| File | Purpose |
| --- | --- |
| `mwp3_kc_compartments.csv` | KC01–KC11 and RD05–RD07 gross, non-productive, ESA, reserve, OGMA and net areas. |
| `mwp3_kc_compartments.metadata.json` | Source, page, reconciliation notes and caveats. |

Source: MWP #3 Appendix 9, PDF page 162 (printed 150). Gross 3,485.6 ha; net
3,162.3 ha. The source map is schematic and has no coordinate grid. This is a
table transcription, not a georeferenced GIS layer.

## 2007 GWM legal targets

| File | Purpose |
| --- | --- |
| `mdwr_gwm2007_targets.csv` | Legal stand-level BA >37.5 cm, D, q and large-tree reserve by habitat class. |
| `mdwr_gwm2007_clump.csv` | Legal clump (4–10+ mature trees), opening, cutting-cycle and 80% retention rules. |
| `mdwr_gwm2007_knife_creek_hmz.csv` | Knife Creek U-5-002 `dwl_50` HMZ 1–5 harvest classes. |

Source: *Amended Order #U-5-001, U-5-002 and U-5-003, Shallow and Moderate
Snowpack* (2007), Schedule 1 GWM 10, Tables 1–3. See
`../../notes/reference/mdwr-canopy-clump-requirements.md`.

The legal targets differ from MWP #3 Table 29: the order uses BA >37.5 cm
≥16/11/6 m²/ha and Table 2 D ≥70/60/50, while Table 29 uses D 60/55/50 and no
large-tree reserve. Table 29 is an AFRF interpretation, not the legal curve.

## Policy contract

`../../config/mdwr_regimes.yaml` holds both the AFRF Table 29 interpretation
(`habitat_classes`) and the legal 2007 GWM extraction (`legal_gwm_2007`).
`../../config/fvsbc/regimes.yaml` holds the FVS-BC `THINQFA` templates. The
current `habitat_classes` block is not a legal-compliance set.
