#!/usr/bin/env python3
"""Attach KC spatial account groups to a compiled ws4 dataset.

WS4's compiler writes only the default ``forest`` group.  The KC account
structure also needs the HMZ, clump and reserve classes that come from the
fragment inventory, so this runbook adds those memberships after the build.

Usage::

    python runbooks/build_kc_account_groups.py \
      --dataset ws4/dataset_kc_v1 \
      --fragments data/patchworks_knifecreek/fragments.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

GROUP_COLUMNS = {
    "HMZ": "hmz",
    "CLUMP": "clump",
    "RESERVE": "reserve",
}


def _clean(value: object) -> str:
    """Return a stable group token."""
    return str(value).strip().lower().replace(" ", "_").replace("/", "_")


def main() -> None:
    """Write multiple group memberships for every compiled block."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--fragments", type=Path, required=True)
    args = parser.parse_args()

    fragments = pd.read_parquet(args.dataset / "fragments.parquet")
    source = pd.read_csv(args.fragments)
    required = {"BLOCK", *GROUP_COLUMNS}
    missing = sorted(required - set(source.columns))
    if missing:
        raise ValueError(f"fragment source is missing group columns: {missing}")

    memberships = fragments[["block_id"]].drop_duplicates().copy()
    memberships = memberships.merge(
        source[["BLOCK", *GROUP_COLUMNS]].drop_duplicates("BLOCK"),
        left_on="block_id",
        right_on="BLOCK",
        how="left",
    )
    if memberships[list(GROUP_COLUMNS)].isna().any().any():
        raise ValueError("one or more compiled blocks have no spatial group values")

    rows: list[dict[str, object]] = []
    for row in memberships.itertuples(index=False):
        block = int(row.block_id)
        rows.append({"block_id": block, "group": "forest"})
        rows.append({"block_id": block, "group": "ifm_managed"})
        for column, prefix in GROUP_COLUMNS.items():
            rows.append(
                {
                    "block_id": block,
                    "group": f"{prefix}_{_clean(getattr(row, column))}",
                }
            )

    groups = pd.DataFrame(rows, columns=["block_id", "group"])
    groups["group"] = groups["group"].astype("string")
    groups.to_parquet(args.dataset / "groups.parquet", index=False)
    print(
        f"groups={groups['group'].nunique()} rows={len(groups)} "
        f"blocks={groups['block_id'].nunique()}"
    )


if __name__ == "__main__":
    main()
