"""Validate a BA/QMD state graph before compilation.

The graph is a set of nodes keyed by ``(au_id, state_id)`` and directed edges
to the next state. The validator checks:

- unique node keys and edge endpoints;
- every non-terminal node has at least one outgoing edge;
- terminal nodes are only the declared final stages;
- every AU reaches a terminal state;
- every node passes the empirical BA/QMD/TPH envelope.

This is a structural check, not a growth or AAC validation.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from fvs_envelope import check_envelope

__all__ = ["GraphCheck", "validate_graph"]


@dataclass(frozen=True, slots=True)
class GraphCheck:
    """Result of validating one state graph."""

    nodes: int
    edges: int
    problems: tuple[str, ...]

    @property
    def passed(self) -> bool:
        """Return True when no problem was found."""
        return not self.problems


def validate_graph(
    nodes: Iterable[Mapping[str, object]],
    edges: Iterable[Mapping[str, object]],
    *,
    terminal_stage: str = "6",
) -> GraphCheck:
    """Validate a state graph for completeness and envelope compliance.

    Parameters
    ----------
    nodes : iterable of mapping
        Node records with ``au_id``, ``state_id``, ``stages``, ``ba_mean``,
        ``qmd_mean``, ``tph_mean``, and ``BEC``.
    edges : iterable of mapping
        Edge records with ``au_id``, ``state_id``, and ``next_state``.
    terminal_stage : str, optional
        Stage string that identifies a terminal state. Defaults to ``"6"``.

    Returns
    -------
    GraphCheck
        Counts and a tuple of human-readable problems.
    """
    node_list = list(nodes)
    edge_list = list(edges)
    keys = {(str(row["au_id"]), str(row["state_id"])) for row in node_list}
    problems: list[str] = []

    if len(keys) != len(node_list):
        problems.append("duplicate node keys")

    outgoing: dict[tuple[str, str], int] = dict.fromkeys(keys, 0)
    terminal_keys: set[tuple[str, str]] = set()
    for row in node_list:
        key = (str(row["au_id"]), str(row["state_id"]))
        stages = {part.strip() for part in str(row["stages"]).split(",")}
        if stages == {terminal_stage}:
            terminal_keys.add(key)
        bec = str(row["BEC"])
        check = check_envelope(
            bec,
            ba=float(str(row["ba_mean"])),
            qmd=float(str(row["qmd_mean"])),
            tph=float(str(row["tph_mean"])),
        )
        if not check.passed:
            problems.append(f"{key[0]}/{key[1]} envelope: {'; '.join(check.flags)}")

    for row in edge_list:
        source = (str(row["au_id"]), str(row["state_id"]))
        target = (str(row["au_id"]), str(row["next_state"]))
        if source not in keys:
            problems.append(f"edge source missing: {source[0]}/{source[1]}")
            continue
        if target not in keys:
            problems.append(f"edge target missing: {target[0]}/{target[1]}")
            continue
        if source == target:
            problems.append(f"self edge: {source[0]}/{source[1]}")
        outgoing[source] += 1

    for key, count in outgoing.items():
        if count == 0 and key not in terminal_keys:
            problems.append(f"non-terminal dead end: {key[0]}/{key[1]}")

    aus = {key[0] for key in keys}
    for au_id in aus:
        if not any(key[0] == au_id for key in terminal_keys):
            problems.append(f"no terminal state for {au_id}")

    return GraphCheck(nodes=len(node_list), edges=len(edge_list), problems=tuple(problems))
