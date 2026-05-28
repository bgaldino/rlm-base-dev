# PricingRecipeTableMappings Payloads

JSON payloads consumed by `configure_core_pricing_recipe_table_mappings` and
`configure_pricing_recipe_table_mappings`.

These files are not SFDMU datasets. They are used by
`tasks.rlm_configure_pricing_recipe_table_mappings.ConfigurePricingRecipeTableMappings`,
which uses the Salesforce Tooling API to ensure
`PricingRecipeTableMapping` rows exist (or are corrected) without deploying
pricing recipe metadata.

## Files

- `core_ngp_default.json`
  - Core prerequisite mapping for `NGPDefaultRecipe`:
    `RLM_CostBookEntries` as `ListPrice`.
  - Applied by `configure_core_pricing_recipe_table_mappings`.
  - Wired in `prepare_expression_sets` before `deploy_expression_sets`.
- `prm_ngp_default.json`
  - PRM feature mappings for `NGPDefaultRecipe`:
    - `RLM_CostBookEntries` as `ListPrice` (shared/idempotent coverage)
    - `RLM_Channel_Program_Level_Partner` as `PriceAdjustmentMatrix`
  - Applied by `configure_pricing_recipe_table_mappings`.
  - Wired in `deploy_post_prm_pricing` before
    `deploy_post_prm_pricing_expression_sets`.

## JSON Contract

Each file must be a JSON array of mapping objects:

```json
[
  {
    "pricingRecipeDeveloperName": "NGPDefaultRecipe",
    "decisionTableDeveloperName": "RLM_CostBookEntries",
    "pricingComponentType": "ListPrice"
  }
]
```

Required fields per row:

- `pricingRecipeDeveloperName`
- `decisionTableDeveloperName`
- `pricingComponentType`

Rows are matched by `(PricingRecipeId, LookupTableId)`. The task behavior is:

- create when mapping row does not exist
- update when `PricingComponentType` differs
- no-op when row already matches

## Task Usage

Run the core prerequisite task:

```bash
cci task run configure_core_pricing_recipe_table_mappings --org <cci_alias>
```

Run the PRM feature task:

```bash
cci task run configure_pricing_recipe_table_mappings --org <cci_alias>
```

Diagnostic mode to list mappings (no writes):

```bash
cci task run configure_pricing_recipe_table_mappings --org <cci_alias> -o operation list
```

Dry run:

```bash
cci task run configure_pricing_recipe_table_mappings --org <cci_alias> -o dry_run true
```

## Verification

Confirm expected mappings via Tooling API:

```bash
sf data query --use-tooling-api -q "SELECT Id, PricingComponentType, PricingRecipe.DeveloperName, LookupTable.DeveloperName FROM PricingRecipeTableMapping WHERE PricingRecipe.DeveloperName = 'NGPDefaultRecipe'" --target-org rlm-base__<cci_alias>
```

Expected baseline:

- `NGPDefaultRecipe` + `RLM_CostBookEntries` -> `ListPrice`

Expected with PRM pricing enabled:

- `NGPDefaultRecipe` + `RLM_CostBookEntries` -> `ListPrice`
- `NGPDefaultRecipe` + `RLM_Channel_Program_Level_Partner` ->
  `PriceAdjustmentMatrix`

## Failure Behavior and Guardrails

- Default `skip_missing_tables: false` fails fast when a required
  `DecisionTable` is missing.
- Use `skip_missing_tables: true` only for explicit diagnostics/manual runs.
- Keep payloads additive and idempotent; avoid replacing core mappings when
  introducing feature-specific prerequisites.
