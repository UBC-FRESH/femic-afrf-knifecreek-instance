#!/usr/bin/env python3
"""Build spatial clump-geometry scenarios from the policy pilot.

The policy pilot gives a non-spatial large-tree TPH and mean crown width. This
script places those trees in clumps of 4-10 on a ring around a clump centre and
measures the fraction of the clump footprint covered by crowns. The 4-10 range
is the legal GWM 10 mature-tree clump; 2-5 is only the maximum-diameter subgroup. It is a
geometry scenario, not an empirical clump distribution and not a snow model.

Usage::

    python runbooks/build_clump_scenarios.py \
      --transitions ws4/policy_pilot_v0/transitions.csv \
      --out-dir ws4/policy_pilot_v0
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

CLUMP_SIZES = (4, 6, 8, 10)
CLUMP_RADII_M = (3.0, 5.0, 7.0)
CLOSED_THRESHOLD = 0.70
GRID_M = 0.25


def _clump_closure(
    n_trees: int,
    crown_radius_m: float,
    clump_radius_m: float,
) -> tuple[float, float]:
    """Return crown closure inside the clump footprint and footprint area."""
    outer = max(clump_radius_m + crown_radius_m, GRID_M)
    axis = np.arange(-outer, outer + GRID_M, GRID_M)
    xx, yy = np.meshgrid(axis, axis)
    covered = np.zeros_like(xx, dtype=bool)
    if n_trees == 1:
        centres = [(0.0, 0.0)]
    else:
        angles = np.linspace(0.0, 2.0 * np.pi, n_trees, endpoint=False)
        centres = [(clump_radius_m * np.cos(a), clump_radius_m * np.sin(a)) for a in angles]
    for cx, cy in centres:
        covered |= (xx - cx) ** 2 + (yy - cy) ** 2 <= crown_radius_m**2
    footprint = np.pi * outer**2
    closure = float(covered.sum() * GRID_M**2 / footprint)
    return min(1.0, closure), footprint


def main() -> None:
    """Write the clump scenario table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transitions", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    transitions = pd.read_csv(args.transitions)
    rows = []
    for row in transitions.itertuples(index=False):
        if not np.isfinite(row.post_large_tph) or row.post_large_tph <= 0:
            continue
        if not np.isfinite(row.mean_large_crown_width_m) or row.mean_large_crown_width_m <= 0:
            continue
        crown_radius = float(row.mean_large_crown_width_m) / 2.0
        for clump_size in CLUMP_SIZES:
            n_clumps = float(row.post_large_tph) / clump_size
            spacing = float(np.sqrt(10000.0 / n_clumps)) if n_clumps > 0 else np.nan
            for clump_radius in CLUMP_RADII_M:
                closure, footprint = _clump_closure(clump_size, crown_radius, clump_radius)
                raw_cover = n_clumps * footprint / 10000.0
                rows.append(
                    {
                        "transition_id": row.transition_id,
                        "stand": row.stand,
                        "regime": row.regime,
                        "policy": row.policy,
                        "clump_size": clump_size,
                        "legal_clump_size": 4 <= clump_size <= 10,
                        "clump_radius_m": clump_radius,
                        "crown_radius_m": crown_radius,
                        "clump_footprint_m2": footprint,
                        "n_clumps_per_ha": n_clumps,
                        "mean_spacing_m": spacing,
                        "clump_closure": closure,
                        "closed_canopy_clump": closure >= CLOSED_THRESHOLD,
                        "total_cover_sum": min(1.0, raw_cover),
                        "total_cover_poisson": 1.0 - np.exp(-raw_cover),
                    }
                )
    scenarios = pd.DataFrame(rows)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    scenarios.to_csv(args.out_dir / "clump_scenarios.csv", index=False)
    summary = (
        scenarios.groupby(["regime", "policy", "clump_size", "clump_radius_m"])
        .agg(
            n=("transition_id", "size"),
            mean_clumps_per_ha=("n_clumps_per_ha", "mean"),
            mean_spacing_m=("mean_spacing_m", "mean"),
            mean_clump_closure=("clump_closure", "mean"),
            closed_fraction=("closed_canopy_clump", "mean"),
            legal_clump_fraction=("legal_clump_size", "mean"),
            mean_total_cover=("total_cover_poisson", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(args.out_dir / "clump_scenario_summary.csv", index=False)
    print(f"clump scenarios={len(scenarios)} summary rows={len(summary)}")


if __name__ == "__main__":
    main()
