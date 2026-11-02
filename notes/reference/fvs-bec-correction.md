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

`runbooks/build_kc_au_yield_200y.py` now:

- uses the plot's BEC label and TSA region;
- takes an explicit `--site-series` (diagnostic default `01`);
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
