#!/usr/bin/env python3
"""Run the KC baseline and two selection regimes.

Regimes are structural smoke comparisons, not reviewed management
prescriptions.  Each schedule chooses the preferred GWM treatment where the
block's track offers it, with a fallback to the other reviewed treatment.

Usage::

    python runbooks/run_kc_scenarios.py \
      --dataset ws4/dataset_kc_v1 \
      --runtime ws4/runtime/kc_v1 \
      --targets ws4/targets_kc_smoke.yaml \
      --years 30
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import pandas as pd

REGIMES = {
    "selection_gwm_low": ("GWM_LOW", "GWM_MODERATE"),
    "selection_gwm_moderate": ("GWM_MODERATE", "GWM_LOW"),
}
LEGAL_BY_HMZ = {"M": "GWM_MODERATE", "A": "GWM_MODERATE", "L": "GWM_LOW"}


def _run(command: list[str]) -> None:
    """Run one CLI command and print it."""
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def _schedule(dataset: Path, preferred: str, fallback: str) -> pd.DataFrame:
    """Build one treatment schedule from the compiled matrix."""
    fragments = pd.read_parquet(dataset / "fragments.parquet")
    treatments = pd.read_parquet(dataset / "treatments.parquet")
    available = treatments[["track_id", "treatment"]].drop_duplicates()
    rows: list[dict[str, object]] = []
    for block_id, track_id in (
        fragments[["block_id", "track_id"]].drop_duplicates().itertuples(index=False)
    ):
        labels = set(available.loc[available["track_id"] == track_id, "treatment"].astype(str))
        chosen = preferred if preferred in labels else fallback if fallback in labels else None
        if chosen is not None:
            rows.append({"block_id": int(block_id), "treatment": chosen, "offset": 0})
    return pd.DataFrame(rows, columns=["block_id", "treatment", "offset"])


def _legal_schedule(dataset: Path) -> pd.DataFrame:
    """Build the HMZ-mixed GWM schedule: M/A moderate, L low, U none."""
    fragments = pd.read_parquet(dataset / "fragments.parquet")
    treatments = pd.read_parquet(dataset / "treatments.parquet")
    available = treatments[["track_id", "treatment"]].drop_duplicates()
    tracks = pd.read_parquet(dataset / "tracks.parquet")
    hmz_by_track = {
        int(row.track_id): str(row.name).split("HMZ(")[1].split(")")[0]
        for row in tracks.itertuples(index=False)
    }
    hmz_by_block = {
        int(row.block_id): hmz_by_track.get(int(row.track_id), "U")
        for row in fragments[["block_id", "track_id"]].drop_duplicates().itertuples(index=False)
    }
    rows: list[dict[str, object]] = []
    for block_id, track_id in (
        fragments[["block_id", "track_id"]].drop_duplicates().itertuples(index=False)
    ):
        hmz = str(hmz_by_block.get(block_id, "U"))
        preferred = LEGAL_BY_HMZ.get(hmz)
        if preferred is None:
            continue
        labels = set(available.loc[available["track_id"] == track_id, "treatment"].astype(str))
        if preferred in labels:
            rows.append({"block_id": int(block_id), "treatment": preferred, "offset": 0})
        elif hmz in {"M", "A"} and "GWM_LOW" in labels:
            rows.append({"block_id": int(block_id), "treatment": "GWM_LOW", "offset": 0})
    return pd.DataFrame(rows, columns=["block_id", "treatment", "offset"])


def main() -> None:
    """Build and run the baseline and two selection regimes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--years", type=int, default=30)
    parser.add_argument("--evidence", type=Path, default=None)
    args = parser.parse_args()

    args.runtime.mkdir(parents=True, exist_ok=True)
    baseline = args.runtime / "baseline_no_cut.csv"
    pd.DataFrame(columns=["block_id", "treatment", "offset"]).to_csv(baseline, index=False)
    schedules = {"baseline_no_cut": baseline}
    for name, (preferred, fallback) in REGIMES.items():
        path = args.runtime / f"{name}.csv"
        schedule = _schedule(args.dataset, preferred, fallback)
        schedule.to_csv(path, index=False)
        schedules[name] = path
        print(f"{name}: {len(schedule)} blocks")
    legal = args.runtime / "selection_gwm_legal.csv"
    legal_schedule = _legal_schedule(args.dataset)
    legal_schedule.to_csv(legal, index=False)
    schedules["selection_gwm_legal"] = legal
    print(f"selection_gwm_legal: {len(legal_schedule)} blocks")

    evidence_dir = args.evidence.parent / "scenario_reports" if args.evidence else None
    manifests: dict[str, object] = {}
    for name, schedule in schedules.items():
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
                str(schedule),
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
                "python",
                "runbooks/normalize_kc_accounts.py",
                "--dataset",
                str(args.dataset),
                "--runs",
                str(args.runtime),
            ]
        )
        _run(
            [
                "ws4",
                "report",
                "--run",
                str(run_dir),
                "--targets",
                str(args.targets),
                "--out",
                str(run_dir / "report"),
            ]
        )
        if evidence_dir is not None:
            target_dir = evidence_dir / name
            target_dir.mkdir(parents=True, exist_ok=True)
            for filename in (
                "report/report_targets.csv",
                "report/report_accounts.csv",
                "account_values.csv",
                "product_values.csv",
                "patch_accounts.csv",
            ):
                source = run_dir / filename
                if source.exists():
                    shutil.copy2(source, target_dir / source.name)
        manifests[name] = {
            "schedule": str(schedule),
            "blocks": len(pd.read_csv(schedule)),
            "run": str(run_dir),
        }

    result = {
        "dataset": str(args.dataset),
        "years": args.years,
        "runs": manifests,
        "caveats": [
            "Structural smoke regimes, not reviewed management prescriptions.",
            "No calibrated-growth or legal-compliance claim.",
        ],
    }
    evidence = args.evidence or (args.runtime / "scenario_manifest.json")
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
