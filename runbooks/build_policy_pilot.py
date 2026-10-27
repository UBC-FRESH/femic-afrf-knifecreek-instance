#!/usr/bin/env python3
"""Run a policy pilot for veteran/large-tree retention in FVS-BC.

The pilot compares a full-range BDq cut that leaves all trees above the habitat
maximum DBH with split cuts that first remove surplus trees above 50 cm to a
residual large-tree BA, then thin the 0-50 cm component to the remaining Table
29 basal area and q.

FVS-BC is distance-independent. The clump metrics are post-processing proxies,
not a spatial snow-interception model.

Usage::

    PYTHONPATH=/path/to/fresh-fvsbc/src \
      /path/to/fvsbc-build-venv/bin/python runbooks/build_policy_pilot.py \
      --sample data/psp/idf_cariboo_psp_conditional_stemlists.csv \
      --policies config/retention_policies.yaml \
      --out-dir ws4/policy_pilot_v0 \
      --runtime-dir runtime/policy_pilot_v0
"""

from __future__ import annotations

import argparse
import itertools
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import UnknownTableError, read_table
from fresh_fvsbc.run import run_population

STANDS = ("PSP-REG-004", "PSP-REG-005")
REGIMES = {
    "SEL_MDWR_HIGH": {"B": 29.0, "D": 60.0, "q": 1.25},
    "SEL_MDWR_MODERATE": {"B": 22.0, "D": 55.0, "q": 1.25},
    "SEL_MDWR_LOW": {"B": 16.0, "D": 50.0, "q": 1.30},
}
LARGE_THRESHOLD = 50.0
FT2_PER_M2 = 4.356


