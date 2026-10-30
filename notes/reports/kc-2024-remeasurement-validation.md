# KC 2024 Marshall remeasurement validation

Status: **temporal holdout diagnostic**. Not an independent-site validation,
not a production-growth calibration and not a legal-compliance claim.

## Data

Source: `inst88-11_2024meas_clean.xlsx`, 24 Knife Creek Marshall plots,
install 88.11.

- 5,637 tree records: 3,515 residual, 1,872 dead, 250 ingrowth.
- Plots 1–2 end in 2024; the other 22 plots end in 2025.
- 11–12 year interval from the 2013 measurement.
- Interior trees only; buffer trees excluded.
- Raw tree records remain private. Derived summaries are in
  `data/psp/kc_afrf_psp_*_2024*`.

Observed 2013 → 2024/2025:

| Metric | 2013 | 2024/2025 |
| --- | ---: | ---: |
| Mean BA (m²/ha) | 35.38 | 39.34 |
| Mean TPH | 2,291 | 1,938 |
| Mean QMD (cm) | 14.98 | 16.76 |
| Mean annual mortality | — | 1.57% |

The 2013 start values match the existing 1993–2013 transition table. The new
interval adds one temporal observation per plot.

## FVS backtest

The v1 calibration was fitted to 2013. It was not refitted for this test.
Starting from the 2013 tree list, FVS-BC ran one no-cut interval to each plot's
2024/2025 measurement year.

| Parameter set | BA bias (m²/ha) | BA MAE | QMD bias (cm) | QMD MAE | TPH bias | TPH MAE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Uncalibrated | +0.83 | 1.85 | −0.08 | 0.86 | +201 | 341 |
| v1 calibrated | +1.33 | 1.80 | +0.78 | 1.10 | +24 | 270 |

Species-group BA bias with v1 calibration:

| Group | Observed BA total | Predicted BA total | Mean BA bias |
| --- | ---: | ---: | ---: |
| FD | 849.8 | 889.0 | +1.63 |
| SE | 68.3 | 66.9 | −0.06 |
| PL | 8.8 | 3.8 | −0.20 |
| HW | 17.3 | 26.9 | +0.40 |

## Interpretation

- The v1 calibration transfers temporally for total TPH: bias falls from +201
  to +24, and MAE falls from 341 to 270.
- BA bias increases slightly, from +0.83 to +1.33 m²/ha; BA MAE is essentially
  unchanged.
- QMD bias moves from −0.08 to +0.78 cm; the uncalibrated run is closer on QMD.
- Douglas-fir BA is overpredicted by about 1.6 m²/ha on average. The small
  lodgepole-pine component remains underpredicted.
- The result supports using the calibration as a **sensitivity**, not as a
  production default. The test is on the same 24 plots used in fitting, so it
  is temporal, not independent-site, validation.

## Files

- `runbooks/ingest_kc_2024_remeasurement.py`
- `runbooks/fvs_validate_kc_2024.py`
- `data/psp/kc_afrf_psp_plot_summary_2024.csv`
- `data/psp/kc_afrf_psp_transitions_2024.csv`
- `data/psp/kc_afrf_psp_transitions_2024_species.csv`
- `data/psp/kc_afrf_psp_2024_metadata.json`
- `ws4/kc_psp_validation_2024/`
