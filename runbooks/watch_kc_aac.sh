#!/usr/bin/env bash
# Watch a KC AAC/even-flow search live.
#
# Usage:
#   bash runbooks/watch_kc_aac.sh [iterations]
#
# Examples:
#   bash runbooks/watch_kc_aac.sh 50000
#   PLAIN=1 bash runbooks/watch_kc_aac.sh 50000
#   MODEL=calibrated bash runbooks/watch_kc_aac.sh 50000
#   ISLANDS=8 bash runbooks/watch_kc_aac.sh 100000
#
# Environment:
#   MODEL       uncalibrated (default) or calibrated
#   DATASET     override the compiled dataset
#   INITIAL     override the starting schedule
#   TARGETS     override the targets YAML
#   PLAIN=1     print one final frame instead of the live TUI
#   ISLANDS     parallel search islands (0 = one search)
#   REFRESH     live repaint interval in seconds
#   YEARS       simulation horizon (default: 200)
#   PERIOD      period width in years (default: 10)
#
# This is the watcher only. To write a schedule and AAC summary, use
# `ws4 optimize ... --out <dir>` and then `runbooks/summarize_kc_aac.py`.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL="${MODEL:-uncalibrated}"
ITERATIONS="${1:-50000}"
PLAIN="${PLAIN:-0}"
ISLANDS="${ISLANDS:-0}"
REFRESH="${REFRESH:-2}"
YEARS="${YEARS:-200}"
PERIOD="${PERIOD:-10}"

case "$MODEL" in
  uncalibrated)
    DEFAULT_DATASET="$ROOT/ws4/dataset_kc_au_stages_v1"
    DEFAULT_INITIAL="$ROOT/ws4/runtime/kc_au_stages/selection_gwm_legal.csv"
    ;;
  calibrated)
    DEFAULT_DATASET="$ROOT/ws4/dataset_kc_au_stages_calibrated_v1"
    DEFAULT_INITIAL="$ROOT/ws4/runtime/kc_au_stages_calibrated/selection_gwm_legal.csv"
    ;;
  *)
    echo "MODEL must be 'uncalibrated' or 'calibrated' (got '$MODEL')" >&2
    exit 2
    ;;
esac

DATASET="${DATASET:-$DEFAULT_DATASET}"
INITIAL="${INITIAL:-$DEFAULT_INITIAL}"
TARGETS="${TARGETS:-$ROOT/ws4/targets_kc_evenflow.yaml}"

for path in "$DATASET" "$INITIAL" "$TARGETS" "$ROOT/ws4/topology.csv" "$ROOT/ws4/patch_accounts.yaml"; do
  if [[ ! -e "$path" ]]; then
    echo "missing required path: $path" >&2
    exit 2
  fi
done

args=(
  watch
  --dataset "$DATASET"
  --targets "$TARGETS"
  --account product.yield.managed.total
  --account feature.yield.managed.total
  --account product.area.managed.total
  --account feature.area.managed.total
  --years "$YEARS"
  --period-width "$PERIOD"
  --iterations "$ITERATIONS"
  --seed 1
  --refresh "$REFRESH"
  --islands "$ISLANDS"
  --topology "$ROOT/ws4/topology.csv"
  --patch-accounts "$ROOT/ws4/patch_accounts.yaml"
  --initial-schedule "$INITIAL"
)

if [[ "$PLAIN" == "1" ]]; then
  args+=(--plain)
fi

echo "model=$MODEL"
echo "dataset=$DATASET"
echo "initial=$INITIAL"
echo "iterations=$ITERATIONS"
exec ws4 "${args[@]}"
