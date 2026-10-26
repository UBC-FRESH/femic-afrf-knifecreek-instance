# ADR 0003: Data publication boundary

Status: accepted
Date: 2026-10-26

## Context

This is a public model instance. Knife Creek source data may include field
measurements, culturally sensitive locations, rare-species information, or
commercial detail. A layer is not public because it is technically readable.

## Decision

Publish the model logic, the configuration, the reviewed derived surfaces, and
the evidence. Do not publish private or restricted source data without a
recorded permission.

Published:

- documentation, ADRs, planning notes, and runbooks;
- the instance configuration and toolchain pin;
- data-acquisition manifests and checksums;
- reviewed stem-list manifests and their synthetic or measured status;
- FVS-BC keyword sets, run manifests, and derived state-transition tables;
- ws4 inputs and evidence; and
- reviewed scenario definitions and results.

Excluded:

- raw cost, revenue, contractor-rate, and cash-flow workbooks;
- private financial overlays;
- credentials, tokens, and keys;
- machine-specific paths and personal identifiers;
- raw field data without publication permission; and
- third-party documents that cannot be redistributed.

For a restricted source, publish the schema, the checksum of the private
source, the transformation, the derived public summary, and a contact path.
That preserves reproducibility without republishing the source.

## Consequences

- Every source needs a publication status before Phase 1 closes.
- A restricted source can still support a public model if its derived surface
  is releasable and the transformation is documented.
- The workflow validator is a mechanical check, not a permission check. The
  maintainer records the permission decision.
