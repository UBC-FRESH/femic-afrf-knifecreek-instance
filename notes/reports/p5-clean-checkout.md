# P5 clean-checkout verification

Status: release-candidate verification. The FVS-BC pilot is blocked by a
missing runtime in this environment; it is not claimed to have run.

## Checkout

- Repository: `UBC-FRESH/femic-afrf-knifecreek-instance`
- Branch: `feature/p5-release`
- Commit: `41b2ada1101faa40a423250bde981e0bf814d956`
- Method: shallow clone into `/tmp/opencode/kc-clean`

## Results

| Check | Result |
| --- | --- |
| `python scripts/dashboard.py` | green: lint, format, types, tests, validator, docs |
| `ws4 build --xml data/kc_ws4_recipe/forestmodel.xml --fragments data/kc_ws4_recipe/fragments.csv` | built |
| `ws4 validate --dataset /tmp/opencode/kc-clean-out` | valid |
| `python -c "import fresh_fvsbc"` | `ModuleNotFoundError` |

The clean build produced the expected tables:

| Table | Rows |
| --- | ---: |
| fragments | 160 |
| blocks | 160 |
| tracks | 19 |
| treatments | 19 |
| curves | 6,661 |
| features | 114 |
| products | 38 |
| accounts | 8 |

## FVS-BC status

`fresh_fvsbc` is not installed in this environment. The FVS-BC pilot cannot be
reproduced from this checkout without building or installing the wrapper and
its FVS runtime. This is a release prerequisite and a documented known gap, not
a successful pilot claim.

The ws4 compile, validation and dashboard checks do not depend on the FVS-BC
package; they use the committed recipe, fragments and structural curves.

## Evidence

- `ws4/evidence/kc_v1/p5_clean_checkout.log`
