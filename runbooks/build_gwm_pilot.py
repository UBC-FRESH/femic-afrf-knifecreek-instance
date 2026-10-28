#!/usr/bin/env python3
"""Run a GWM 2007 legal-basis structural pilot on PSP-derived stands.

The default GWM cut harvests surplus large trees above the legal minimum while
protecting the legal maximum-DBH floor: THINABA removes surplus in the
37.5-D cm range to the minimum large-tree BA, leaving trees above D as the
reserve, then THINQFA thins 0-37.5 cm to B minus the retained large-tree BA. A
retain-all-above-D method is included as a sensitivity.

This is a stand-structure feasibility test, not a legal-compliance test. The
UWR/HMZ spatial layer is not checked.

Usage::

    PYTHONPATH=/path/to/fresh-fvsbc/src \
      /path/to/fvsbc-build-venv/bin/python runbooks/build_gwm_pilot.py \
      --sample data/psp/idf_cariboo_psp_conditional_stemlists.csv \
      --out-dir ws4/gwm_pilot_v0 \
      --runtime-dir runtime/gwm_pilot_v0
"""

from __future__ import annotations

import argparse
import itertools
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import UnknownTableError, read_table
from fresh_fvsbc.run import run_population

STANDS = (
    "PSP-REG-001",
    "PSP-REG-002",
    "PSP-REG-003",
    "PSP-REG-004",
    "PSP-REG-005",
)
REGIMES = {
    "GWM_HIGH": {
        "B": 29.0,
        "large_ba": 16.0,
        "D": 70.0,
        "q": 1.25,
        "q_min": 1.20,
        "q_max": 1.35,
        "reserve": 2.9,
    },
    "GWM_MODERATE": {
        "B": 22.0,
        "large_ba": 11.0,
        "D": 60.0,
        "q": 1.25,
        "q_min": 1.25,
        "q_max": 1.35,
        "reserve": 2.2,
    },
    "GWM_LOW": {
        "B": 16.0,
        "large_ba": 6.0,
        "D": 50.0,
        "q": 1.30,
        "q_min": 1.25,
        "q_max": 1.40,
        "reserve": 1.6,
    },
}
LARGE_THRESHOLD = 37.5
FT2_PER_M2 = 4.356
CLUMP_SIZE = 6


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


