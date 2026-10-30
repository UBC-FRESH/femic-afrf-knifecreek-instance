#!/usr/bin/env python3
"""Normalize KC compiled-stratum cycle metadata to the source H matrix.

The WS4 compiler writes ``cycle=0`` because the recipe has no stratum-cycle
field. The KC source H matrix carries the 30-year selection entry cycle, so this
runbook copies that one metadata value into the compiled ``strata`` table. It
does not change growth curves or treatment windows.

Usage::

    python runbooks/normalize_kc_strata.py \
      --dataset ws4/dataset_kc_v1 \
      --h-dir data/patchworks_knifecreek/tracks/H
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    """Set the compiled stratum cycle from the source H matrix."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--h-dir", type=Path, required=True)
    args = parser.parse_args()

    source = pd.read_csv(args.h_dir / "strata.csv")
    cycles = sorted(int(value) for value in source["CYCLE"].dropna().unique())
    if len(cycles) != 1:
        raise ValueError(f"source H matrix has more than one cycle: {cycles}")
    cycle = cycles[0]
    if cycle <= 0:
        raise ValueError(f"source H matrix has a non-positive cycle: {cycle}")

    strata = pd.read_parquet(args.dataset / "strata.parquet")
    strata["cycle"] = cycle
    strata.to_parquet(args.dataset / "strata.parquet", index=False)
    print(f"strata={len(strata)} cycle={cycle}")


if __name__ == "__main__":
    main()
