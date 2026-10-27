# ws4 state-transition contract

Status: v0 transition library exists; no compiled ws4 dataset yet.

## Required tables

The dataset follows the ws4 compiled-dataset schema. The required tables and
columns are:

| Table | Columns |
| --- | --- |
| `fragments` | `fragment_id`, `block_id`, `area_ha`, `age`, `track_id` |
| `blocks` | `block_id`, `track_id`, `offset`, `area_ha` |
| `tracks` | `track_id`, `name` |
| `strata` | `track_id`, `offset`, `next_age`, `cycle` |
| `treatments` | `track_id`, `begin`, `end`, `treatment`, `new_track`, `offset`, `retain` |
| `curves` | `curve_id`, `x`, `y` |
| `features` | `track_id`, `label`, `curve_id` |
| `products` | `track_id`, `treatment`, `label`, `curve_id` |
| `accounts` | `group`, `attribute`, `account`, `sum` |
| `protoaccounts` | `group`, `attribute`, `account`, `sum` |
| `groups` | `block_id`, `group` |
| `messages` | `severity`, `message` |

## State and treatment semantics

- `tracks.name` carries the state key, such as
  `AU01__FD__BA20_30__QMD35_50__natural`.
- `treatments.begin` is the minimum cutting cycle in years.
- `treatments.end` is the horizon.
- `treatments.new_track` is the residual state.
- `treatments.offset` is 0; the residual state starts a new entry clock.
- `treatments.retain` is 0; the residual structure is in the new track.
- No treatment named `CC` or any other clearcut is present.

## Curves

A curve is keyed by `curve_id` and sampled on `x = years since entry`. The
library must provide at least:

- merchantable volume (m³/ha);
- basal area (m²/ha);
- quadratic mean diameter (cm);
- large-tree basal area (m²/ha);
- canopy cover (%); and
- any habitat indicator the constraints read.

Feature labels use the shared account vocabulary where possible, such as
`feature.yield.managed.total`. Block-specific or habitat-specific labels are
prefixed `feature.habitat.` and documented.

## Products

A product row is the cut yield at a selection entry. It uses the same product
labels as the account vocabulary, such as `product.yield.managed.total`, and
may split by species or grade where the FVS-BC cut list supports it.

## Topology

- The block topology is built from the legal boundary.
- No cross-block edges in the merged model.
- A selection opening is a patch account on the disturbed area; the exact
  account is deferred until the mule-deer constraint review.

## Provenance

The ws4 schema has no free-text provenance column. Provenance travels in:

- `tracks.name` (state key);
- a library manifest with state, regime, FVS-BC run, stem-list hash, and
  keyword hash;
- the dataset manifest source hashes; and
- the evidence summary.

## Validation

The dataset is valid when `ws4 validate` passes and:

- every `fragments.track_id` exists in `tracks`;
- every `treatments.new_track` exists in `tracks`;
- every curve domain is strictly increasing;
- no fragment has a negative age;
- the cutting cycle is positive;
- no clearcut treatment exists; and
- the habitat accounts are present and non-empty.
