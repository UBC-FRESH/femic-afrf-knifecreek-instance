#!/usr/bin/env python3
"""Ensure every run exposes the dataset's full account list.

The simulator omits an account when a run never produces it.  A no-cut baseline
therefore has no product account rows, which makes a wood-supply model look as
if it has no product accounts.  This runbook adds explicit zero rows for every
dataset account and offset that the run did not write.

Usage::

    python runbooks/normalize_kc_accounts.py \
      --dataset ws4/dataset_kc_v1 \
      --runs ws4/runtime/kc_v1
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _normalize(run_dir: Path, accounts: list[str]) -> None:
    """Add zero rows for missing account/offset combinations in one run."""
    path = run_dir / "account_values.csv"
    if not path.is_file():
        return
    frame = pd.read_csv(path)
    if not {"offset", "account", "value"}.issubset(frame.columns):
        raise ValueError(f"unexpected account_values schema in {path}")
    offsets = sorted({int(value) for value in frame["offset"].dropna().unique()})
    if not offsets:
        return
    existing = {
        (int(row.offset), str(row.account))
        for row in frame[["offset", "account"]].drop_duplicates().itertuples(index=False)
    }
    rows = [
        {"offset": offset, "account": account, "value": 0.0}
        for offset in offsets
        for account in accounts
        if (offset, account) not in existing
    ]
    if rows:
        frame = pd.concat([frame, pd.DataFrame(rows)], ignore_index=True)
        frame = frame.sort_values(["offset", "account"]).reset_index(drop=True)
        frame.to_csv(path, index=False)
    print(f"{run_dir.name}: added {len(rows)} zero account rows")


def main() -> None:
    """Normalize every run directory under a runtime root."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--runs", type=Path, required=True)
    args = parser.parse_args()

    accounts = sorted(
        {str(value) for value in pd.read_parquet(args.dataset / "accounts.parquet")["account"]}
    )
    for run_dir in sorted(path for path in args.runs.iterdir() if path.is_dir()):
        _normalize(run_dir, accounts)


if __name__ == "__main__":
    main()
