# Knife Creek screening delivered-wood layer

This is the best delivered-wood layer that can be built from the current data.
It is a screening model, not an operational or legal-access model.

## Route network

`route/` contains the four WS4 route tables and `route.yaml`.

- 211 split blocks.
- 75 public tenure-road segments from the BC road layer.
- The public layer is disconnected: 13 components, joined by 12 straight
  synthetic connectors.
- 4 candidate sawlog mills: Tolko Williams Lake, Tolko Williams Lake (second
  mill), West Fraser Williams Lake, and West Fraser 100 Mile House.
- Block access is a straight line to the nearest public-road vertex. Median
  distance is 350 m; maximum is 1,493 m.
- Mill haul is a straight-line distance times 1.25, not a routed highway path.

Cost rates are TSA23 C5 route-fixture medians used as a proxy:

- haul: 0.00016 CAD per m3 per metre;
- build: 0.00 CAD per metre;
- maintenance: 2.00 CAD per metre per year.

They are not AFRF contract rates.

## Route result

The run is `ws4/runtime/kc_delivered_wood_screening`, reproduced with:

```bash
python runbooks/build_kc_screening_route.py --out-dir data/delivered_wood/kc/route
ws4 simulate \
  --dataset ws4/dataset_kc_au_stages_split_volume_v1 \
  --schedule ws4/runtime/kc_aac_50k/schedule.csv \
  --years 200 \
  --route-config data/delivered_wood/kc/route/route.yaml \
  --out ws4/runtime/kc_delivered_wood_screening
```

Result:

- 97 blocks routed; 13 scheduled blocks produce no routed yield.
- 306,438 m3 routed.
- 1.79 M CAD haul.
- 1.25 M CAD maintenance.
- 0 build cost, because all public roads are treated as existing.
- All volume goes to `destination.MILL_103_LBR`; without mill demand or
  capacity constraints, the least-cost mill wins.

## Log sorts and value

`runbooks/build_kc_delivered_wood.py` splits each block's routed volume using:

- area-weighted species composition from the 2025 VRI;
- the BC interior market species groups;
- the June-August 2026 BC Interior Log Market Report sort mix; and
- the published species-group and sort average prices.

The result is 306,438 m3 and about 36.4 M CAD gross value. The largest sort is
Df-Larch sawlog at 204,378 m3 and 25.4 M CAD. Deciduous and residual species
use the `Other/Other` price as a proxy.

The sort mix is a regional market-purchase mix, not an AFRF grade distribution.
The prices are regional averages, not AFRF sales. This is a screening layer.

## Files

- `delivered_wood_values.csv` - block/year/mill/species/sort volume and value.
- `delivered_wood_by_year.csv` - year/mill/species/sort totals.
- `delivered_wood_by_mill.csv` - mill/species/sort totals.
- `delivered_wood_metadata.json` - totals, assumptions, caveats.
- `route_values.csv` - WS4 route output.
- `route_cost_report.csv` - WS4 route cost report.
- `used_roads.csv` - WS4 used-road geometry.
- `product_values.csv` - WS4 product values.

## Limits

- Public road layer is incomplete against MWP #3 Table 37.
- Synthetic connectors and mill haul are not routed roads.
- Mill acceptance, demand, and capacity are not modelled.
- Sort mix and prices are regional BC references, not AFRF records.
- No AAC, legal-access, or legal-compliance claim is made.
