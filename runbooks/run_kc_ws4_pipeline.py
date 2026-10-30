#!/usr/bin/env python3
"""Compile, validate, run, report and prepare the KC ws4 model.

This is the reproducible P3.7 lane:

1. compile the ForestModelXML recipe against the fragment inventory with
   ``ws4 build`` (the matrix builder path);
2. validate the compiled dataset;
3. write no-cut and selection-smoke schedules;
4. simulate and report both;
5. export the block GeoJSON;
6. write evidence and the serve command.

The script does not start a long-running web server; it prints the command.

Usage::

    python runbooks/run_kc_ws4_pipeline.py \
      --xml data/kc_ws4_recipe/forestmodel.xml \
      --fragments data/kc_ws4_recipe/fragments.csv \
      --spatial-fragments data/patchworks_knifecreek/fragments.csv \
      --fragment-shapefile data/patchworks_knifecreek/spatial/fragments.shp \
      --dataset ws4/dataset_kc_v1 \
      --runtime ws4/runtime/kc_v1 \
      --evidence ws4/evidence/kc_v1
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import geopandas as gpd
import pandas as pd


def _run(command: list[str]) -> None:
    """Run one CLI command and print it."""
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def _schedules(dataset: Path, runtime: Path) -> tuple[Path, Path]:
    """Write the no-cut and first-treatment selection schedules."""
    fragments = pd.read_parquet(dataset / "fragments.parquet")
    treatments = pd.read_parquet(dataset / "treatments.parquet")
    first_treatment = treatments.sort_values(["track_id", "begin"]).drop_duplicates("track_id")[
        ["track_id", "treatment"]
    ]
    schedule = fragments[["block_id", "track_id", "age"]].merge(
        first_treatment, on="track_id", how="left"
    )
    schedule = schedule.dropna(subset=["treatment"])
    schedule = schedule[["block_id", "treatment"]].assign(offset=0)
    baseline_path = runtime / "kc_baseline_no_cut.csv"
    selection_path = runtime / "kc_selection_smoke.csv"
    pd.DataFrame(columns=["block_id", "treatment", "offset"]).to_csv(baseline_path, index=False)
    schedule.to_csv(selection_path, index=False)
    return baseline_path, selection_path


def main() -> None:
    """Assemble and run the model lane."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xml", type=Path, required=True)
    parser.add_argument("--fragments", type=Path, required=True)
    parser.add_argument("--spatial-fragments", type=Path, required=True)
    parser.add_argument("--fragment-shapefile", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--years", type=int, default=10)
    args = parser.parse_args()
    args.runtime.mkdir(parents=True, exist_ok=True)
    args.evidence.mkdir(parents=True, exist_ok=True)
    if args.dataset.exists():
        shutil.rmtree(args.dataset)
    _run(
        [
            "ws4",
            "build",
            "--xml",
            str(args.xml),
            "--fragments",
            str(args.fragments),
            "--out",
            str(args.dataset),
        ]
    )
    _run(
        [
            "python",
            "runbooks/build_kc_account_groups.py",
            "--dataset",
            str(args.dataset),
            "--fragments",
            str(args.spatial_fragments),
        ]
    )
    _run(
        [
            "python",
            "runbooks/normalize_kc_strata.py",
            "--dataset",
            str(args.dataset),
            "--h-dir",
            "data/patchworks_knifecreek/tracks/H",
        ]
    )
    _run(["ws4", "validate", "--dataset", str(args.dataset)])
    audit_path = args.evidence / "account_audit.json"
    _run(
        [
            "python",
            "runbooks/audit_kc_accounts.py",
            "--dataset",
            str(args.dataset),
            "--targets",
            "ws4/targets_kc_smoke.yaml",
            "--targets",
            "ws4/targets_kc_gwm2007.yaml",
            "--out",
            str(audit_path),
        ]
    )

    coverage_path = args.evidence / "coverage_audit.json"
    _run(
        [
            "python",
            "runbooks/audit_kc_coverage.py",
            "--dataset",
            str(args.dataset),
            "--recipe-fragments",
            str(args.fragments),
            "--source-fragments",
            str(args.spatial_fragments),
            "--topology",
            "ws4/topology.csv",
            "--out",
            str(coverage_path),
        ]
    )

    integrity_path = args.evidence / "integrity_audit.json"
    _run(
        [
            "python",
            "runbooks/audit_kc_integrity.py",
            "--dataset",
            str(args.dataset),
            "--recipe",
            str(args.xml),
            "--h-dir",
            "data/patchworks_knifecreek/tracks/H",
            "--out",
            str(integrity_path),
        ]
    )

    baseline_path, selection_path = _schedules(args.dataset, args.runtime)

    for name, schedule_path in (
        ("baseline_no_cut", baseline_path),
        ("selection_smoke", selection_path),
    ):
        run_dir = args.runtime / name
        if run_dir.exists():
            shutil.rmtree(run_dir)
        _run(
            [
                "ws4",
                "simulate",
                "--dataset",
                str(args.dataset),
                "--schedule",
                str(schedule_path),
                "--years",
                str(args.years),
                "--out",
                str(run_dir),
                "--topology",
                "ws4/topology.csv",
                "--patch-accounts",
                "ws4/patch_accounts.yaml",
            ]
        )
        _run(
            [
                "ws4",
                "report",
                "--run",
                str(run_dir),
                "--targets",
                "ws4/targets_kc_smoke.yaml",
                "--out",
                str(run_dir / "report"),
            ]
        )

    fragments = gpd.read_file(args.fragment_shapefile).to_crs(3005)
    geometry = fragments[["BLOCK", "geometry"]].rename(columns={"BLOCK": "block_id"})
    if geometry.crs is None or geometry.crs.to_epsg() != 3005:
        raise ValueError("KC map geometry must be in EPSG:3005")
    geometry.to_file(args.runtime / "kc_blocks.geojson", driver="GeoJSON")
    evidence = {
        "phase": "P3.7",
        "recipe": str(args.xml),
        "fragments": str(args.fragments),
        "spatial_fragments": str(args.spatial_fragments),
        "account_audit": str(audit_path),
        "coverage_audit": str(coverage_path),
        "integrity_audit": str(integrity_path),
        "dataset": str(args.dataset),
        "years": args.years,
        "baseline_schedule": str(baseline_path),
        "selection_schedule": str(selection_path),
        "runs": ["baseline_no_cut", "selection_smoke"],
        "serve": (
            "ws4 serve --dataset "
            + str(args.dataset)
            + " --runs "
            + str(args.runtime)
            + " --targets ws4/targets_kc_smoke.yaml --geometry "
            + str(args.runtime / "kc_blocks.geojson")
            + " --crs EPSG:3005 --topology ws4/topology.csv "
            + "--patch-accounts ws4/patch_accounts.yaml --port 8766"
        ),
        "caveats": [
            "Structural model, not a calibrated KC growth model.",
            "The recipe is generated from the KC H-matrix source tables.",
            "Selection smoke applies the first available treatment to every block at offset 0.",
            "Product yield curves are point estimates; features are 100-year "
            "space-for-time curves.",
            "Patch account uses managed area, not a seral/opening criterion.",
            "Large-tree BA, reserve BA, seral/opening and species-split features "
            "are unavailable and not fabricated.",
            "Route configuration is unavailable; the public road layer is map context only.",
        ],
    }
    (args.evidence / "pipeline_manifest.json").write_text(json.dumps(evidence, indent=2) + "\n")
    for name in ("baseline_no_cut", "selection_smoke"):
        summary = args.runtime / name / "summary.json"
        if summary.exists():
            shutil.copy2(summary, args.evidence / f"{name}_summary.json")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
