# KC even-flow harvest-volume scenario

Status: structural scenario parametrization. Not calibrated growth and not a
legal-compliance test.

## Structure

This mirrors the TSA 27 even-flow pattern:

- a flow target on `product.yield.managed.total`;
- an even-flow band of +/-5% against period 1;
- a matching level target on `feature.yield.managed.total`;
- a paired area flow/level check on `product.area.managed.total` and
  `feature.area.managed.total`;
- one harvest floor target per period.

The flow target is the shape. The floor targets are the level. Neither replaces
the other.

## Horizon limit

The KC product curves cover 30 years, so the runnable horizon is three
10-year periods. TSA 27 uses 200 years; that pattern cannot be copied to KC
until the product curves are extended.

## Tested level

Using the GWM moderate selection schedule as the starting schedule:

- 150,000 m3/period: met;
- 185,000 m3/period: met;
- 190,000 m3/period: met in all three periods;
- 195,000 m3/period: below in all three periods.

The current target file uses 190,000 m3/period as a tested structural floor.
This is not a proof of the global maximum and not a calibrated AAC.

## Files

- `ws4/targets_kc_evenflow.yaml`
- `runbooks/run_kc_evenflow.sh`

## Caveats

- Product curves are 30-year point estimates.
- Feature curves are 100-year space-for-time curves.
- The scenario uses the structural KC model; there is no KC calibration.
- The level accounts are reported; they are not a legal habitat test.
