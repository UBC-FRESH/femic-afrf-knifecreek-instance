#!/usr/bin/env bash
# KC AU stage-model watcher.
#
# Usage:
#   bash runbooks/run_kc_evenflow.sh [iterations]
#
# Environment:
#   DATASET   compiled dataset (default: ws4/dataset_kc_au_stages_v1)
#   TARGETS   targets YAML (default: ws4/targets_kc_evenflow.yaml)
#   INITIAL   initial schedule CSV (default: runtime selection_gwm_low.csv)
#   ISLANDS   parallel islands (0 = one search)
#   REFRESH   seconds between live repaints
#   PLAIN=1   print one final frame instead of the live TUI
#
# Examples:
#   bash runbooks/run_kc_evenflow.sh
#   PLAIN=1 bash runbooks/run_kc_evenflow.sh 5000
#   ISLANDS=8 bash runbooks/run_kc_evenflow.sh 100000
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATASET="${DATASET:-$ROOT/ws4/dataset_kc_au_stages_v1}"
TARGETS="${TARGETS:-$ROOT/ws4/targets_kc_evenflow.yaml}"
ITERATIONS="${1:-100000}"
ISLANDS="${ISLANDS:-0}"
REFRESH="${REFRESH:-2}"
YEARS="${YEARS:-200}"
PERIOD_WIDTH="${PERIOD_WIDTH:-10}"

args=(
  watch
  --dataset "$DATASET"
  --targets "$TARGETS"
  --account product.yield.managed.total
  --account feature.yield.managed.total
  --account product.area.managed.total
  --account feature.area.managed.total
  --years "$YEARS"
  --period-width "$PERIOD_WIDTH"
  --iterations "$ITERATIONS"
  --seed 1
  --refresh "$REFRESH"
  --islands "$ISLANDS"
  --topology "$ROOT/ws4/topology.csv"
  --patch-accounts "$ROOT/ws4/patch_accounts.yaml"
)

if [[ "${PLAIN:-0}" == "1" ]]; then
  args+=(--plain)
fi

if [[ -n "${INITIAL:-}" ]]; then
  args+=(--initial-schedule "$INITIAL")
else
  for candidate in \
    "$ROOT/ws4/runtime/kc_au_stages/selection_gwm_low.csv" \
    "$ROOT/ws4/runtime/kc_au_stages/selection_gwm_moderate.csv"; do
    if [[ -f "$candidate" ]]; then
      args+=(--initial-schedule "$candidate")
      break
    fi
  done
fi

# If no schedule was found, let WS4 build a greedy seed.
if ! printf '%s\n' "${args[@]}" | grep -q -- '--initial-schedule'; then
  args+=(--seed-greedy)
fi

exec ws4 "${args[@]}"
