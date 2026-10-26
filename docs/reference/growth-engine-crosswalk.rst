Growth-Engine Crosswalk
=======================

This page maps the FVS-BC state-transition library to the ws4 dataset. It is a
design contract; there is no run yet.

FVS-BC outputs
--------------

===============================  ===============================================
Table                            Use
===============================  ===============================================
`FVS_Cases`                      Run identity, variant, version, keyword file.
`FVS_TreeList_Metric`            Pre-cut and post-cut tree lists by period.
`FVS_CutList_Metric`             Removed trees by period and treatment.
`FVS_ATRTList_Metric`            After-treatment tree list.
`FVS_Summary_Metric`             Stand volume, basal area, density by period.
`FVS_StrClass_Metric`            Structural stage and canopy attributes.
`FVS_Stats_Species_Metric`       Species composition.
`FVS_Carbon_Metric`              Carbon pools, if needed.
===============================  ===============================================

State library
-------------

===============================  ===============================================
Library field                    Meaning
===============================  ===============================================
`state_id`                       Stable state key.
`au_id`                          Analysis unit.
`regime_id`                      Selection regime that produced the transition.
`pre_cut_run_id`                 FVS-BC run for the pre-cut stand.
`cut_run_id`                     FVS-BC run that applies the selection cut.
`residual_state_id`              Post-cut state key.
`cycle_years`                    Years between entries.
`volume_m3_ha`                   Merchantable volume by year.
`basal_area_m2_ha`               Basal area by year.
`qmd_cm`                         Quadratic mean diameter by year.
`large_tree_ba_m2_ha`            Large-tree basal area for habitat indicators.
`canopy_cover_pct`               Canopy cover for habitat indicators.
`cut_volume_m3`                  Removed volume at the entry.
`cut_species_share`              Removed volume by species.
===============================  ===============================================

ws4 tables
----------

===============================  ===============================================
Library field                    ws4 table and column
===============================  ===============================================
`state_id`                       `tracks.track_id` and `tracks.name`.
`cycle_years`                    `strata.offset` / `strata.next_age` and
                                 `treatments.begin`.
`regime_id`                      `treatments.treatment`.
`residual_state_id`              `treatments.new_track`.
`volume_m3_ha`                   `curves` with x = years since entry.
`basal_area_m2_ha`               `curves` or `features`.
`qmd_cm`                         `curves` or `features`.
`large_tree_ba_m2_ha`            `features` and account definitions.
`canopy_cover_pct`               `features` and account definitions.
`cut_volume_m3`                  `products` at the treatment.
`cut_species_share`              `products` by species label.
===============================  ===============================================

Translation rules
-----------------

1. A state is a track. A treatment moves a block from one state to another.
2. The entry clock is the years since the last selection entry. A treatment's
   `begin` is the minimum cutting cycle.
3. A residual state is a new track, not an area split.
4. The growth curve is a function of years since entry, not stand age.
5. Habitat indicators are features on the state track, so the optimizer and
   reports can read them.
6. Every track and treatment names its FVS-BC run and regime in the library
   manifest, even though ws4 does not store the name in the Parquet schema.

Open issues
-----------

- The ws4 schema has no free-text provenance column. The library manifest is
  the provenance surface, and the `tracks.name` string carries the state key.
- The state count and the canonicalization tolerance are not set.
- The FVS-BC keyword sequence for each regime is not reviewed.
- The mule-deer constraints are not yet mapped to ws4 accounts.
