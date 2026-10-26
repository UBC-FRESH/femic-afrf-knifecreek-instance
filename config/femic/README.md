FEMIC lane
==========

FEMIC is used for the data-prep lane:

- boundary ingest and validation;
- VRI and BEC joins;
- strata and analysis-unit construction;
- site index and species attributes; and
- disturbance overlays.

FEMIC's VDYP/TIPSY growth lane is **not** the primary growth engine for Knife
Creek. VDYP and TIPSY are stand-level models and cannot carry a residual
diameter distribution through repeated selection entries. Use them only for a
documented even-aged sensitivity or a volume cross-check.

The run profile in this directory is a template. It is not runnable until the
boundary and inventory exist. The eventual model-build lane is:

1. FEMIC data prep;
2. nemora stem populations;
3. fresh-fvsbc selection-cut runs;
4. state-transition library; and
5. ws4 dataset compile.
