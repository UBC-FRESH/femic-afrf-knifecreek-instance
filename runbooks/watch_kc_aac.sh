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
#   MODEL=split bash runbooks/watch_kc_aac.sh 50000
#   MODEL=split_volume bash runbooks/watch_kc_aac.sh 50000
#   ISLANDS=8 bash runbooks/watch_kc_aac.sh 100000
#
# Environment:
#   MODEL       uncalibrated (default), calibrated, or split
#   DATASET     override the compiled dataset
#   INITIAL     override the starting schedule
#   TARGETS     override the targets YAML
#   TOPOLOGY    override the ws4 topology CSV
#   PATCH_ACCOUNTS override the patch-account YAML
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
    DEFAULT_TOPOLOGY="$ROOT/ws4/topology.csv"
    ;;
  calibrated)
    DEFAULT_DATASET="$ROOT/ws4/dataset_kc_au_stages_calibrated_v1"
    DEFAULT_INITIAL="$ROOT/ws4/runtime/kc_au_stages_calibrated/selection_gwm_legal.csv"
    DEFAULT_TOPOLOGY="$ROOT/ws4/topology.csv"
    ;;
  split)
    DEFAULT_DATASET="$ROOT/ws4/dataset_kc_au_stages_split_v1"
    DEFAULT_INITIAL="$ROOT/data/kc_ws4_recipe_au_stages_split/selection_gwm_legal.csv"
    DEFAULT_TOPOLOGY="$ROOT/ws4/topology_split.csv"
    ;;
  split_volume)
    DEFAULT_DATASET="$ROOT/ws4/dataset_kc_au_stages_split_volume_v1"
    DEFAULT_INITIAL="$ROOT/data/kc_ws4_recipe_au_stages_split/selection_gwm_legal.csv"
    DEFAULT_TOPOLOGY="$ROOT/ws4/topology_split.csv"
    ;;
  *)
    echo "MODEL must be 'uncalibrated', 'calibrated', 'split' or 'split_volume' (got '$MODEL')" >&2
    exit 2
    ;;
esac

DATASET="${DATASET:-$DEFAULT_DATASET}"
INITIAL="${INITIAL:-$DEFAULT_INITIAL}"
TARGETS="${TARGETS:-$ROOT/ws4/targets_kc_evenflow.yaml}"
TOPOLOGY="${TOPOLOGY:-$DEFAULT_TOPOLOGY}"
PATCH_ACCOUNTS="${PATCH_ACCOUNTS:-$ROOT/ws4/patch_accounts.yaml}"

for path in "$DATASET" "$INITIAL" "$TARGETS" "$TOPOLOGY" "$PATCH_ACCOUNTS"; do
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
  --topology "$TOPOLOGY"
  --patch-accounts "$PATCH_ACCOUNTS"
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
