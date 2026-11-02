"""Tests for the FVS-BC empirical envelope flags."""

from __future__ import annotations

import pytest

from fvs_envelope import EnvelopeLimit, check_envelope


def test_inside_envelope_passes() -> None:
    result = check_envelope("IDFdk3", ba=45.0, qmd=25.0, tph=500.0)
    assert result.passed
    assert result.flags == ()


def test_ba_above_p99_is_a_warning_not_a_max_flag() -> None:
    result = check_envelope("IDFdk3", ba=56.0)
    assert not result.passed
    assert len(result.flags) == 1
    assert "p99" in result.flags[0]


def test_ba_above_observed_max_is_a_hard_flag() -> None:
    result = check_envelope("IDFdk3", ba=67.0)
    assert any("observed max" in flag for flag in result.flags)


def test_qmd_above_max_is_flagged() -> None:
    result = check_envelope("IDFxm", ba=45.0, qmd=50.0)
    assert any("QMD" in flag and "observed max" in flag for flag in result.flags)


def test_low_tph_is_flagged() -> None:
    result = check_envelope("IDFdk3", ba=45.0, tph=150.0)
    assert any("TPH" in flag and "observed min" in flag for flag in result.flags)


def test_unknown_bec_is_rejected() -> None:
    with pytest.raises(ValueError, match="no envelope"):
        check_envelope("SBSdw1", ba=30.0)


def test_custom_limits_are_used() -> None:
    limits = {"TEST": EnvelopeLimit(50.0, 60.0, 25.0, 30.0, 200.0, 100.0)}
    result = check_envelope("TEST", ba=55.0, qmd=26.0, tph=150.0, limits=limits)
    assert len(result.flags) == 3
    assert result.passed is False
