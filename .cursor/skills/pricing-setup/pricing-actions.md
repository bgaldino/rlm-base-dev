# Pricing Actions

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. Release 264 / API v68.0. Sources:
> `ind.pricing_pricing_action_parameters.htm`, `ind.pricing_get_ready_to_create_pricing_actions.htm`,
> `ind.pricing_standard_pricing_actions.htm`, `ind.pricing_configure_pricing_action_parameters_for_standards_objects.htm`,
> `ind.pricing_configure_pricing_action_button_using_LWC.htm`, `ind.pricing_add_calculate_price_button.htm`,
> `ind.pricing_calculate_price_of_object.htm`, `ind.pricing_create_constant_resource.htm`; dev guide
> `meta_pricingactionparameters.htm`, `sforce_api_objects_pricingactionparameters.htm`;
> `unpackaged/post_quantumbit/pricingActionParameters/`. Not live-verified.

A pricing action is a Calculate Price button on a record page. Each action binds an object to a
context definition, a context mapping and a pricing procedure, so pricing results are stored on
the Salesforce object itself. [Help] It is a record-page pricing tool, not the quote/order pricing
path (see Limits).

## When you need it

- Price Opportunity, Case, Contract, Quote or Order records from their own page without a transaction flow.
- Test a procedure against real records with a button instead of Simulate.

## Set it up

Prerequisites ("get ready") [Help `ind.pricing_get_ready_to_create_pricing_actions.htm`]:

1. An **extended** context definition with nodes, attributes, tags and a mapping to the target object.
   The base `SalesTransactionContext__stdctx` does not work directly; extend it. See
   [context-service](../context-service/SKILL.md).
2. A pricing procedure on that context definition. See
   [procedure-anatomy-and-ordering.md](../pricing-procedures/procedure-anatomy-and-ordering.md).
3. Pricing action parameters for the object (standard button only).

### Standard button (Quote, Order, Contract, Case, Opportunity)

1. Setup > Quick Find "Pricing Action Parameters" > New (permission: Salesforce Pricing Admin).
2. Pick the object, the extended context definition, a context mapping matching that object, and the pricing procedure.
3. Set Effective From (date and time); Effective To is optional. Save.
4. Setup > Object Manager > object > Page Layouts > layout > Buttons palette; drag **Calculate Price**
   into the Salesforce Mobile and Lightning Experience Actions section (permission: Customize Application). Save.
5. Users with Salesforce Pricing Admin or Salesforce Pricing Run Time User open a record and click Calculate Price.

### Custom button (Lightning component)

1. On any record page: Edit Page; drag the **Pricing Calculation** component onto the canvas.
2. Name the action; choose context definition, context mapping and pricing procedure on the component (no parameter record). Save.

Help is inconsistent on supported objects: the layout steps list five objects, the run article also
lists Sales Agreement and Work Order. The dev guide's `objectName` values include all seven. Check
the layout in the org. [Help, Dev guide]

## Fields and rules

Object `PricingActionParameters` (metadata type and setup entity, API 60.0+) [Dev guide:
`meta_pricingactionparameters.htm`, `sforce_api_objects_pricingactionparameters.htm`]. Core exposes
it in the Tooling family, so query it with the Tooling API. Create, edit and delete need Pricing
Design Time User, Pricing Manager or Pricing Admin. [Core]

| UI label | API name | Rules |
|---|---|---|
| Object | `objectName` | `Case`, `Contract`, `Opportunity`, `Order`, `Quote`, `SalesAgreement`, `WorkOrder` [Dev guide]. Help's setup list omits the last two |
| Context definition | `contextDefinition` | Required. Must be extended, with nodes, attributes, tags [Help] |
| Context mapping | `contextMapping` | Required. Must match the target object type or pricing errors [Help] |
| Pricing procedure | `pricingProcedure` | Text (name or id), not a lookup; optional. Blank: see below [Core] |
| Effective From / To | `effectiveFrom` / `effectiveTo` | From required, To optional. Two parameters for the same object may not overlap; save rejects it [Core] |
| Name | `developerName`, `masterLabel` | Required on deploy, but save overwrites both with `<Object>_<timestamp>` [Core] |

