# FVS-BC BEC code correction

Date: 2026-11-02
Task: #127
Status: code and one-case check; full rerun pending

## Problem

The FVS-BC runbooks wrote:

```text
STDINFO   712       CHS131    ...
```

FVS-BC parses `STDINFO` fields 1 and 2 as
`region + zone + subzone + /site-series`. `712CHS131` contains none of those
tokens, so FVS falls back to **ICHmw2/01**:

```text
STDINFO    BEC=ICHmw2/01
MAXIMUM BASAL AREA FOR ICHmw2/01 IS SET BY DEFAULT TO: 89.0 SQ M/HA.
```

That is why the KC 200-year curve could reach 77 m²/ha.

## Fix

`scripts/fvs_bec.py` validates region, BEC label, and site series, and returns
the two `STDINFO` fields. It rejects the legacy `CHS131` string.

`runbooks/build_kc_au_yield_200y.py`, `build_kc_au_managed_200y.py`, and
`build_kc_au_multientry_200y.py` now:

- use the plot's BEC label and TSA region;
- take an explicit `--site-series` (diagnostic default `01`);
- writes `STDINFO` as `CAR IDFdk3/01` (or the actual plot BEC);
- records `fvs_bec` in the plot-match table and `site_series` in the manifest.

## Evidence

Real 1993 KC tree list (`KC_IDFdk3_FDI_M__4024754-PSP1`), no cut, no
calibration:

| STDINFO | Max BA | Final TPH |
|---|---:|---:|
| `712 / CHS131` | 77.4 m²/ha | 401 |
| `CAR / IDFdk3/01` | 49.6 m²/ha | 258 |

One runbook case (`KC_IDFdk3_FDI_H`, one FAIB plot, series `01`):

```text
STDINFO BEC=IDFdk3/01
MAXIMUM BASAL AREA FOR IDFdk3/01 ... 53.0 SQ M/HA.
```

200-year max BA: **52.0 m²/ha**. The old curve reached 77 m²/ha.

1993–2013 backtest on 24 KC plots:

| Run | 2013 BA bias | BA MAE | TPH bias | TPH MAE |
|---|---:|---:|---:|---:|
| legacy | +1.04 m²/ha | 3.94 | +421.8 | 514.6 |
| corrected | −1.29 m²/ha | 2.96 | +249.5 | 421.5 |

The BEC fix reduces TPH overshoot but leaves a positive TPH bias. That residual
is the mortality-calibration target.

A six-AU corrected-BEC diagnostic (one plot per AU, no calibration) gave:

| AU | Max BA (m²/ha) |
|---|---:|
| KC_IDFdk3_FDI_H | 52 |
| KC_IDFdk3_FDI_L | 43 |
| KC_IDFdk3_FDI_M | 50 |
| KC_IDFxm_FDI_H | 57 |
| KC_IDFxm_FDI_L | 28 |
| KC_IDFxm_FDI_M | 45 |

The IDFxm H AU exceeds its 30 m²/ha default by 27 m²/ha. The default did not
bind; explicit `BAMAX` and an IDFxm capacity decision are still required.

The full six-AU, 28-plot no-cut diagnostic (five plots per AU, series `01`, no
calibration) gives 200-year volumes of **353–589 m³/ha**, versus **750–1,232
m³/ha** on the old ICH-default curves. Managed year-170 volumes are
**339–517 m³/ha** versus **614–917 m³/ha**; first multi-entry volume is
**163–196 m³/ha** versus **219–287 m³/ha**. That is the scale of the error; the
old AAC and schedule diagnostics cannot stand.

An explicit `BAMAX 53` m²/ha sensitivity brings IDFxm H/L/M to
49.2/45.2/51.7 m²/ha and 621.6/532.2/635.3 m³/ha at 200 years. It leaves the
IDFdk3 AUs essentially unchanged. This is the current plausibility cap, not a
calibrated parameter.

## Units

`BAMAX` is **m²/ha** in the BC variant, despite the generic FVS keyword guide
saying ft²/ac. `BAMAX 53` means 53 m²/ha.

## What remains

- Full KC and Gavin/GL FVS reruns.
- Site-series assignment per plot/AU, not a global `01`.
- IDFxm capacity decision: FVS defaults 25–40 m²/ha, PSP p99 52.9.
- Mortality calibration on the corrected BEC.
- Mark old FVS-derived curves and AAC diagnostics superseded.

## Tests

`tests/test_fvs_bec.py`: 14 tests covering IDFdk3, IDFxm, SBS, site-series
phases, invalid region/zone/subzone/variant, and rejection of `CHS131`.

Dashboard: green at the code commit.
