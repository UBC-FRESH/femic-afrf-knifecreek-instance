#!/usr/bin/env python3
"""Audit the KC ws4 feature, product and target account wiring.

This is a build-time check, not a growth validation.  It verifies that every
compiled account has a source curve and that every target names an account the
dataset can resolve.

Usage::

    python runbooks/audit_kc_accounts.py \
      --dataset ws4/dataset_kc_v1 \
      --targets ws4/targets_kc_smoke.yaml \
      --targets ws4/targets_kc_gwm2007.yaml \
      --out ws4/evidence/kc_v1/account_audit.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import yaml


def _target_accounts(path: Path) -> list[str]:
    """Return target account names from a target YAML file."""
    payload = yaml.safe_load(path.read_text()) or {}
    return [str(target["account"]) for target in payload.get("targets", [])]


def main() -> None:
    """Write a machine-readable account audit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--targets", type=Path, action="append", default=[])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    tables = {
        name: pd.read_parquet(args.dataset / f"{name}.parquet")
        for name in ("accounts", "features", "products", "curves")
    }
    accounts = set(tables["accounts"]["account"].astype(str))
    features = set(tables["features"]["label"].astype(str))
    products = set(tables["products"]["label"].astype(str))
    curve_ids = set(tables["curves"]["curve_id"].astype(int))
    feature_curves = set(tables["features"]["curve_id"].astype(int))
    product_curves = set(tables["products"]["curve_id"].astype(int))
    target_accounts = {path.name: _target_accounts(path) for path in args.targets}
    pairs = {
        account: "feature." + account[len("product.") :]
        for account in accounts
        if account.startswith("product.")
    }

    issues: list[str] = []
    for label in sorted(features - accounts):
        issues.append(f"feature label has no account: {label}")
    for label in sorted(products - accounts):
        issues.append(f"product label has no account: {label}")
    for label in sorted(feature_curves - curve_ids):
        issues.append(f"feature curve is missing: {label}")
    for flow, level in sorted(pairs.items()):
        if level not in accounts:
            issues.append(f"product flow has no matching level account: {flow} -> {level}")
    for label in sorted(product_curves - curve_ids):
        issues.append(f"product curve is missing: {label}")
    for target_file, names in target_accounts.items():
        for name in sorted(set(names) - accounts):
            issues.append(f"{target_file} target has no account: {name}")

    result = {
        "dataset": str(args.dataset),
        "accounts": len(accounts),
        "features": len(features),
        "products": len(products),
        "product_level_pairs": pairs,
        "curves": len(curve_ids),
        "targets": target_accounts,
        "issues": issues,
        "ok": not issues,
        "limits": [
            "Large-tree BA, reserve BA, seral/opening and species-split accounts are not present.",
            "Group aggregation is membership only; it does not create new growth curves.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
