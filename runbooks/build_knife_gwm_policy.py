#!/usr/bin/env python3
"""Build the Knife Creek multi-entry GWM policy schedule.

The schedule follows the compiled canonical state graph. For each block, the
runbook chooses the allowed treatment path with the largest cumulative
canonical cut over ten 30-year entries, then staggers the first entry across
30 phases. This is a reproducible policy screen, not an optimizer replacement
and not an approved management plan.

Usage::

    python runbooks/build_knife_gwm_policy.py \
      --dataset ws4/dataset_kc_spatial_v4 \
      --canonical ws4/state_library_v2/canonical \
      --out /tmp/knife_gwm_policy_schedule.csv
"""

from __future__ import annotations

import argparse
from functools import cache
from pathlib import Path

import pandas as pd


def _as_int(value: object) -> int:
    """Return an integer from a pandas scalar."""
    return int(str(value))


def _as_float(value: object) -> float:
    """Return a float from a pandas scalar."""
    return float(str(value))


def _state_of_track(track_name: str) -> str:
    """Return the canonical state portion of a dataset track name."""
    return str(track_name).split("__HMZ_", 1)[0]


def _load_edges(
    tracks: pd.DataFrame,
    treatments: pd.DataFrame,
    transitions: pd.DataFrame,
) -> dict[int, list[tuple[str, int, float]]]:
    """Build track-level treatment edges with canonical cut volumes."""
    state = {
        _as_int(row.track_id): _state_of_track(str(row.name))
        for row in tracks.itertuples(index=False)
    }
    cut = {
        (str(row.from_state), str(row.regime), str(row.to_state)): _as_float(row.fvs_cut_m3_ha)
        for row in transitions.itertuples(index=False)
    }
    edges: dict[int, list[tuple[str, int, float]]] = {}
    for row in treatments.itertuples(index=False):
        source = _as_int(row.track_id)
        target = _as_int(row.new_track)
        treatment = str(row.treatment)
        volume = cut.get((state[source], treatment, state[target]), 0.0)
        edges.setdefault(source, []).append((treatment, target, volume))
    return edges


def _best_paths(
    edges: dict[int, list[tuple[str, int, float]]],
    starts: list[int],
    entries: int,
) -> dict[int, tuple[tuple[str, int], ...]]:
    """Return the maximum-cut path for each starting track."""

    @cache
    def best(track: int, steps: int) -> tuple[float, tuple[tuple[str, int], ...]]:
        if steps <= 0 or track not in edges:
            return (0.0, ())
        best_value = -1.0
        best_path: tuple[tuple[str, int], ...] = ()
        for treatment, target, volume in edges[track]:
            tail_value, tail = best(target, steps - 1)
            value = volume + tail_value
            if value > best_value:
                best_value = value
                best_path = ((treatment, target), *tail)
        return (best_value, best_path)

    return {start: best(start, entries)[1] for start in starts}


def build_schedule(
    *,
    dataset: Path,
    canonical: Path,
    entries: int,
    phases: int,
) -> pd.DataFrame:
    """Build a block/treatment/offset schedule CSV frame."""
    blocks = pd.read_parquet(dataset / "blocks.parquet")
    tracks = pd.read_parquet(dataset / "tracks.parquet")
    treatments = pd.read_parquet(dataset / "treatments.parquet")
    transitions = pd.read_csv(canonical / "transitions.csv")
    edges = _load_edges(tracks, treatments, transitions)
    starts = [_as_int(value) for value in blocks["track_id"].tolist()]
    paths = _best_paths(edges, starts, entries)
    rows: list[dict[str, int | str]] = []
    for block in blocks.itertuples(index=False):
        phase = _as_int(block.block_id) % phases
        for step, (treatment, _target) in enumerate(paths[_as_int(block.track_id)]):
            rows.append(
                {
                    "block_id": _as_int(block.block_id),
                    "treatment": treatment,
                    "offset": phase + 30 * step,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    """Write the GWM policy schedule."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--entries", type=int, default=10)
    parser.add_argument("--phases", type=int, default=30)
    args = parser.parse_args()
    if args.entries < 1 or args.phases < 1:
        raise ValueError("--entries and --phases must be positive")
    schedule = build_schedule(
        dataset=args.dataset,
        canonical=args.canonical,
        entries=args.entries,
        phases=args.phases,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    schedule.to_csv(args.out, index=False)
    print(
        f"scheduled_blocks={schedule['block_id'].nunique()} "
        f"events={len(schedule)} "
        f"max_offset={_as_int(schedule['offset'].max()) if len(schedule) else 0}"
    )


if __name__ == "__main__":
    main()
