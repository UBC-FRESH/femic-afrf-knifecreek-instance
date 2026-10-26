# Knife Creek planning

Active planning surfaces for the Knife Creek instance:

- `knife_creek_bootstrap.md` — phase-level work breakdown, data dependencies,
  risks, and decisions.
- `fvsbc-state-transition-design.md` — the technical design for turning
  FVS-BC selection-cut runs into a ws4 state-transition dataset.

Implementation surfaces that follow these plans:

- `config/instance.yaml` — stable block identity.
- `config/toolchain.yaml` — pinned engine versions.
- `config/data_requirements.yaml` — source checklist.
- `config/fvsbc/regimes.yaml` — selection-regime templates.
- `ws4/state_transition_contract.md` — ws4 table contract.
- `notes/adr/0002-fvsbc-growth-engine.md` — the growth-engine decision.
