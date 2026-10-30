#!/usr/bin/env bash
# Run the KC even-flow harvest-volume scenario in WS4 watch mode.
#
# Usage:
#   bash runbooks/run_kc_evenflow.sh [iterations]
#
# The KC product curves cover 30 years, so the current horizon is three
# 10-year periods. Extend the product curves before using a longer horizon.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ITERATIONS="${1:-100000}"
ISLANDS="${ISLANDS:-0}"
REFRESH="${REFRESH:-2}"
YEARS="${YEARS:-30}"
PERIOD_WIDTH="${PERIOD_WIDTH:-10}"

args=(
  watch
  --dataset "$ROOT/ws4/dataset_kc_v1"
  --targets "$ROOT/ws4/targets_kc_evenflow.yaml"
  --account product.yield.managed.total
  --account feature.yield.managed.total
  --account product.area.managed.total
  --account feature.area.managed.total
  --years "$YEARS"
  --period-width "$PERIOD_WIDTH"
  --iterations "$ITERATIONS"
  --seed 1
  --seed-greedy
  --refresh "$REFRESH"
  --islands "$ISLANDS"
)

if [[ "${PLAIN:-0}" == "1" ]]; then
  args+=(--plain)
fi

DEFAULT_SEED="$ROOT/ws4/runtime/kc_v1/selection_gwm_moderate.csv"
if [[ -n "${INITIAL:-}" ]]; then
  args+=(--initial-schedule "$INITIAL")
elif [[ -f "$DEFAULT_SEED" ]]; then
  args+=(--initial-schedule "$DEFAULT_SEED")
fi

exec ws4 "${args[@]}"
