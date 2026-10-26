# Metadata

Provenance ledgers for the Knife Creek instance.

Files:

| File | Purpose | Status |
| --- | --- | --- |
| `data_sources.csv` | Source, owner, licence, status, checksum | boundary row recorded |
| `boundary_source.yaml` | Boundary provenance, fetch command, area reconciliation | recorded |
| `stem_lists.csv` | AU, source, method, generator, hash, synthetic flag | planned |
| `fvsbc_runs.csv` | State, regime, run id, keyword hash, commit, status | planned |
| `state_library.csv` | State, regime, residual state, cycle, curve ids | planned |
| `ws4_builds.csv` | Dataset, source hashes, targets, command, status | planned |

Rules:

- Every evidence run names its source hashes and the pinned engine commit.
- A derived file records the transformation, not only the output.
- A private source is represented by a checksum and a schema, not by the
  payload.
- The metadata is updated in the same change set as the run it describes.
