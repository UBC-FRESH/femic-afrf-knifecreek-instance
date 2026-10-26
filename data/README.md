# Data directory

No source data is committed yet.

Planned layout:

| Path | Purpose | Git |
| --- | --- | --- |
| `boundaries/` | Knife Creek legal boundary | Public only, with permission |
| `inventory/` | VRI, BEC, site index, disturbance | Public only, with permission |
| `habitat/` | Mule-deer winter-range layers | Public only, with permission |
| `fvsbc/populations/` | Stem-population JSON per AU | Reviewed derived data |
| `downloads/` | Local downloads | Ignored |
| `raw/` | Local raw source copies | Ignored |
| `private/` | Restricted source data | Ignored, never committed |

Rules:

- A source is not committed until its publication status is recorded.
- A restricted source can be represented by a checksum, a schema, and a
  derived public summary.
- Generated stem populations and FVS-BC outputs are derived data; record the
  source and generator.
- Do not commit machine-specific paths or personal identifiers.
