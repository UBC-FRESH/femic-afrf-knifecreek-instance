# Knife Creek mule-deer HMZ layer

## Source

BC Map Hub / DataBC, *Mule Deer Winter Range Habitat Management Zones —
Cariboo Region*, ArcGIS item `96151b4539c4437897e3ec3324037db2`, layer 8 of
`bcgw_pub_reg_land_and_natural_resource`. Licence: Open Government Licence -
British Columbia.

Query: ArcGIS MapServer `.../MapServer/8/query`, clipped to SUP S15382 in
EPSG:3005. Reproducer: `runbooks/fetch_mdwr_hmz.py`.

Derived files:

- `data/habitat/mule_deer_hmz_kc.gpkg`
- `data/habitat/mule_deer_hmz_kc.csv`
- `data/habitat/mule_deer_hmz_kc.metadata.json`
- `data/habitat/kc_vri_hmz_overlay.csv` (VRI polygon × HMZ area crosswalk)
- `data/habitat/kc_vri_hmz_summary.csv`

## Area

| HMZ | Code | Area (ha) |
| ---: | --- | ---: |
| 1 | M | 738.29 |
| 2 | L | 1,217.15 |
| 3 | M | 320.51 |
| 4 | M | 1,213.33 |
| 5 | A | 0.00045 |
| **Total** | | **3,489.27** |

The SUP is 3,533.13 ha; 43.86 ha is outside the HMZ polygons (edge/unclassified).
Do not force the HMZ area to equal the SUP.

## Legal matrix

Knife Creek is U-5-002 `dwl_50`:

- HMZ 1: M — Low or Moderate only;
- HMZ 2: L — Low only;
- HMZ 3: M — Low or Moderate only;
- HMZ 4: M — Low or Moderate only;
- HMZ 5: A — all classes.

The HMZ layer is a spatial constraint. A stand-level BDq run is not compliance.
The layer must be joined to the block/AU geometry and the legal stand-structure
class map before a harvest opportunity is accepted.

## Caveats

- The public layer is the legal-order HMZ layer as published; verify the current
  approved order before a compliance claim.
- HMZ 5 is effectively absent inside the SUP (0.00045 ha).
- The public stand-structure habitat-class layer is in
  `data/habitat/mule_deer_stand_structure_kc.gpkg`; it is not by itself a
  compliance determination.
- The VRI crosswalk uses the largest HMZ area share as `dominant_hmz`; that is a
  summary, not a legal interpretation.
- The synthetic 4-block ws4 dataset does not carry spatial blocks. The spatial
  VRI/HMZ structural dataset `ws4/dataset_kc_spatial_v1/` applies the HMZ
  matrix through track copies (M/L/A/U).
