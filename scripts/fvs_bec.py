"""Build FVS-BC ``STDINFO`` BEC fields without silent fallback.

FVS-BC expects ``STDINFO`` fields 1 and 2 to concatenate into
``region + zone + subzone + /series``. A bare ``IDFdk3`` or an unrelated
placeholder is not rejected by FVS; it falls back to ``ICHmw2/01`` and changes
the default maximum basal area. This module makes that failure explicit.

The region codes are the three FVS-BC calibration regions: ``CAR`` (Cariboo),
``KAM`` (Kamloops), and ``NEL`` (Nelson).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = [
    "REGIONS",
    "ZONES",
    "FvsBec",
    "bec_from_label",
    "fvs_bec",
    "region_for_tsa",
    "stdinfo_parameters",
]

#: FVS-BC region codes.
REGIONS: tuple[str, ...] = ("CAR", "KAM", "NEL")

#: BEC zones the BC variant documents.
ZONES: tuple[str, ...] = ("ESSF", "ICH", "IDF", "MS", "PP", "SBS", "SBPS")

_LABEL = re.compile(r"^(ESSF|ICH|IDF|MS|PP|SBS|SBPS)([a-z]{2,3})([1-9])?$")
_SUBZONE = re.compile(r"^[a-z]{2,3}$")
_VARIANT = re.compile(r"^[1-9]$")
_SERIES = re.compile(r"^\d{2}(?:[a-z]|-[a-z]{2})?$")

_TSA_REGION: dict[str, str] = {
    "100 mile house tsa": "CAR",
    "williams lake tsa": "CAR",
    "quesnel tsa": "CAR",
    "cariboo": "CAR",
    "kamloops tsa": "KAM",
    "merritt tsa": "KAM",
    "okanagan tsa": "KAM",
    "invermere tsa": "NEL",
    "boundary tsa": "NEL",
    "kootenay": "NEL",
}


@dataclass(frozen=True, slots=True)
class FvsBec:
    """A validated FVS-BC region and BEC/site-series code.

    Attributes
    ----------
    region : str
        One of :data:`REGIONS`.
    bec : str
        A code such as ``IDFdk3/01`` or ``IDFxm/01``.
    """

    region: str
    bec: str

    @property
    def stdinfo(self) -> tuple[str, str]:
        """Return the two ``STDINFO`` fields.

        Returns
        -------
        tuple of str
            ``(region, bec)``, ready for ``Keyword("STDINFO", (*fields, ...))``.
        """
        return self.region, self.bec


def region_for_tsa(tsa: str) -> str:
    """Return the FVS-BC region for a known BC TSA name.

    Parameters
    ----------
    tsa : str
        TSA description, case-insensitive.

    Returns
    -------
    str
        ``CAR``, ``KAM``, or ``NEL``.

    Raises
    ------
    ValueError
        If the TSA is unknown. Unknown is not silently mapped to Cariboo.
    """
    key = tsa.strip().lower()
    try:
        return _TSA_REGION[key]
    except KeyError as error:
        raise ValueError(
            f"no FVS-BC region mapping for TSA {tsa!r}; add an explicit mapping"
        ) from error


def fvs_bec(
    *,
    region: str,
    zone: str,
    subzone: str,
    variant: str | None,
    series: str,
) -> FvsBec:
    """Validate and assemble an FVS-BC BEC/site-series code.

    Parameters
    ----------
    region : str
        ``CAR``, ``KAM``, or ``NEL``.
    zone : str
        One of :data:`ZONES`.
    subzone : str
        Lower-case subzone, e.g. ``dk`` or ``xm``.
    variant : str or None
        Single digit 1-9, or ``None`` when the BEC has no variant.
    series : str
        Two-digit site series, optionally with a lower-case phase suffix,
        e.g. ``01``, ``01a``, or ``01-ys``.

    Returns
    -------
    FvsBec
        The validated code.

    Raises
    ------
    ValueError
        If any component is invalid. The error names the bad component.
    """
    region = region.strip().upper()
    zone = zone.strip().upper()
    subzone = subzone.strip().lower()
    series = series.strip().lower()

    if region not in REGIONS:
        raise ValueError(f"region must be one of {REGIONS}, not {region!r}")
    if zone not in ZONES:
        raise ValueError(f"zone must be one of {ZONES}, not {zone!r}")
    if not _SUBZONE.fullmatch(subzone):
        raise ValueError(f"subzone must be two or three lower-case letters, not {subzone!r}")
    if variant is not None and not _VARIANT.fullmatch(variant):
        raise ValueError(f"variant must be a single digit 1-9 or None, not {variant!r}")
    if not _SERIES.fullmatch(series):
        raise ValueError(f"series must be like 01, 01a, or 01-ys, not {series!r}")

    return FvsBec(region=region, bec=f"{zone}{subzone}{variant or ''}/{series}")


def bec_from_label(label: str, *, region: str, series: str) -> FvsBec:
    """Parse a BEC label such as ``IDFdk3`` and append a site series.

    Parameters
    ----------
    label : str
        BEC label with optional variant, e.g. ``IDFdk3``, ``IDFxm``, ``SBSdw1``.
    region : str
        ``CAR``, ``KAM``, or ``NEL``.
    series : str
        Site-series code, e.g. ``01``.

    Returns
    -------
    FvsBec
        The validated code.

    Raises
    ------
    ValueError
        If the label is not a recognized BEC label, or any component is
        invalid. A legacy placeholder such as ``CHS131`` fails here rather than
        silently becoming ICHmw2/01 in FVS.
    """
    match = _LABEL.fullmatch(label.strip())
    if match is None:
        raise ValueError(
            f"BEC label {label!r} is not a zone+subzone+variant label; "
            "use a value such as IDFdk3 or IDFxm"
        )
    zone, subzone, variant = match.groups()
    return fvs_bec(
        region=region,
        zone=zone,
        subzone=subzone,
        variant=variant,
        series=series,
    )


def stdinfo_parameters(label: str, *, region: str, series: str) -> tuple[str, str]:
    """Return the two ``STDINFO`` fields for a BEC label and site series.

    Parameters
    ----------
    label : str
        BEC label such as ``IDFdk3``.
    region : str
        ``CAR``, ``KAM``, or ``NEL``.
    series : str
        Site-series code, e.g. ``01``.

    Returns
    -------
    tuple of str
        ``(region, bec)``.
    """
    return bec_from_label(label, region=region, series=series).stdinfo
