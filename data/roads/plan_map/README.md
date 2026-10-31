# Appendix 11 access-map recovery

This directory records an attempt to recover road geometry and mill context from
the 2007 AFRF Management and Working Plan #3 Appendix 11 maps and text.

## What was done

`runbooks/recover_mwp3_access_maps.py` uses `figrecover 0.1.0a1` to:

- render PDF pages 165 and 166 at 300 dpi;
- crop the Gavin Lake and Knife Creek access plans;
- write a figure manifest; and
- test whether the scanned magenta boundary can be registered to a known GIS
  boundary.

The Knife Creek map registers well to the legal SUP boundary:

- mean boundary distance: 4.48 px;
- scale: about 10.68 m/px; and
- rotation: about 0.00015 rad.

The overlay is `knife_creek_access_overlay.png`: green is the SUP boundary, blue
is the public BC road layer.

The Gavin Lake map does **not** register cleanly to the managed-fragment union:

- mean boundary distance: 49.17 px; and
- status: unresolved.

The mapped magenta boundary includes working-circle and non-forest edges that do
not match the legacy fragment union. A legal Gavin boundary or the original
`Roads_PW_v2.shp` is required.

## Road table reconciliation

`mwp3_appendix11_road_table.csv` transcribes the road tables printed on the two
maps. `mwp3_access_reconciliation.csv` compares them with Table 37.

The plan is internally inconsistent:

| Block | Measure | Appendix 11 | Table 37 | Difference |
| --- | --- | ---: | ---: | ---: |
| Knife Creek | Existing road length | 69.3 km | 86.2 km | -16.9 km |
| Knife Creek | Planned road length | 0.0 km | 77.2 km | -77.2 km |
| Gavin Lake | Existing road length | 91.9 km | 112.2 km | -20.3 km |
| Gavin Lake | Planned road length | 121.4 km | 136.1 km | -14.7 km |
| Knife Creek | Net area | 3,485.6 ha | 3,117 ha | +368.6 ha |
| Gavin Lake | Net area | 6,354.8 ha | 4,922 ha | +1,432.8 ha |

These are not rounding differences. The map tables use working-circle areas;
Table 37 uses different net areas. Do not silently reconcile them.

## Why this is not a road GIS layer

The map lines mix roads, contours, streams, labels, and symbols. A test
skeleton of the dark map lines produced about 70 km on Knife Creek, close to the
69.3 km map total, but only about 5% of that skeleton fell within 10 m of the
public road layer. The length match was therefore coincidental: most of the
skeleton was contour or stream linework, not road centreline.

The maps are useful for:

- visual context;
- road-class and feature inventory;
- a rough check on public-road alignment; and
- the plan's own road-length table.

They are not sufficient for:

- a block-to-road linkage;
- a route network;
- legal access status; or
- road costs.

## Mills

The plan text names only historical mills:

- G.W.J. Moore Sawmill, 150 Mile House, date unknown;
- Knife Creek bush mills, 1940s to early 1960s;
- All-Fir Lumber sawmill, eastern end of Gavin Lake, mid-1950s to early 1960s;
- Merrill-Gardner/Merrill-Wagner sawmill, Gavin Lake, mid-1960s; and
- generic "large mills in Williams Lake" after the mid-1960s.

It does not name current mills, capacities, accepted sorts, or grade prices. The
historical references are in `data/mills/mwp3_historical_mill_references.csv`.