def _keywords(regime: str, method: str, cycle: int) -> list[Keyword]:
    """Build the GWM split or retain-above-D keyword sequence."""
    spec = REGIMES[regime]
    if method == "retain_above_d":
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
    small_b = max(0.0, spec["B"] - spec["large_ba"])
    return [
        Keyword(
            "THINABA",
            (
                str(cycle),
                str(spec["large_ba"]),
                "1.0",
                str(LARGE_THRESHOLD),
                str(spec["D"]),
                "0",
                "999",
            ),
        ),
        Keyword(
            "THINQFA",
            (
                str(cycle),
                "0.0",
                str(LARGE_THRESHOLD),
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
    method: str,
    runtime_dir: Path,
) -> object:
    """Run one GWM case."""
    keywords = [
        Keyword(
            "DATABASE",
            (),
            ("DSNOut", "FVSOut.db", "TreeLIDB", "CutLIDB", "ATRTLIDB", "Summary"),
        ),
        Keyword("STDIDENT", (f"{stand} {regime} {method}",)),
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
        *_keywords(regime, method, 4),
        Keyword("PROCESS"),
        Keyword("STOP"),
    ]
    return run_population(
        population,
        directory=runtime_dir / f"{stand}__{regime}__{method}",
        species="FD",
        tree_age=age,
        keywords=keywords,
    )


def _extract(
    result: object,
    *,
    stand: str,
    regime: str,
    method: str,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Extract one transition and its 0-30 year curve."""
    spec = REGIMES[regime]
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
        max_dbh = np.nan
        q_factor = np.nan
        reserve_ba = np.nan
    else:
        after["ba"] = 0.00007854 * after["DBH"] ** 2 * after["TPH"]
        large = after[after["DBH"] >= LARGE_THRESHOLD]
        large_ba = float(large["ba"].sum()) if len(large) else 0.0
        large_tph = float(large["TPH"].sum()) if len(large) else 0.0
        mean_width = float(large["CrWidth"].mean()) if len(large) else 0.0
        mean_crown = float(large["PctCr"].mean()) if len(large) else 0.0
        clump_count = large_tph / CLUMP_SIZE if CLUMP_SIZE > 0 else 0.0
        crown_area = large_tph * np.pi * (mean_width / 2.0) ** 2
        clump_cover = min(1.0, crown_area / 10000.0)
        max_dbh = float(after["DBH"].max())
        q_factor = _q_factor(after)
        reserve_ba = float(after[after["DBH"] > spec["D"]]["ba"].sum())
    post_ba = float(row.ATBA)
    checks = {
        "total_ba_ok": bool(np.isfinite(post_ba) and post_ba >= spec["B"]),
        "large_ba_ok": bool(np.isfinite(large_ba) and large_ba >= spec["large_ba"]),
        "max_dbh_ok": bool(np.isfinite(max_dbh) and max_dbh >= spec["D"]),
        "q_ok": bool(np.isfinite(q_factor) and spec["q_min"] <= q_factor <= spec["q_max"]),
    }
    failures = [name for name, ok in checks.items() if not ok]
    transition = {
        "transition_id": f"{stand}__{regime}__{method}",
        "stand": stand,
        "basis": "GWM_2007",
        "regime": regime,
        "method": method,
        "target_b_m2_ha": spec["B"],
        "target_large_ba_m2_ha": spec["large_ba"],
        "target_d_cm": spec["D"],
        "target_q": spec["q"],
        "target_reserve_max_m2_ha": spec["reserve"],
        "clump_size_proxy": CLUMP_SIZE,
        "pre_ba_m2_ha": float(row.BA),
        "pre_qmd_cm": float(row.QMD),
        "pre_tph": float(row.Tph),
        "pre_volume_m3_ha": float(row.TCuM),
        "post_ba_m2_ha": post_ba,
        "post_qmd_cm": float(row.ATQMD),
        "post_tph": max(0.0, float(row.Tph) - float(row.RTph)),
        "post_q_factor": q_factor,
        "post_max_dbh_cm": max_dbh,
        "post_canopy_ccf": float(row.ATCCF) if hasattr(row, "ATCCF") else float(row.CCF),
        "post_large_ba_m2_ha": large_ba,
        "post_large_tph": large_tph,
        "post_reserve_above_d_m2_ha": reserve_ba,
        "mean_large_crown_width_m": mean_width,
        "mean_large_crown_ratio": mean_crown,
        "clump_count_per_ha": clump_count,
        "clump_crown_cover_fraction": clump_cover,
        "cut_tph": float(row.RTph),
        "cut_m3_ha": float(row.RTCuM),
        "treatment_applied": bool(float(row.RTph) > 0.0),
        "stand_structure_pass": all(checks.values()),
        "failure_reasons": ";".join(failures),
        "legal_compliance": False,
        "hmz_check": "not_tested",
    }
    curves = []
    for point in summary[summary["Year"] <= 30].itertuples(index=False):
        curves.append(
            {
                "transition_id": transition["transition_id"],
                "stand": stand,
                "regime": regime,
                "method": method,
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
    """Run the GWM pilot and write the tables."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--stands", nargs="*", default=list(STANDS))
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.runtime_dir.mkdir(parents=True, exist_ok=True)
    sample = pd.read_csv(args.sample)
    transitions = []
    curves = []
    runs = []
    for stand in args.stands:
        frame = sample[sample["stand_id"] == stand].copy()
        if frame.empty:
            raise ValueError(f"stand {stand!r} is not in {args.sample}")
        population = frame[["stand_id", "dbh_cm", "height_m", "crown_ratio"]].to_dict("records")
        age = float(frame["tree_age"].iloc[0])
        for regime in REGIMES:
            for method in ("split_large_small", "retain_above_d"):
                result = _run_case(
                    population,
                    stand=stand,
                    age=age,
                    regime=regime,
                    method=method,
                    runtime_dir=args.runtime_dir,
                )
                transition, curve_rows = _extract(result, stand=stand, regime=regime, method=method)
                transitions.append(transition)
                curves.extend(curve_rows)
                runs.append(
                    {
                        "stand": stand,
                        "regime": regime,
                        "method": method,
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
        transitions_df.groupby(["regime", "method"])
        .agg(
            n=("transition_id", "size"),
            mean_post_ba=("post_ba_m2_ha", "mean"),
            mean_large_ba=("post_large_ba_m2_ha", "mean"),
            mean_large_tph=("post_large_tph", "mean"),
            mean_post_q=("post_q_factor", "mean"),
            mean_max_dbh=("post_max_dbh_cm", "mean"),
            mean_reserve=("post_reserve_above_d_m2_ha", "mean"),
            mean_cut_m3_ha=("cut_m3_ha", "mean"),
            pass_n=("stand_structure_pass", "sum"),
        )
        .reset_index()
    )
    benchmark.to_csv(args.out_dir / "benchmark.csv", index=False)
    manifest = {
        "pilot": "knife-creek-gwm2007-v0",
        "status": "stand-structure-feasibility-test",
        "generated_at": datetime.now(UTC).isoformat(),
        "basis": "GWM_2007",
        "source_stemlist": str(args.sample),
        "stands": list(args.stands),
        "regimes": REGIMES,
        "methods": ["split_large_small", "retain_above_d"],
        "counts": {
            "transitions": len(transitions_df),
            "curves": len(curves_df),
        },
        "runs": runs,
        "caveats": [
            "PSP-derived regional IDF Cariboo analog, not Knife Creek data.",
            "Stand-structure feasibility test only; legal_compliance is false.",
            "The UWR/HMZ spatial layer is not tested.",
            "The clump metrics are post-processing proxies, not spatial clumps.",
            "No KC FVS-BC calibration exists.",
            "High BA >37.5 >=16 may be unreachable from low-large-tree stands; report the gap.",
        ],
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"transitions={len(transitions_df)} curves={len(curves_df)} "
        f"pass={int(transitions_df['stand_structure_pass'].sum())}/{len(transitions_df)}"
    )


if __name__ == "__main__":
    main()
