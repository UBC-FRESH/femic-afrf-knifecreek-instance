# Metadata

Provenance ledgers for the Knife Creek instance.

Planned files:

| File | Purpose |
| --- | --- |
| `data_sources.csv` | Source, owner, licence, status, checksum |
| `stem_lists.csv` | AU, source, method, generator, hash, synthetic flag |
| `fvsbc_runs.csv` | State, regime, run id, keyword hash, commit, status |
| `state_library.csv` | State, regime, residual state, cycle, curve ids |
| `ws4_builds.csv` | Dataset, source hashes, targets, command, status |

Rules:

- Every evidence run names its source hashes and the pinned engine commit.
- A derived file records the transformation, not only the output.
- A private source is represented by a checksum and a schema, not by the
  payload.
- The metadata is updated in the same change set as the run it describes.
