#!/usr/bin/env python3
"""Compile, validate, run, report and prepare the KC ws4 model.

This is the reproducible P3.7 lane:

1. ingest the source matrix tables;
2. validate the compiled dataset;
3. write no-cut and selection-smoke schedules;
4. simulate and report both;
5. export the block GeoJSON;
6. write evidence and the serve command.

The script does not start a long-running web server; it prints the command.

Usage::

    python runbooks/run_kc_ws4_pipeline.py \
      --h-dir data/patchworks_knifecreek/tracks/H \
      --fragments data/patchworks_knifecreek/fragments.csv \
      --fragment-shapefile data/patchworks_knifecreek/spatial/fragments.shp \
      --dataset ws4/dataset_kc_h_v1 \
      --runtime ws4/runtime/kc_h \
      --evidence ws4/evidence/kc_h
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


def main() -> None:
    """Assemble and run the model lane."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h-dir", type=Path, required=True)
    parser.add_argument("--fragments", type=Path, required=True)
    parser.add_argument("--fragment-shapefile", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--years", type=int, default=10)
    args = parser.parse_args()
    args.runtime.mkdir(parents=True, exist_ok=True)
    args.evidence.mkdir(parents=True, exist_ok=True)
    for path in (args.dataset,):
        if path.exists():
            shutil.rmtree(path)
    _run(
        [
            "ws4",
            "ingest",
            "--matrix",
            str(args.h_dir),
            "--fragments",
            str(args.fragments),
            "--out",
            str(args.dataset),
        ]
    )
    _run(["ws4", "validate", "--dataset", str(args.dataset)])

    blocks = pd.read_csv(args.h_dir / "blocks.csv")
    treatments = pd.read_csv(args.h_dir / "treatments.csv")
    first_treatment = treatments.sort_values(["TRACK", "BEGIN"]).drop_duplicates("TRACK")[
        ["TRACK", "TREATMENT"]
    ]
    schedule = blocks.merge(first_treatment, on="TRACK", how="left")
    schedule = schedule.dropna(subset=["TREATMENT"])
    schedule = schedule[["BLOCK", "TREATMENT", "OFFSET"]].rename(
        columns={"BLOCK": "block_id", "TREATMENT": "treatment", "OFFSET": "offset"}
    )
    baseline_path = args.runtime / "kc_baseline_no_cut.csv"
    selection_path = args.runtime / "kc_selection_smoke.csv"
    pd.DataFrame(columns=["block_id", "treatment", "offset"]).to_csv(baseline_path, index=False)
    schedule.to_csv(selection_path, index=False)

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

    fragments = gpd.read_file(args.fragment_shapefile).to_crs(4326)
    geometry = fragments[["BLOCK", "geometry"]].rename(columns={"BLOCK": "block_id"})
    geometry.to_file(args.runtime / "kc_blocks.geojson", driver="GeoJSON")
    evidence = {
        "phase": "P3.7",
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
            + " --topology ws4/topology.csv --patch-accounts ws4/patch_accounts.yaml --port 8766"
        ),
        "caveats": [
            "Structural model, not a calibrated KC growth model.",
            "Selection smoke applies the first available treatment to every block at offset 0.",
            "Product yield curves are point estimates; features are 100-year "
            "space-for-time curves.",
            "Patch account uses managed area, not a seral/opening criterion.",
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
