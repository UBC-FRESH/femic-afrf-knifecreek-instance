Instance Contract
=================

Purpose
-------

This repository is a public ws4 model instance for the Knife Creek block of the
UBC Alex Fraser Research Forest. It has three jobs:

1. record the data and management constraints that make Knife Creek an
   uneven-aged problem;
2. build a reproducible FVS-BC state-transition library for the block; and
3. compile that library into a ws4 dataset that can be optimized and reported.

It is not the FEMIC core package, the ws4 runtime package, the fresh-fvsbc
package, or the future merged AFRF model.

Scope
-----

In scope:

- the Knife Creek boundary, VRI/inventory, BEC, site index, disturbance, and
  mule-deer winter-range constraints;
- reviewed stem lists and synthetic stem populations for each analysis unit;
- FVS-BC selection-cut runs and their per-tree, cut-list, structural, and
  summary outputs;
- a state-transition library and its ws4 translation;
- a baseline selection schedule and scenario comparison;
- GWM 2007 as the default MDWR basis, with Table 29 as a named AFRF
  alternative; and
- documentation of the data publication and merge boundaries.

Out of scope until a later phase:

- even-aged clearcut regimes, except as a documented sensitivity or a
  historical comparison;
- VDYP/TIPSY as the primary growth engine;
- private financial data;
- the Gavin Lake block; and
- the merged AFRF model.

Inputs
------

Table: Knife Creek inputs.

============================  =================================================
Input                         Use
============================  =================================================
Legal boundary                Block geometry, area, and spatial joins.
VRI / AFRF forest cover       Species, age, site index, density, and polygon
                              attributes.
BEC and site-series map       Analysis-unit stratification and FVS-BC site
                              input.
Disturbance history           The 2013 wildfire and harvest history that shape
                              current structure.
Mule-deer winter-range map    Legal UWR/HMZ spatial constraints and habitat
                              indicators. The 2007 order text and 2003
                              transition plan are acquired; the spatial layer
                              is still required.
CFI / tree-level tallies      Measured or reconstructed stem distributions.
nemora outputs                Synthetic stem populations where measured tree
                              lists are unavailable.
FVS-BC and fresh-fvsbc        Individual-tree growth and selection-cut engine.
============================  =================================================

Outputs
-------

- a stem-list manifest per analysis unit;
- an FVS-BC run manifest per state and regime;
- a state-transition library with pre-cut states, cut lists, residual states,
  growth curves, and habitat indicators;
- a ws4 dataset with tracks, treatments, curves, features, products, and
  accounts; and
- a baseline run and scenario evidence.

Reproducibility
---------------

Every derived surface must be reproducible from:

- the source data checksum;
- the stem-list generator and its parameters;
- the pinned `fresh-fvsbc` commit and FVS-BC build;
- the keyword set and its hash;
- the state-key and regime definitions; and
- the ws4 build command and target set.

No run is complete until that chain is recorded.

The policy basis is part of the chain. A GWM 2007 run and a Table 29 run are
different products; the state key or manifest must say which basis was used.
The legal order and HMZ text are not a compliance claim without the spatial
UWR layer.

Relationship to Gavin Lake
---------------------------

Gavin Lake and Knife Creek are separate ws4 instances. Gavin Lake uses a legacy
Patchworks age-class matrix; Knife Creek uses an FVS-BC state-transition
library. They share the ws4 compiled-dataset schema, which is the seam for the
future merged model.

The merge contract is in `notes/adr/0004-merged-afrf-model.md`.
