#!/usr/bin/env python3
"""Summarize a KC harvest run into period volumes and an AAC range.

This is a model-based AAC calculation, not a statutory determination.  It reads
the aggregate `product.yield.managed.total` rows from a ws4 run, sums them by
10-year period, and reports the implied annual cut.

Usage::

    python runbooks/summarize_kc_aac.py --run ws4/runtime/kc_aac_50k
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> None:
    """Write period volumes, AAC and target status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--period-width", type=int, default=10)
    args = parser.parse_args()
    products = pd.read_csv(args.run / "product_values.csv")
    total = products[products["account"] == "product.yield.managed.total"].copy()
    total["period"] = (total["offset"] // args.period_width) + 1
    period = total.groupby("period", as_index=False)["value"].sum()
    period["annual_aac_m3"] = period["value"] / args.period_width
    summary = {
        "run": str(args.run),
        "periods": int(period["period"].max()),
        "period_width_years": args.period_width,
        "mean_period_m3": float(period["value"].mean()),
        "min_period_m3": float(period["value"].min()),
        "max_period_m3": float(period["value"].max()),
        "mean_aac_m3_year": float(period["annual_aac_m3"].mean()),
        "min_aac_m3_year": float(period["annual_aac_m3"].min()),
        "max_aac_m3_year": float(period["annual_aac_m3"].max()),
        "total_m3": float(period["value"].sum()),
    }
    period.to_csv(args.run / "aac_periods.csv", index=False)
    report_path = args.run / "report_targets.csv"
    if report_path.exists():
        report = pd.read_csv(report_path)
        summary["target_status"] = report.groupby("status").size().to_dict()
    (args.run / "aac_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(period.to_string(index=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