def _q_factor(rows: pd.DataFrame) -> float:
    """Return the median q-factor from 5 cm TPH classes."""
    if rows.empty:
        return float("nan")
    classes = (rows["DBH"] // 5 * 5 + 2.5).astype(float)
    density = rows.assign(dbh_class=classes).groupby("dbh_class")["TPH"].sum()
    all_classes = np.arange(classes.min(), classes.max() + 5.0, 5.0)
    density = density.reindex(all_classes, fill_value=0.0)
    ratios = []
    for lower, upper in itertools.pairwise(all_classes):
        if density.loc[lower] > 0 and density.loc[upper] > 0:
            ratios.append(float(density.loc[lower] / density.loc[upper]))
    return float(np.median(ratios)) if ratios else float("nan")


def _policy_keywords(
    policy: dict[str, object],
    regime: str,
    cycle: int,
) -> list[Keyword]:
    """Build the FVS-BC treatment keywords for one policy/regime pair."""
    spec = REGIMES[regime]
    method = str(policy["method"])
    if method == "full_range_bdq":
        return [
            Keyword(
                "THINQFA",
                (
                    str(cycle),
                    "0.0",
                    str(spec["D"]),
                    "0",
                    str(spec["q"]),
                    "5.0",
                    str(round(spec["B"] * FT2_PER_M2, 2)),
                ),
                supplemental=("0",),
            )
        ]
    large = float(policy["large_tree_residual_ba_m2_ha"])
    small_b = max(0.0, float(spec["B"]) - large)
    return [
        Keyword(
            "THINABA",
            (str(cycle), str(large), "1.0", "50", "999", "0", "999"),
        ),
        Keyword(
            "THINQFA",
            (
                str(cycle),
                "0.0",
                "50.0",
                "0",
                str(spec["q"]),
                "5.0",
                str(round(small_b * FT2_PER_M2, 2)),
            ),
            supplemental=("0",),
        ),
    ]


def _run_case(
    population: list[dict[str, object]],
    *,
    stand: str,
    age: float,
    regime: str,
    policy: dict[str, object],
    runtime_dir: Path,
) -> object:
    """Run one policy case."""
    keywords = [
        Keyword(
            "DATABASE",
            (),
            ("DSNOut", "FVSOut.db", "TreeLIDB", "CutLIDB", "ATRTLIDB", "Summary"),
        ),
        Keyword("STDIDENT", (f"{stand} {regime} {policy['id']}",)),
        Keyword("STDINFO", ("712", "CHS131", "0", "200", "35", "16")),
        Keyword("MANAGED", ("0", "1")),
        Keyword("SITECODE", ("FD", "60")),
        Keyword("INVYEAR", ("0",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", "10")),
        Keyword("NUMCYCLE", ("4",)),
        Keyword("RANNSEED", ("1",)),
        Keyword("TREELIST", ("4",)),
        Keyword("CUTLIST", ("4",)),
        Keyword("ATRTLIST", ("4",)),
        *_policy_keywords(policy, regime, 4),
        Keyword("PROCESS"),
        Keyword("STOP"),
    ]
    return run_population(
        population,
        directory=runtime_dir / f"{stand}__{regime}__{policy['id']}",
        species="FD",
        tree_age=age,
        keywords=keywords,
    )


def _extract(
    result: object,
    *,
    stand: str,
    regime: str,
    policy: dict[str, object],
    clump_size: int,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Extract one transition and its 0-30 year curve."""
    summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
    try:
        atrt = read_table(result.database, "FVS_ATRTList_Metric")
        after = atrt[atrt["Year"] == 30].copy()
    except UnknownTableError:
        after = pd.DataFrame()
    row = summary.loc[summary["Year"] == 30].iloc[0]
    if after.empty:
        large_ba = np.nan
        large_tph = np.nan
        mean_width = np.nan
        mean_crown = np.nan
        clump_count = np.nan
        clump_cover = np.nan
        post_max_dbh = np.nan
        post_q_factor = np.nan
    else:
        after["ba"] = 0.00007854 * after["DBH"] ** 2 * after["TPH"]
        large = after[after["DBH"] >= LARGE_THRESHOLD]
        large_ba = float(large["ba"].sum()) if len(large) else 0.0
        large_tph = float(large["TPH"].sum()) if len(large) else 0.0
        mean_width = float(large["CrWidth"].mean()) if len(large) else 0.0
        mean_crown = float(large["PctCr"].mean()) if len(large) else 0.0
        clump_count = large_tph / clump_size if clump_size > 0 else 0.0
        crown_area = large_tph * np.pi * (mean_width / 2.0) ** 2
        clump_cover = min(1.0, crown_area / 10000.0)
        post_max_dbh = float(after["DBH"].max())
        post_q_factor = _q_factor(after)
    post_ba = float(row.ATBA)
    post_qmd = float(row.ATQMD)
    post_tph = max(0.0, float(row.Tph) - float(row.RTph))
    transition = {
        "transition_id": f"{stand}__{regime}__{policy['id']}",
        "stand": stand,
        "regime": regime,
        "policy": str(policy["id"]),
        "policy_method": str(policy["method"]),
        "target_b_m2_ha": float(REGIMES[regime]["B"]),
        "target_d_cm": float(REGIMES[regime]["D"]),
        "target_q": float(REGIMES[regime]["q"]),
        "target_large_ba_m2_ha": (
            None
            if policy.get("large_tree_residual_ba_m2_ha") is None
            else float(policy["large_tree_residual_ba_m2_ha"])
        ),
        "clump_size": clump_size,
        "pre_ba_m2_ha": float(row.BA),
        "pre_qmd_cm": float(row.QMD),
        "pre_tph": float(row.Tph),
        "pre_volume_m3_ha": float(row.TCuM),
        "post_ba_m2_ha": post_ba,
        "post_qmd_cm": post_qmd,
        "post_tph": post_tph,
        "post_q_factor": post_q_factor,
        "post_max_dbh_cm": post_max_dbh,
        "post_canopy_ccf": float(row.ATCCF) if hasattr(row, "ATCCF") else float(row.CCF),
        "post_large_ba_m2_ha": large_ba,
        "post_large_tph": large_tph,
        "mean_large_crown_width_m": mean_width,
        "mean_large_crown_ratio": mean_crown,
        "clump_count_per_ha": clump_count,
        "clump_crown_cover_fraction": clump_cover,
        "cut_tph": float(row.RTph),
        "cut_m3_ha": float(row.RTCuM),
        "treatment_applied": bool(float(row.RTph) > 0.0),
    }
    curves = []
    for point in summary[summary["Year"] <= 30].itertuples(index=False):
        curves.append(
            {
                "transition_id": transition["transition_id"],
                "stand": stand,
                "regime": regime,
                "policy": str(policy["id"]),
                "year": int(point.Year),
                "ba_m2_ha": float(point.BA),
                "qmd_cm": float(point.QMD),
                "tph": float(point.Tph),
                "volume_m3_ha": float(point.TCuM),
                "canopy_ccf": float(point.CCF),
            }
        )
    return transition, curves


def main() -> None:
    """Run the policy pilot and write the tables."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--policies", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--stands", nargs="*", default=list(STANDS))
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.runtime_dir.mkdir(parents=True, exist_ok=True)
    sample = pd.read_csv(args.sample)
    policy_config = yaml.safe_load(args.policies.read_text())
    policies = policy_config["policies"]
    transitions = []
    curves = []
    runs = []
    for stand in args.stands:
        frame = sample[sample["stand_id"] == stand].copy()
        if frame.empty:
            raise ValueError(f"stand {stand!r} is not in {args.sample}")
        population = frame[["stand_id", "dbh_cm", "height_m", "crown_ratio"]].to_dict("records")
        age = float(
            frame["source_age"].iloc[0]
            if "source_age" in frame.columns
            else frame["tree_age"].iloc[0]
        )
        for regime in REGIMES:
            for policy in policies:
                result = _run_case(
                    population,
                    stand=stand,
                    age=age,
                    regime=regime,
                    policy=policy,
                    runtime_dir=args.runtime_dir,
                )
                transition, curve_rows = _extract(
                    result,
                    stand=stand,
                    regime=regime,
                    policy=policy,
                    clump_size=int(policy.get("clump_size", 3)),
                )
                transitions.append(transition)
                curves.extend(curve_rows)
                runs.append(
                    {
                        "stand": stand,
                        "regime": regime,
                        "policy": policy["id"],
                        "case_id": result.provenance.case_id,
                        "keyword_hash": result.provenance.keyword_set_hash,
                        "treelist_hash": result.provenance.treelist_hash,
                    }
                )
    transitions_df = pd.DataFrame(transitions)
    curves_df = pd.DataFrame(curves)
    transitions_df.to_csv(args.out_dir / "transitions.csv", index=False)
    curves_df.to_csv(args.out_dir / "curves.csv", index=False)
    benchmark = (
        transitions_df.groupby(["regime", "policy"])
        .agg(
            n=("transition_id", "size"),
            target_ba=("target_b_m2_ha", "first"),
            mean_post_ba=("post_ba_m2_ha", "mean"),
            mean_post_q=("post_q_factor", "mean"),
            mean_large_ba=("post_large_ba_m2_ha", "mean"),
            mean_large_tph=("post_large_tph", "mean"),
            mean_clump_count=("clump_count_per_ha", "mean"),
            mean_clump_cover=("clump_crown_cover_fraction", "mean"),
            mean_cut_m3_ha=("cut_m3_ha", "mean"),
            mean_cut_tph=("cut_tph", "mean"),
            n_cut=("treatment_applied", "sum"),
            n_large=("post_large_tph", "count"),
        )
        .reset_index()
    )
    benchmark.to_csv(args.out_dir / "benchmark.csv", index=False)
    manifest = {
        "pilot": "knife-creek-veteran-retention-v0",
        "status": "structural-policy-pilot",
        "generated_at": datetime.now(UTC).isoformat(),
        "source_stemlist": str(args.sample),
        "policies_file": str(args.policies),
        "stands": list(args.stands),
        "regimes": REGIMES,
        "counts": {
            "transitions": len(transitions_df),
            "curves": len(curves_df),
            "policies": len(policies),
        },
        "runs": runs,
        "caveats": [
            "FVS-BC is distance-independent; clump metrics are post-processing proxies.",
            "No physical snow-interception model is used.",
            "The pilot uses two PSP-derived regional IDF Cariboo stands, not KC data.",
            "The policy levels are scenario axes, not approved MDWR policy.",
            "The large-tree target is a residual BA above 50 cm, not a legal objective.",
            (
                "GWM 10 requires clumps of 4-10 or more mature trees with "
                "interlocking crowns; 2-5 is the maximum-diameter subgroup."
            ),
            (
                "The 50 cm threshold and Table 29 D values are an AFRF "
                "interpretation; the legal GWM uses BA >37.5 cm and D 70/60/50."
            ),
            (
                "A canceled treatment with no after-treatment tree list has missing "
                "large-tree metrics, not zero."
            ),
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"transitions={len(transitions_df)} curves={len(curves_df)} policies={len(policies)}")


if __name__ == "__main__":
    main()
