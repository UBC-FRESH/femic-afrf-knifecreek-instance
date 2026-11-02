"""Tests for the state-graph validator."""

from __future__ import annotations

from state_graph import validate_graph


def _node(state: str, stages: str = "1") -> dict[str, object]:
    return {
        "au_id": "AU1",
        "state_id": state,
        "stages": stages,
        "ba_mean": 45.0,
        "qmd_mean": 25.0,
        "tph_mean": 500.0,
        "BEC": "IDFdk3",
    }


def _edge(source: str, target: str) -> dict[str, str]:
    return {"au_id": "AU1", "state_id": source, "next_state": target}


def test_complete_graph_passes() -> None:
    result = validate_graph(
        [_node("A", "1,2"), _node("B", "3,4"), _node("T", "6")],
        [_edge("A", "B"), _edge("B", "T")],
    )
    assert result.passed
    assert result.nodes == 3
    assert result.edges == 2


def test_missing_edge_target_is_rejected() -> None:
    result = validate_graph([_node("A", "1"), _node("T", "6")], [_edge("A", "X")])
    assert any("target missing" in problem for problem in result.problems)


def test_non_terminal_dead_end_is_rejected() -> None:
    result = validate_graph([_node("A", "1"), _node("T", "6")], [])
    assert any("non-terminal dead end" in problem for problem in result.problems)


def test_terminal_dead_end_is_allowed() -> None:
    result = validate_graph([_node("A", "1"), _node("T", "6")], [_edge("A", "T")])
    assert result.passed


def test_duplicate_node_is_rejected() -> None:
    result = validate_graph([_node("A", "1"), _node("A", "1"), _node("T", "6")], [_edge("A", "T")])
    assert any("duplicate" in problem for problem in result.problems)


def test_missing_terminal_state_is_rejected() -> None:
    result = validate_graph([_node("A", "1")], [])
    assert any("no terminal" in problem for problem in result.problems)


def test_stage_six_in_a_mixed_stage_node_is_terminal() -> None:
    result = validate_graph([_node("A", "1,2,6"), _node("B", "3,6")], [_edge("A", "B")])
    assert result.passed


def test_self_edge_is_allowed() -> None:
    result = validate_graph([_node("A", "1,6")], [_edge("A", "A")])
    assert result.passed


def test_envelope_violation_is_rejected() -> None:
    node = _node("A", "1")
    node["qmd_mean"] = 50.0
    result = validate_graph([node, _node("T", "6")], [_edge("A", "T")])
    assert any("envelope" in problem for problem in result.problems)
