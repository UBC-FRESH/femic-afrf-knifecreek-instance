AFRF Knife Creek Instance
=========================

A **ws4 forest-estate model instance** for the Knife Creek block of the UBC
Alex Fraser Research Forest (AFRF).

Knife Creek is an uneven-aged, continuous-cover problem. The block is
predominantly Interior Douglas-fir, the species is relatively shade tolerant
there, and almost the whole block is constrained by mule-deer winter-range
objectives. Even-aged clearcutting is largely unavailable. The growth engine is
FVS-BC through the `UBC-FRESH/fresh-fvsbc` wrapper, and the bridge to ws4 is a
state-transition library built from FVS-BC per-tree and cut-list outputs.

The default mule-deer policy basis is the **2007 GWM order**. The legal clump
is 4–10 or more mature trees with interlocking crowns; the legal large-tree
threshold is 37.5 cm. The AFRF Table 29 values are a named alternative, not the
legal curve. See :doc:`reference/mdwr-legal-basis` and
:doc:`guides/mdwr-habitat-constraints`.

.. toctree::
   :maxdepth: 2
   :caption: Guides

   guides/index

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference/index

.. toctree::
   :maxdepth: 2
   :caption: API

   api/index
