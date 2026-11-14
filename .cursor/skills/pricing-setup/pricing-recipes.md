# Pricing Recipes

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. Release 264 / API v68.0. Sources:
> `ind.pricing_pricing_recipes.htm`, `ind.pricing_create_new_pricing_recipe.htm`,
> `ind.pricing_view_pricing_recipes.htm`, `ind.pricing_sync_decision_tables_in_a_pricing_recipe.htm`,
> `ind.pricing_automate_pricing_data_sync.htm`; repo: `../pricing-wiring/SKILL.md` section A,
> `datasets/tooling/PricingRecipeTableMappings/README.md`. Not live-verified.

A pricing recipe groups the decision tables a pricing procedure may read, and is the single place that
says how those tables are used. The org has one active recipe, selected in Salesforce Pricing Setup;
Builder element lookups list only tables mapped to the **default recipe of the procedure's subtype**. [Help]

## When you need it

- A procedure element (List Price, Price Adjustment Matrix, Price Revision, ...) cannot find or reject a decision table.
- You added a custom decision table and want it selectable in the Builder.
- You run more than one cloud (Revenue Cloud, Life Sciences Cloud) and need a default recipe per subtype.
- You need to know which recipe is active, or to re-sync a recipe's tables.

## Set it up

Permission for all steps: Salesforce Pricing Design Time. [Help]

**View / select the active recipe**
1. Setup > Quick Find > `Salesforce Pricing` > Salesforce Pricing Setup.
2. In **Select a Pricing Recipe**, choose the recipe. Only one is active at a time. [Help: `ind.pricing_view_pricing_recipes.htm`]
3. Activating Salesforce Pricing creates the predefined recipe `NGPDefaultRecipe`, mapped to all predefined decision tables. [Help]

**Create a recipe** (when the predefined one is not enough; decision tables must already exist) [Help: `ind.pricing_create_new_pricing_recipe.htm`]
1. Setup > Quick Find > `Pricing Recipes`.
2. New: enter a name and pick a **Subtype**. The list shows only clouds matching your active licenses. Each subtype may have several recipes, one of them the default (changeable).
3. Save, open the recipe, go to the **Price Adjustment Matrix** tab, click **Modify**, select the decision tables to map, save.
4. New procedures with usage type Pricing then offer the predefined tables plus the ones you mapped.

**Sync a recipe's decision tables**: Setup > Pricing Recipes > row action **Sync**. [Help: `ind.pricing_sync_decision_tables_in_a_pricing_recipe.htm`]

## Fields and rules

| UI label | API name | Rules |
|---|---|---|
| Pricing Recipe | `PricingRecipe` (Tooling API) [Repo] | One active per org. `NGPDefaultRecipe` is the shipped developer name [Help, Repo]. Not in the offline ERD; confirm by describe. |
| Subtype | not confirmed | Settable on create and clone, not on edit. Procedures created before Winter '27 default to the Revenue Cloud subtype. [Help] |
| Recipe-table mapping | `PricingRecipeTableMapping` (Tooling API) [Repo] | Links a recipe to a `DecisionTable` with a `PricingComponentType` (for example `ListPrice`) [Repo: `../pricing-wiring/SKILL.md` section A]. UI path is the Price Adjustment Matrix tab. |

Element lookups show only tables linked to the **default recipe of the procedure's subtype**. [Help]

## How pricing uses it

- The Builder's lookup pickers (List Price, Price Adjustment Matrix, Price Revision, ...) list mapped tables only. Element fields: [`../pricing-procedures/elements/list-price.md`](../pricing-procedures/elements/list-price.md), [`../pricing-procedures/elements/price-adjustment-matrix.md`](../pricing-procedures/elements/price-adjustment-matrix.md).
- Help adds that a recipe supports Dynamic Output Mapping: map a table, then define custom outputs per element, so pricing is data-model independent. [Help]
- Unmapped table: a List Price step can fail with `Ensure that the lookup table in the ListPrice step is valid and try again.` even when the table exists and is Active. [Repo skill, see List Price element]
- Which procedure runs and how to simulate/activate it: [`../pricing-procedures/operations-and-troubleshooting.md`](../pricing-procedures/operations-and-troubleshooting.md).

## Data and automation

- Repo build of recipe-table mappings (tasks, JSON payloads, flow order, idempotency): [`../pricing-wiring/SKILL.md`](../pricing-wiring/SKILL.md) section A and [`datasets/tooling/PricingRecipeTableMappings/README.md`](../../../datasets/tooling/PricingRecipeTableMappings/README.md). Not repeated here.
- Refresh mechanics, freshness and ordering after data changes: [`../decision-tables/SKILL.md`](../decision-tables/SKILL.md).
- Three Help refresh paths [Help]: recipe **Sync** action; **Sync Pricing Data** button in Salesforce Pricing Setup; a schedule-triggered Flow calling the **Refresh Decision Table** action (one action per table).
- Scheduled flow cautions [Help: `ind.pricing_automate_pricing_data_sync.htm`]: run off-peak;
  deactivate during bulk loads and run a manual sync after; add a fault path or enable flow error
  emails (failures are silent otherwise, e.g. deactivated table or hourly limit); confirm via
  Decision Tables > Last Refreshed. Permissions for building the flow: Manage Flow, Salesforce
  Pricing Design Time, and Assetize Order for a complete sync. The action has its own gate:
  [decision-tables](../decision-tables/SKILL.md) (the refresh flow action is admin-only).

## Verify

```bash
sf data query --use-tooling-api --target-org <sf_alias> -q "SELECT Id, DeveloperName FROM PricingRecipe"
sf data query --use-tooling-api --target-org <sf_alias> -q "SELECT PricingComponentType, LookupTableId FROM PricingRecipeTableMapping WHERE PricingRecipeId = '<id>'"
```
(Object and field names are taken from the repo's validation playbook; describe first if a query errors.) In the UI: Salesforce Pricing Setup shows the selected recipe; the Builder lookup picker lists the mapped tables; Decision Tables shows Last Refreshed.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Custom table missing from Builder picker | Not mapped to the default recipe of the procedure's subtype | Add on the recipe's Price Adjustment Matrix tab |
| List Price "lookup table ... is valid" error | Mapping row absent or table inactive | Map and activate the table; in this repo see pricing-wiring section A |
| Recipe exists but picker still empty | Recipe is not the default for the subtype, or procedure has another subtype | Make it the subtype default; check the procedure's subtype |
| Prices plausible but stale | Table not synced after data change | Sync the recipe or refresh the table |
| Cannot change subtype | Only possible when cloning | Clone with the new subtype |

## Open questions

- Help does not state how to set the subtype default (the "default recipe that you can change" control) or its API field name.
- Help's Price Adjustment Matrix tab holds all mapped tables, not only matrices; the label looks historical (inferred).
- Help does not say whether Sync activates tables. Core: it refreshes only active mapped tables and never activates one ([scope](import-export-and-bulk-data.md#sync-pricing-data)).