[Repo] `unpackaged/post_quantumbit/pricingActionParameters/` holds Quote and Order parameters
(`RLM_SalesTransactionContext`, `QuoteEntitiesMapping` / `OrderEntitiesMapping`,
`RLM_DefaultPricingProcedure`), but `.forceignore` excludes that folder, so a source deploy skips them.

## How pricing uses it

The click runs the chosen procedure over the context hydrated through the mapping; outputs are
written back through the same mapping. The procedure for quotes and orders is a different setting
(Revenue Settings), see [operations-and-troubleshooting.md](../pricing-procedures/operations-and-troubleshooting.md#1-which-procedure-does-the-org-run).
The standard button needs exactly one parameter for the object whose window covers now: zero or
two-plus matches show a "record missing" error and pricing never runs. With one match and a blank
procedure, the server uses the active Revenue Cloud pricing recipe's Default Pricing Procedure, or
fails with `PRICING_PROCEDURE_NOT_FOUND` if none is set. [Core] The custom component uses its own
property.

Limits [Help]: the button only prices Salesforce objects, has no custom data hydration, and does
not replace Transaction Management pricing of bundles and derived products (those need a
custom-built button acting on persisted data).

## Constant resources

Constants hold fixed values for variables that lack context tags (for example the resolution
strategy text for output resolution). [Help `ind.pricing_create_constant_resource.htm`]

1. Open the procedure in the builder; click the resource icon > Resource Manager > Add Resource.
2. Set type (Constant is the only supported type), name, data type, default value; save.
3. Use unique names; avoid reserved words such as Currency, Number, Text.

Used in [lowest price](scenarios/lowest-price-across-price-books.md) and
[sequential discounts](scenarios/sequential-discounts.md); element side in
[list-price.md](../pricing-procedures/elements/list-price.md).

## Data and automation

Parameters are records; bulk paths in [import-export-and-bulk-data.md](import-export-and-bulk-data.md).
Query them with `sf data query --use-tooling-api -q "SELECT DeveloperName, ObjectName,
PricingProcedure, EffectiveFrom, EffectiveTo FROM PricingActionParameters"` (fields per core;
not yet run live). An active parameter blocks deactivating its context definition
([`../context-service/authoring-and-lifecycle.md`](../context-service/authoring-and-lifecycle.md)). [Repo]

## Verify

1. Open a record, click Calculate Price; confirm no error.
2. Confirm which procedure ran via the waterfall/logs
   ([runtime-and-observability.md](../pricing-procedures/runtime-and-observability.md)).
3. To prove the binding, point the parameter at a procedure with a distinguishing output (for
   example a constant-assigned value) and confirm it appears after the click (inferred technique).
4. Confirm the parameter is inside its effective window and the layout carries the button.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| No Calculate Price button | Not on page layout | Add via Page Layouts > Buttons |
| Button errors or nothing computed | No effective parameter for the object, or mapping mismatch | Check Effective From/To; select the mapping for that object |
| "Record missing" error with a parameter present | Outside its window, or not exactly one effective row | Fix the dates so exactly one row covers now [Core] |
| `PRICING_PROCEDURE_NOT_FOUND` | Blank procedure and no Default Pricing Procedure on the active recipe | Set the parameter's procedure [Core] |
| Base context not usable | Base context cannot be used directly | Extend it first |
| Bundle or derived prices wrong | Standard button lacks custom hydration | Use transaction pricing or a custom button |
| Context cannot be deactivated | A parameter references it | Unlink the parameter first |

## Open questions

- Whether the Help setup UI offers Sales Agreement and Work Order as the dev guide's `objectName` values do.
- The Tooling query above has not been run on a live org.
