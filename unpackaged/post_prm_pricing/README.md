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
- Gate when invoked from `prepare_prm`: `project_config.project__custom__prm`
  and `project_config.project__custom__prm_pricing`
- Task group: `deploy_post_prm_pricing_*` in `cumulusci.yml`

## Context Mapping Note

PRM pricing expects
`RLM_Transient_Distributor_Discount_Percent__c` to exist as a transient
`SalesTransactionItem` context attribute and to be mapped to the
`QuoteLineItem` node without source-field hydration. That mapping lives in
`datasets/context_plans/PrmPricing/contexts/prm_pricing.json` and is applied by
`apply_context_prm_pricing`.

Baseline PRM deployment remains in `unpackaged/post_prm` and continues to run
through `prepare_prm` using legacy/main-compatible gating and sequencing.

## Pricing Recipe Table Mappings

Pricing procedure lookup tables require `PricingRecipeTableMapping` records in
the target org. These records are Tooling API data, not deployable metadata.

Shared/default pricing owns the core cost-book mapping:

- Payload: `datasets/tooling/PricingRecipeTableMappings/core_ngp_default.json`
- Task: `configure_core_pricing_recipe_table_mappings`
- Flow: `prepare_expression_sets`
- Mapping: `NGPDefaultRecipe` + `RLM_CostBookEntries` + `ListPrice`

PRM pricing owns the PRM channel-program lookup mapping:

- Payload: `datasets/tooling/PricingRecipeTableMappings/prm_ngp_default.json`
- Task: `configure_pricing_recipe_table_mappings`
- Flow: `deploy_post_prm_pricing`
- Mapping: `NGPDefaultRecipe` + `RLM_Channel_Program_Level_Partner` +
  `PriceAdjustmentMatrix`

The PRM payload also includes the shared `RLM_CostBookEntries` mapping
idempotently. In a full org-prep run it is already created by
`prepare_expression_sets`; keeping it in the PRM payload lets direct
`prepare_prm_pricing` runs repair the prerequisite before deploying the PRM
pricing procedure.

## Shared Core Dependencies

`RLM_PRM_DISTI_Pricing_Procedure` reuses shared cost-book pricing assets:

- `RLM_CostBookEntries` decision table from `unpackaged/pre/5_decisiontables/`
- `NGPDefaultRecipe` mapping for `RLM_CostBookEntries`
- deploy-time lookup ID transform `__LOOKUPID_RLM_COSTBOOKENTRIES__`

PRM-specific ownership remains limited to PRM fields, context extensions,
`RLM_Channel_Program_Level_Partner`, `RLM_PRM_DISTI_Pricing_Procedure`, PRM
flows, and `RLM_PRM_Pricing`.
