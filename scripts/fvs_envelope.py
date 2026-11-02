"""Plausibility flags for FVS-BC IDF stand states.

The envelope is empirical, not a biological maximum. It is derived from the
FAIB PSP plot summaries used in the 2026-11 mortality work:

- BA: p99 and observed maximum by BEC.
- QMD: p99 and observed maximum by BEC.
- TPH: first percentile and observed minimum by BEC.

A state above the p99 is a warning; a state above the observed maximum is a
hard flag. Low TPH is flagged against the first percentile, because FVS-BC has
no regeneration/ingrowth and drifts toward a few large trees.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "DEFAULT_ENVELOPE",
    "EnvelopeCheck",
    "EnvelopeLimit",
    "check_envelope",
]


@dataclass(frozen=True, slots=True)
class EnvelopeLimit:
    """Empirical limits for one BEC unit."""

    ba_p99: float
    ba_max: float
    qmd_p99: float
    qmd_max: float
    tph_p01: float
    tph_min: float


@dataclass(frozen=True, slots=True)
class EnvelopeCheck:
    """Result of checking one stand state against an envelope."""

    bec: str
    ba: float
    qmd: float | None
    tph: float | None
    flags: tuple[str, ...] = field(default_factory=tuple)

    @property
    def passed(self) -> bool:
        """Return True when no flag was raised."""
        return not self.flags


# Values are from `ba_envelope_and_mortality_by_bec.csv` and
# `kc-psp-qmd-tph-envelope.csv` (FAIB PSP, 2026-11 snapshot).
DEFAULT_ENVELOPE: dict[str, EnvelopeLimit] = {
    "IDFdk": EnvelopeLimit(55.1, 55.5, 46.4, 46.6, 193.3, 192.6),
    "IDFdk1": EnvelopeLimit(45.0, 46.5, 34.8, 43.2, 209.1, 187.1),
    "IDFdk2": EnvelopeLimit(55.2, 60.2, 29.9, 35.9, 314.0, 237.9),
    "IDFdk3": EnvelopeLimit(54.1, 63.7, 27.2, 45.8, 279.5, 187.1),
    "IDFdk4": EnvelopeLimit(51.3, 52.4, 24.0, 26.0, 593.7, 410.1),
    "IDFdk5": EnvelopeLimit(36.0, 37.4, 29.3, 30.0, 479.2, 472.6),
    "IDFxm": EnvelopeLimit(52.9, 53.8, 26.7, 26.8, 251.8, 199.9),
}


def check_envelope(
    bec: str,
    *,
    ba: float,
    qmd: float | None = None,
    tph: float | None = None,
    limits: dict[str, EnvelopeLimit] | None = None,
) -> EnvelopeCheck:
    """Check one stand state against the empirical BEC envelope.

    Parameters
    ----------
    bec : str
        BEC code, e.g. ``IDFdk3``.
    ba : float
        Basal area in m²/ha.
    qmd : float or None, optional
        Quadratic mean diameter in cm. ``None`` skips the QMD checks.
    tph : float or None, optional
        Trees per hectare. ``None`` skips the low-TPH checks.
    limits : dict of str to EnvelopeLimit or None, optional
        Alternative envelope. Defaults to :data:`DEFAULT_ENVELOPE`.

    Returns
    -------
    EnvelopeCheck
        The state and its flags.

    Raises
    ------
    ValueError
        If the BEC has no envelope.
    """
    table = DEFAULT_ENVELOPE if limits is None else limits
    try:
        limit = table[bec]
    except KeyError as error:
        raise ValueError(f"no envelope for BEC {bec!r}") from error

    flags: list[str] = []
    if ba > limit.ba_max:
        flags.append(f"BA {ba:.1f} > observed max {limit.ba_max:.1f}")
    elif ba > limit.ba_p99:
        flags.append(f"BA {ba:.1f} > p99 {limit.ba_p99:.1f}")
    if qmd is not None:
        if qmd > limit.qmd_max:
            flags.append(f"QMD {qmd:.1f} > observed max {limit.qmd_max:.1f}")
        elif qmd > limit.qmd_p99:
            flags.append(f"QMD {qmd:.1f} > p99 {limit.qmd_p99:.1f}")
    if tph is not None:
        if tph < limit.tph_min:
            flags.append(f"TPH {tph:.0f} < observed min {limit.tph_min:.0f}")
        elif tph < limit.tph_p01:
            flags.append(f"TPH {tph:.0f} < p01 {limit.tph_p01:.0f}")
    return EnvelopeCheck(bec=bec, ba=ba, qmd=qmd, tph=tph, flags=tuple(flags))
