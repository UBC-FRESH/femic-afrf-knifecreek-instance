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

## Horizon and curve contract

WS4 clamps yield curves to their endpoint values before the first point and
after the last point. The 200-year run is therefore defined by the WS4 curve
contract, not by a separate post-extend step. The current source product curves
end at 30 years; a real 200-year rebuild should run FVS for the full horizon
rather than relying on the flat clamp.

## Final growing stock

The final-period target is:

- account: `feature.yield.managed.total`;
- period: 20;
- minimum: 2,306,547.786 (90% of the initial 2,562,830.873);
- weight: 1000.

This is the only growing-stock target. It is a structural floor, not a
calibrated inventory objective.

## Tested floor

Using the GWM moderate selection schedule as the starting schedule:

- 20,000 m3/period: met in all 20 periods;
- 27,000 m3/period: met in all 20 periods after a 50,000-iteration search;
- the ±5% even-flow band is still not converged;
- the target file uses 27,000 m3/period as a tested structural floor.

The 50,000-iteration result is not a proof of a global maximum and not a
calibrated AAC. The remaining failure is the shape band, not the floor.

## Files

- `ws4/targets_kc_evenflow.yaml`
- `runbooks/run_kc_evenflow.sh`

## Caveats

- The current source product curves end at 30 years; the 200-year run uses the documented flat clamp.
- The even-flow band needs a longer search or a different reference-period setup.
- The scenario uses the structural KC model; there is no KC calibration.
