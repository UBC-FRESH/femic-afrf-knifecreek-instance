FVS-BC configuration
====================

`regimes.yaml` holds the selection-regime templates. They are not reviewed
policy. The residual basal-area values are placeholders, and the keyword
sequence is not yet validated against a real run.

The growth engine is pinned in `../toolchain.yaml`:

- `fresh-fvsbc` at commit `ca33d0e26a079a72add5108f1b182b798b0c4e3e`;
- package version 0.11.0.

A runnable regime needs:

- a reviewed keyword sequence, including the selection keyword and its fields;
- a residual basal-area or removal target;
- a cutting cycle and entry window;
- a species preference and diameter limit, if any;
- a stem-list source; and
- a state key for the residual condition.

The wrapper's keyword and output contracts are at
<https://ubc-fresh.github.io/fresh-fvsbc/>. Read the keyword page before adding
a new keyword: the wrapper validates the name, and the parameter fields are
ten columns wide.
