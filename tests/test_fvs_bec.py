"""Tests for the FVS-BC BEC and site-series helper."""

from __future__ import annotations

import pytest

from fvs_bec import (
    REGIONS,
    ZONES,
    FvsBec,
    bec_from_label,
    fvs_bec,
    region_for_tsa,
    stdinfo_parameters,
)


def test_idf_dk3_builds_the_expected_stdinfo() -> None:
    assert stdinfo_parameters("IDFdk3", region="CAR", series="01") == (
        "CAR",
        "IDFdk3/01",
    )


def test_idf_xm_without_variant_builds_the_expected_stdinfo() -> None:
    assert bec_from_label("IDFxm", region="CAR", series="01") == FvsBec(
        region="CAR",
        bec="IDFxm/01",
    )


def test_sbs_variant_builds_the_expected_stdinfo() -> None:
    assert stdinfo_parameters("SBSdw1", region="CAR", series="01") == (
        "CAR",
        "SBSdw1/01",
    )


def test_series_phase_suffix_is_preserved() -> None:
    assert stdinfo_parameters("ICHmw2", region="NEL", series="01a") == (
        "NEL",
        "ICHmw2/01a",
    )


def test_legacy_placeholder_is_rejected() -> None:
    with pytest.raises(ValueError, match="BEC label"):
        bec_from_label("CHS131", region="CAR", series="01")


def test_bare_zone_is_rejected() -> None:
    with pytest.raises(ValueError, match="BEC label"):
        bec_from_label("IDF", region="CAR", series="01")


def test_missing_series_is_rejected() -> None:
    with pytest.raises(ValueError, match="series"):
        stdinfo_parameters("IDFdk3", region="CAR", series="")


def test_unknown_region_is_rejected() -> None:
    with pytest.raises(ValueError, match="region"):
        fvs_bec(region="XYZ", zone="IDF", subzone="dk", variant="3", series="01")


def test_unknown_zone_is_rejected() -> None:
    with pytest.raises(ValueError, match="zone"):
        fvs_bec(region="CAR", zone="XYZ", subzone="dk", variant="3", series="01")


def test_bad_subzone_is_rejected() -> None:
    with pytest.raises(ValueError, match="subzone"):
        fvs_bec(region="CAR", zone="IDF", subzone="D", variant="3", series="01")


def test_bad_variant_is_rejected() -> None:
    with pytest.raises(ValueError, match="variant"):
        fvs_bec(region="CAR", zone="IDF", subzone="dk", variant="99", series="01")


def test_region_lookup_is_case_insensitive() -> None:
    assert region_for_tsa("Williams Lake TSA") == "CAR"
    assert region_for_tsa("kamloops tsa") == "KAM"
    assert region_for_tsa("Invermere TSA") == "NEL"


def test_unknown_tsa_is_rejected() -> None:
    with pytest.raises(ValueError, match="no FVS-BC region"):
        region_for_tsa("Unknown TSA")


def test_constants_are_the_documented_sets() -> None:
    assert REGIONS == ("CAR", "KAM", "NEL")
    assert ZONES == ("ESSF", "ICH", "IDF", "MS", "PP", "SBS", "SBPS")
