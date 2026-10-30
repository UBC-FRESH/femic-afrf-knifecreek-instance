# KC even-flow harvest-volume scenario

Status: structural scenario parametrization. Not calibrated growth and not a
legal-compliance test.

## Structure

- 20 x 10-year periods (200 years).
- Flow target on `product.yield.managed.total`.
- Even-flow band of +/-5% against period 1.
- One harvest-volume floor target per period.
- No growing-stock or other level targets yet.

The flow target is the shape. The floor targets are the level.

## Horizon and curve limit

The KC product curves end at 30 years. The 200-year run uses the simulator's
terminal-value extension; it is not a calibrated 200-year yield. The feature
curves are 100-year space-for-time curves.

## Tested floor

Using the GWM moderate selection schedule as the starting schedule:

- 25,000 m3/period: met in all periods;
- 27,000 m3/period: met in all periods;
- the even-flow +/-5% band did not converge in a 50,000-iteration probe.

The target file uses 27,000 m3/period as a provisional structural floor. It is
not a proven maximum and not a calibrated AAC.

## Files

- `ws4/targets_kc_evenflow.yaml`
- `runbooks/run_kc_evenflow.sh`

## Caveats

- No 200-year product curve exists yet.
- The even-flow band needs a longer search or a different reference-period setup.
- The scenario uses the structural KC model; there is no KC calibration.
