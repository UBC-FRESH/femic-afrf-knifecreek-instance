# Data request: AFRF roads, mills, log sorts, and costs

Date: 2026-10-31
For: AFRF operations and data management
Related: P7, roads, log sorts, and mills

## Context

The Knife Creek and Gavin Lake estate models currently carry volume, carbon, and
stand structure, but not delivered wood. We are adding:

- a modelled road network with block access, build, maintenance, and haul
  accounts;
- a mill register with location, capacity, and accepted sorts;
- log-sort and log-grade products with a dated interior price basis; and
- harvest-system classes and operational constraints.

The 2007 Management and Working Plan #3 gives the road classes, road lengths,
harvest systems, slope limits, and skid limits. It does not give the road
geometry, road costs, mill register, accepted sorts, or grade prices.

The legacy Patchworks archive has `useRoutes = false` and an empty `AFRF/roads/`
directory. Its build script references `Roads_PW_v2.shp` and `Mills_PW.shp`, but
those files were not included. The OneDrive modelling payload contains the
Marshall plots, Kozak taper package, and LiDAR only.

## What we are requesting

Please provide, or point us to, the following records.

### Road network and access

1. `Roads_PW_v2.shp` and `Mills_PW.shp`, or their current equivalents.
2. The legacy route tables used with those layers:
   - `vertices.csv`
   - `segments.csv`
   - `destinations.csv`
   - `linkages.csv`
3. The haul-cost table behind the `HAUL` field in the mill layer.
4. Current road inventory:
   - centerlines;
   - road class and surface;
   - existing, planned, temporary, deactivated, or closed status;
   - right-of-way width;
   - bridges, gates, culverts, and other access controls; and
   - any seasonal or weight restrictions.
5. Road construction, maintenance, haul, landing, and deactivation costs, or
   recent contract records that can support a cost range.

### Mills and log sorts

6. Mill register:
   - mill name and operator;
   - location;
   - current status;
   - annual capacity and current demand;
   - accepted species;
   - accepted log sorts and grades; and
   - minimum volume or delivery requirements.
7. Any mill-specific sort specifications, delivery rules, or quota
   arrangements that affect where AFRF logs can go.

### Prices, grades, and scaling

8. AFRF log sales records or price lists by species and sort.
9. Scaling records and grade distributions.
10. Any documented crosswalk from AFRF species and grades to the BC interior
    grades (Z/6/1/2/4) or to the interior log-market species groups.

### Harvest systems and constraints

11. Block-level harvest-system records and prescriptions.
12. Slope, terrain, soil, riparian, and access constraints used in operational
    planning.
13. Any current approved plan or order that governs the blocks.

### Publication

14. For each layer, please confirm whether it is:
    - public;
    - public in derived form only; or
    - private-only.

## What we can use immediately

The following public references are already loaded and will be used with
explicit caveats:

- BC Major Timber Processing Facilities, for candidate mill location and
  capacity;
- BC Interior Log Market Report, June-August 2026, for species-group and sort
  average prices; and
- BC Timber Scaling Manual Chapter 9, for the five interior grade codes.

These do not replace AFRF records. They are screening and sensitivity inputs.

## What will not be claimed

- no legal access determination;
- no statutory AAC;
- no legal-compliance finding; and
- no mill capacity, accepted sort, or price that is not supported by a source.

## Preferred format

Shapefile, GeoPackage, CSV, or Excel are all usable. Please include the date,
the source system, and any known gaps or caveats. If a layer is sensitive, a
derived summary or a private copy is acceptable.
