# ADR 0006: Use the AFRF Knife Creek PSP dataset as the field-data candidate

Status: proposed pending AFRF/PSP QC
Date: 2026-10-28
Issues: #7

## Context

The AFRF Knife Creek permanent-sample-plot (PSP) workbook is now available. It
is the tree-level field dataset previously described imprecisely as the “KC
CFI.” It is not a confirmed formal CFI, and the workbook has no separate data
dictionary. It contains 24 plots, five measurements (1993, 1997, 2004, 2008,
2013), stem-map coordinates, species, DBH, height, crown dimensions and vigor.

The plot design is described in FRDA Report 242 (Marshall 1996) and Acquah and
Marshall (2020), *Forests* 11:167, Methods 2.1: 24 permanent 0.05 ha plots,
three blocks (B/C/D), four pre-commercial-thinning treatments, two plots per
treatment, with border trees >10 cm DBH tagged within 5 m outside the plot
boundary. FRDA 242 confirms the rectangular plot dimensions (15.81 × 31.62 m),
the plot/block/treatment mapping, the `P = I/B` meaning, and the vigor,
crown-diameter and live-crown-base measurement definitions.

The raw workbook is not committed. Its SHA-256 is
`6d958ca93364e424ad41380da87c5f6da1e5ce5ce4fbd762226286d748a82ded`.
The paper PDF is in the workspace source set, not the repo.

## Decision

Treat the AFRF KC PSP workbook as the **primary field-data candidate** for
Knife Creek, subject to the assumptions and QC questions in
`notes/reference/kc-afrf-psp-dataset.md`.

For any derived product:

- use `P = I` as the plot population for density/BA; FRDA 242 confirms that
  buffer-strip tree numbers were followed by `B`;
- treat `P = B` as border/competition context, not plot area;
- use 0.05 ha and the 15.81 × 31.62 m rectangle from FRDA 242;
- treat X/Y as feet from plot centre only as a strong inference, not a
  documented header;
- do not join the plots to VRI, HMZ or LiDAR until absolute plot centres are
  supplied;
- do not call the plots a formal CFI or a random sample of the block;
- keep the raw workbook out of git until publication permission is confirmed;
- commit only the schema, checksum, transformation and derived public
  summaries if the raw data are not cleared.

## Consequences

This dataset can replace the regional IDF Cariboo PSP analog for the plots'
stand types, and gives repeated measurements for growth, mortality, ingrowth
and spatial clump work. It does not represent the whole Knife Creek block by
itself: it is a 24-plot thinning experiment concentrated in three blocks, and
the paper's competition analysis uses only the 16 Block C/D plots.

Most design metadata is now source-backed. The remaining unresolved fields are
`TS`, `TC`, `D1/D2/DA/DS/WTA`, `HT13`, the duplicate `CW1-93.1`, and the exact
X/Y conversion. They must be corrected from AFRF metadata, not silently
“fixed” in the model.

## Alternatives considered

- **Continue using the regional PSP analog only.** Rejected: real KC tree data
  are available.
- **Treat the workbook as a ready CFI.** Rejected: no data dictionary, no
  confirmed `P` code, no absolute plot coordinates, and no publication
  clearance.
- **Commit the raw workbook now.** Rejected until AFRF/PSP custodians confirm
  release.
