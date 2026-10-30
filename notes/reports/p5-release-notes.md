# Knife Creek ws4 instance v0.1 release notes

Status: release candidate notes. Tag and publication are gated on maintainer
approval.

Release date: 2026-10-30

## What this release is

`v0.1` is a structural, runnable ws4 instance for the Knife Creek block of the
UBC Alex Fraser Research Forest. It is not a calibrated Knife Creek growth model
and it is not a legal-compliance product.

The release contains:

- a generated ForestModelXML recipe at
  `data/kc_ws4_recipe/forestmodel.xml`;
- matrix-builder fragments at `data/kc_ws4_recipe/fragments.csv`;
- a compiled ws4 dataset at `ws4/dataset_kc_v1`;
- HMZ, clump and reserve account groups;
- baseline and two selection-regime runs;
- reports, account audits, coverage and integrity evidence;
- a ws4 web service command.

## Model counts

| Object | Count |
| --- | ---: |
| Blocks | 160 |
| Fragments | 160 |
| Reachable track strata | 19 |
| Source scaffold tracks | 92 |
| Treatments | 19 |
| Curve ids / points | 651 / 6,661 |
| Feature rows | 114 |
| Product rows | 38 |
| Accounts | 8 |
| Groups / memberships | 12 / 800 |
| Topology pairs | 500 |
| Public road sections | 44 |
| Public road length | 59.6 km |

Model area is 3,481.773591 ha of net fragment area, not the gross SUP permit
area.

## What was verified

- `ws4 build` compiles the recipe and fragments.
- `ws4 validate --dataset ws4/dataset_kc_v1` passes.
- All 160 blocks appear in fragments, blocks, recipe fragments, source fragments
  and topology.
- Area reconciles across fragments, blocks, recipe and source.
- All 650 source curves reproduce in the compiled matrix; the extra curve is
  `unity`.
- Every feature/product curve reference resolves.
- Every treatment target exists; no clearcut treatment is present.
- Account audit reports zero missing target accounts.
- The baseline and GWM low/moderate regimes run for 30 years and report.

## Scenario snapshot

| Run | Scheduled blocks | Product yield (m³) | Residual BA (m²/ha) |
| --- | ---: | ---: | ---: |
| Baseline no cut | 0 | 0 | 67.44 |
| GWM low | 157 | 575,068 | 25.65 |
| GWM moderate | 157 | 546,223 | 27.62 |

These are structural comparisons. The smoke targets are zero-minimum wiring
checks, not policy outcomes.

## Run it

```bash
python runbooks/run_kc_ws4_pipeline.py \
  --xml data/kc_ws4_recipe/forestmodel.xml \
  --fragments data/kc_ws4_recipe/fragments.csv \
  --spatial-fragments data/patchworks_knifecreek/fragments.csv \
  --fragment-shapefile data/patchworks_knifecreek/spatial/fragments.shp \
  --dataset ws4/dataset_kc_v1 \
  --runtime ws4/runtime/kc_v1 \
  --evidence ws4/evidence/kc_v1
```

```bash
ws4 serve \
  --dataset ws4/dataset_kc_v1 \
  --runs ws4/runtime/kc_v1 \
  --targets ws4/targets_kc_smoke.yaml \
  --geometry ws4/runtime/kc_v1/kc_blocks.geojson \
  --topology ws4/topology.csv \
  --patch-accounts ws4/patch_accounts.yaml \
  --port 8766
```

## Known gaps and limits

### Growth evidence

- The model is not calibrated to Knife Creek. It is a structural instance built
  from the KC H matrix and public PSP-derived IDF Cariboo curves.
- The feature curves are 100-year space-for-time curves, not a Knife Creek
  growth chronology.
- Product yield curves are 30-year point estimates.
- The FVS-BC pilot is not a substitute for a KC CFI calibration.

### Missing accounts

- large-tree basal area;
- reserve basal area as a per-track curve;
- maximum DBH and q-factor;
- species-split softwood/hardwood structure;
- seral/opening area.

These are recorded as data gaps. They are not fabricated from total BA, QMD or
canopy.

### Spatial and road evidence

- The patch account uses managed area, not a seral/opening criterion.
- The public road layer is map context. Route configuration is explicitly
  unavailable because destination, eligibility, gate/bridge, and haul-cost
  inputs are missing.
- Topology is derived from block adjacency, not field-verified access.

### Legal and management status

- No current approved UWR order or legal stand-structure map is verified in this
  release.
- GWM 2007 is the default structural basis; AFRF Table 29 remains a named
  alternative.
- Nothing in this release is a legal-compliance determination or a reviewed
  management prescription.

### Runtime and data publication

- The raw PSP workbook and tree data remain private.
- The FVS-BC wrapper and its runtime prerequisites are documented separately.
  A clean checkout may not have the built FVS-BC variant available.
- The 92-track H scaffold is not a compiled-model count; only 19 strata are
  reachable from the current inventory and treatments.

## Release gate

Do not tag or publish this release until the maintainer approves the P5 closeout
and the clean-checkout report. The tag must point at the approved merged commit,
not at an unmerged branch.

## Evidence

- `notes/reports/p3-closeout.md`
- `notes/reports/p4-scenario-comparison.md`
- `notes/reports/p4-closeout.md`
- `notes/reports/p5-clean-checkout.md` (to be added by P5.3)
- `ws4/evidence/kc_v1/coverage_audit.json`
- `ws4/evidence/kc_v1/integrity_audit.json`
- `ws4/evidence/kc_v1/account_audit.json`
- `ws4/evidence/kc_v1/scenario_manifest.json`
- `ws4/evidence/kc_v1/scenario_reports/`
