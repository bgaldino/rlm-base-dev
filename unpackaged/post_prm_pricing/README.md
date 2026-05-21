# PRM Pricing Metadata (`post_prm_pricing`)

This bundle contains PRM pricing metadata deployed through the
`prm_pricing` feature path (`prepare_prm_pricing`). Baseline PRM site and
partner-channel metadata remains in `unpackaged/post_prm/`.

## Deployment Path

- Flow: `prepare_prm_pricing`
- Gate from `prepare_prm`: `project_config.project__custom__prm` and
  `project_config.project__custom__prm_pricing`
- Metadata deploy task group: `deploy_post_prm_pricing_*`
- Default branch state: `prm_pricing=true`

## Component Inventory

### Custom Fields

| Object | Fields |
| ------ | ------ |
| `Account` | `RLM_Primary_Distributor__c`, `RLM_Primary_Reseller__c` |
| `ChannelProgramLevel` | `RLM_Adjustment_Type__c`, `RLM_Adjustment_Value__c`, `RLM_Discount_Rate__c` |
| `ChannelProgramMember` | `RLM_Adjustment_Type__c`, `RLM_Adjustment_Value__c`, `RLM_Discount_Rate__c` |
| `Quote` | `RLM_Distributor_Account__c` |
| `QuoteLineItem` | `RLM_Distributor_Discount_Percent__c`, `RLM_Distributor_Unit_Price__c`, `RLM_Partner_Net_Total_Price__c` |

The four Channel Program fields that also exist in `post_prm` are kept
metadata-identical so `post_prm_pricing` redeploys them as a no-op when the
pricing feature is active.

### Pricing and Automation Metadata

- Decision table: `RLM_Channel_Program_Level_Partner`
- Pricing procedure: `RLM_PRM_DISTI_Pricing_Procedure`
- Flows: `RLM_Create_New_Quote`, `RLM_Update_Channel_Program_Member`
- Permission set: `RLM_PRM_Pricing`

`RLM_PRM_Pricing` grants read/edit access to the 12 fields above.

## Context Mapping

PRM pricing expects these context additions on `RLM_SalesTransactionContext`:

- `SalesTransaction`: `RLM_Distributor_Account__c`, `PartnerAccount__c`
- `SalesTransactionItem`: `RLM_Distributor_Unit_Price__c`,
  `RLM_Distributor_Discount_Percent__c`,
  `RLM_Partner_Net_Total_Price__c`
- Transient `SalesTransactionItem` attribute:
  `RLM_Transient_Distributor_Discount_Percent__c`

The transient attribute is mapped to the `QuoteLineItem` node without
source-field hydration. The plan lives in
`datasets/context_plans/PrmPricing/contexts/prm_pricing.json` and is applied by
`apply_context_prm_pricing`.

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

## Data and Procedure Plan Overlays

`prepare_prm_pricing` also loads feature-scoped data after metadata deployment:

- `datasets/sfdmu/qb/en-US/qb-prm-pricing/` seeds PRM pricing partner data and
  Account self-lookups when `qb=true`.
- `datasets/sfdmu/procedure-plans-prm/` adds the PRM conditional branch to
  `RLM_Quote_Pricing_Procedure_Plan` when `procedureplans=true`.

The procedure-plan overlay runs through a guarded
deactivate/load/verify/reactivate sequence so partial imports fail before the
plan is reactivated.

## UX Sources

PRM pricing UX is assembled from `templates/` and generated into
`unpackaged/post_ux/` by `assemble_and_deploy_ux`; do not edit generated
`post_ux` files directly.

Source templates:

- `templates/applications/patches/prm_pricing/RLM_Revenue_Cloud.patch.xml`
- `templates/flexipages/patches/prm_pricing/RLM_Account_Record_Page.yml`
- `templates/flexipages/patches/prm_pricing/RLM_Quote_Record_Page.yml`
- `templates/flexipages/standalone/prm_pricing/RLM_Channel_Program_Record_Page.flexipage-meta.xml`
- `templates/flexipages/standalone/prm_pricing/RLM_Channel_Program_Level_Record_Page.flexipage-meta.xml`

Generated outputs include the PRM pricing application patch, Account and Quote
record page changes, and standalone Channel Program / Channel Program Level
record pages under `unpackaged/post_ux/`.

## Shared Core Dependencies

`RLM_PRM_DISTI_Pricing_Procedure` reuses shared cost-book pricing assets:

- `RLM_CostBookEntries` decision table from `unpackaged/pre/5_decisiontables/`
- `NGPDefaultRecipe` mapping for `RLM_CostBookEntries`
- deploy-time lookup ID transform `__LOOKUPID_RLM_COSTBOOKENTRIES__`

PRM-specific ownership remains limited to PRM fields, context extensions,
`RLM_Channel_Program_Level_Partner`, `RLM_PRM_DISTI_Pricing_Procedure`, PRM
flows, `RLM_PRM_Pricing`, feature-scoped data overlays, and PRM pricing UX.
