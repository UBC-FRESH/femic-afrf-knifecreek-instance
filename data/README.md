# Data directory

Public source and derived data are committed with provenance. Restricted or
Access Only sources are represented by a checksum, schema, or derived summary.

| Path | Purpose | Git |
| --- | --- | --- |
| `boundaries/` | Knife Creek legal boundary | Public, with permission |
| `inventory/` | VRI, BEC, site index, disturbance | Public, with permission |
| `habitat/` | Mule-deer winter-range layers | Public, with permission |
| `benchmarks/` | Reviewed public figure/table benchmarks | Derived, reviewed |
| `site_index/` | Klinka 2004 site-index tables | Derived, transcribed |
| `psp/` | Public FAIB PSP-derived IDF Cariboo stem-list analog | Derived, public |
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
