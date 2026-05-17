# PRM Pricing Metadata (`post_prm_pricing`)

This bundle contains branch-scoped PRM pricing metadata deployed only through
the `prm_pricing` feature path (`prepare_prm_pricing` flow).

## Deployed Components

- `objects/`
- `decisionTables/`
- `expressionSetDefinition/`
- `flows/`
- `permissionsets/` (`RLM_PRM_Pricing` only)

## Deployment Path

- Flow: `prepare_prm_pricing`
- Gate: `project_config.project__custom__prm_pricing`
- Task group: `deploy_post_prm_core_*` in `cumulusci.yml`

Baseline PRM deployment remains in `unpackaged/post_prm` and continues to run
through `prepare_prm` using legacy/main-compatible gating and sequencing.
