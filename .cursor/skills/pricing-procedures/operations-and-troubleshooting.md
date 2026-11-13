# Pricing Procedures: Operations and Troubleshooting

> Release 264 / API v68.0. Sources: Help `ind.pricing_*` articles (cited inline);
> shipped XML and `cumulusci.yml` in this repo. Live only where a repo measurement is cited. Generic Expression Set
> lifecycle (Connect CRUD, overlays, activation mechanics) lives in
> [`../expression-sets/SKILL.md`](../expression-sets/SKILL.md); do not repeat it here.

Ongoing management of pricing procedures in a live org: which one runs, how to test and
activate, and a cross-element symptom table. How to observe a run, the execution model and the
limits are in [`runtime-and-observability.md`](runtime-and-observability.md).

## 1. Which procedure does the org run?

Salesforce uses **three separate selections**; they are not the same setting.
[Help] `ind.pricing_set_default_pricing_procedure.htm`

| Where (Setup) | Section | Used for |
|---|---|---|
| Revenue Settings | Set Up Salesforce Pricing | Pricing of quotes and orders (the one transactions run) |
| Salesforce Pricing Setup | Select a Pricing Procedure | Headless pricing calls only |
| Product Discovery Settings | Select a Pricing Procedure | List price shown in Product Discovery (see [discovery-procedures.md](./discovery-procedures.md)) |

- Never assume a name such as `RLM_DefaultPricingProcedure`. Read Revenue Settings, then list
  what exists (inferred: a customer org often runs a clone with a different name):

```bash
python scripts/expression_sets/list_expression_sets.py --target-org <sf_alias> --type PricingProcedure --versions
```

- Salesforce ships a **template, not an executable procedure**. Clone from App Launcher >
  Expression Set Templates > pick template > Save As (new procedure or new version); for quotes
  and orders clone the "Revenue Management Default Pricing Procedure" template. [Help]
- Cloning rules: you may assign a custom context definition on Save As; a cloned version
  takes only a version name and number; the clone's start date must be later than the
  context definition's Effective From. [Help]
- Permission sets: Salesforce Pricing Design Time User (create/update/delete/clone),
  Salesforce Pricing Run Time User (use). [Help] Personas, sharing and pricing actions: [`../pricing-setup/org-enablement-and-permissions.md`](../pricing-setup/org-enablement-and-permissions.md), [`../pricing-setup/pricing-actions.md`](../pricing-setup/pricing-actions.md).

## 2. Simulate and activate

[Help] `ind.pricing_simulate_activate_pricing_procedure.htm`

1. In the Builder add elements, map context tags, choose a rank, tick Include in Output, Save.
2. Simulate. Input modes: Simplified (a field per variable) or Advanced (JSON box; download,
   edit, paste back). Optionally pick a context definition and "Auto-fill line items" with a
   record id (only tags with sObject mapping and a populated field auto-fill).
3. Read the Waterfall View, then Activate.

- Procedures containing List Price or Price Adjustment Matrix elements may need
  deactivate, save, reactivate before the Simulate button appears. [Help]
- If profile access is set at element level, only those profiles see that element's
  pricing in the waterfall. [Help]
- Versions [Core, Live]: disabled versions are skipped; a version is kept only if its start/end
  dates cover the execution date (headless `effectiveDate` must be a full ISO datetime); the
  greater rank wins, whatever the version number. None kept: "Ensure that this procedure has at
  least one active version." Enabling needs a rank unused by any other enabled version, even with
  disjoint dates ("N rank is already in use"), and never null ("Enter a valid rank"), so Core's
  tie and null-rank branches are unreachable [Live, 264]. A named version number or id is returned
  if its dates match, regardless of rank [Core]. Help (discovery) [Help]: give the wanted version
  the larger rank. An enabled version cannot be edited; deactivate, edit, re-enable.
- If an active procedure plan version references the expression set, deploys are locked until
  that plan version is deactivated ([`../pricing-wiring/SKILL.md`](../pricing-wiring/SKILL.md)
  troubleshooting). [Repo]

## 3. Procedure plans (summary only)

[Help] `ind.pricing_procedure_plan_framework.htm`, `ind.pricing_use_the_procedure_plan_framework.htm`,
`ind.pricing_create_procedure_plans.htm`, `ind.pricing_procedure_plan_limits.htm`

| Concept | Meaning |
|---|---|
| Procedure Plan Definition | Ordered container of sections (pricing procedure, Apex, qualification) tied to a context definition |
| Section / Phase | A section holds one procedure or Apex class; phase = lifecycle stage (e.g. Pricing) |
| Resolution Type | Default (pick one procedure) or Rule-Based (criteria choose it) |
| Read / Save Context Mapping | Load Quote/Order into context at start; write results back at end |

- Definitions are a metadata container only; **only the Place Sales Transaction (PST) API
  orchestrates a plan**. [Help]
- Prerequisites: Context Service on; Revenue Settings > Procedure Plan Orchestration for Pricing
  enabled; the same context definition across procedures and the plan. [Help] "Exclude Default and
  Sales Transaction Type Pricing Procedures" (metadata `skipOrgSttPricing` [Dev guide]) conflicts
  across Help: the plan walkthrough enables it, the Apex-hook article says leave it disabled.
- Do not chain several pricing procedures in one plan. Limits [Help]: the waterfall shows only
  the last procedure; Derived Price sees only the Net Unit Price at the end of its own procedure;
  the Inclusive Price "skip pricing" flag does not survive into the second procedure (workaround:
  second procedure checks `InclusivePrice` and stops pricing); with parallel execution on,
  custom tag mappings are cached at activation, so deactivate and reactivate after editing a
  rule library version.
- Repo mechanics (overlays, `placement.afterSubSectionType`, plan-version deactivation) are in
  [`../pricing-wiring/SKILL.md`](../pricing-wiring/SKILL.md) section C. The repo builds the quote
  plan **inactive by default** (`procedureplans_active: false` in `cumulusci.yml`) because an
  active plan re-prices; PRM distributor pricing needs it on. Measured on 264
  (`datasets/sfdmu/procedure-plans/README.md`, Activation): active with `skipOrgSttPricing=false`
  (the repo setting), the Revenue Settings procedure re-runs and doubles a price revision (CPI 4% + 2
  on 2,400: 2,696.64, not 2,544); active with it `true`, a header discount is distributed twice (10% on
  5,240: 4,244.40, not 4,716); inactive, PST runs the Revenue Settings procedure (2,544 / 4,716, full
  waterfall). [Repo, measured]
- Why a price revision doubles: with a plan active, the plan's procedures run in section order and then the Revenue
  Settings default procedure also runs, unless "Exclude Default and Sales Transaction Type Pricing
  Procedures" is on. Two procedures then price the same lines, and a non-idempotent element (price
  revision) applies twice [Platform behaviour, traced]. Turning the setting on removes the double price
  revision; it does not remove the header-discount doubling measured above (cause not traced). The
  other route is to put every element in the plan and leave the default procedure empty of them
  [Platform behaviour, traced]. The plan's context definition must match the
  pricing context definition or no plan procedure runs [Platform behaviour, traced].

## 4. Procedure output resolution

[Help] `ind.pricing_procedure_output_resolution.htm`, `ind.pricing_create_a_procedure_output_resolution_record.htm`,
`ind.pricing_understand_your_resolution_variables.htm`

Picks one definitive price when several candidates exist (multiple price books, stacked
adjustments). Supported only on **List Price, Price Tracking, Price Adjustment Matrix** elements.

| Strategy | Effect |
|---|---|
| Minimum / Maximum | Smallest / largest candidate price |
| Stack | Apply discounts cumulatively (Price Adjustment Matrix only) |
| Sequence | Apply discounts one after another (Price Adjustment Matrix only) |

Setup: App Launcher > Price Management > Procedure Output Resolutions > New; name, element,
formula (for example `Min(List price, Priority)`; a comma list gives tiebreakers). Then enable
output resolution on the element.

| Resolution variable | Elements | Role |
|---|---|---|
| Resolution Strategy | all three | The saved resolution record |
| Use As List | all three | Input the engine resolves over (for example the price book) |
| Candidate Priority | List Price, Price Tracking | Tiebreak |
| Final Price Sequence | List Price, Price Tracking | Last tiebreaker, typically lowest price |

Map variables to context tags; a Write Back section stores the result in a tag. With resolution
on a **List Price or Price Tracking** element, every product needs a matching Price Book
decision-table row: no match is a configuration error that stops pricing that line (no zero
default). [Help] Price Adjustment Matrix resolves over its own adjustment table instead.
[inferred from Repo] Shipped XML carries the flag as
`IsOutputResolutionEnabled` (Literal `false`) on ListPrice. [Repo]

## <a name="5-observability"></a>5. Observability

Headless checks, waterfall, price logs, decision explainer, Operations Console, price history,
batch jobs and execution messages: [`runtime-and-observability.md`](runtime-and-observability.md#observability).

## <a name="6-execution"></a>6. Execution

PST order of execution, parallel execution, Apex hooks, runtime guardrails and the limits table:
[`runtime-and-observability.md`](runtime-and-observability.md#execution).

## 7. Context tag mapping

[Help] `ind.pricing_map_context_tags_in_pricing_procedures.htm`, `ind.pricing_add_context_tags_automatically_to_your_pricing_elements.htm`

Tags bind procedure variables to context definition fields; without them the procedure cannot
read input or write results. Pricing Setting (first element, common variables) and Map Line Item
(precise line/sub-line mapping) do the mapping. "Auto Populate Context Tags" (Einstein, needs
Prompt Template User) suggests mappings with a confidence score; unsupported on Discount
Distribution Service, Formula Based Pricing, Stop Pricing. Context definition authoring and
tag lifecycle: [`../context-service/SKILL.md`](../context-service/SKILL.md). An
`Invalid tag attribute name key` error ([Live, repo owner]; string not found in core labels) means a tag name being used isn't defined on the context
definition. Either the tag was never applied (`../pricing-wiring/SKILL.md` → *`Invalid tag
attribute name key`*, e.g. a context plan the build didn't run), or an attribute name was used
where the tag name is required
([`../context-service/runtime-and-persistence.md`](../context-service/runtime-and-persistence.md)
→ *Tag names are a distinct namespace from attribute names*).

## 8. Decision table sync

[Help] `ind.pricing_sync_decision_tables_in_a_pricing_recipe.htm`, `ind.pricing_automate_pricing_data_sync.htm`

Pricing reads decision-table snapshots, not the source rows. A stale table prices silently and
plausibly with no error. Refresh paths: Pricing Recipes > Sync (one recipe); Salesforce Pricing
Setup > Sync Pricing Data; a schedule-triggered Flow calling the **Refresh Decision Table**
action (one action per table, off-peak, add a fault path, pause during bulk loads, hourly
refresh limit exists; needs Manage Flow, Salesforce Pricing Design Time, Assetize Order for a
complete sync). Verify with the Last Refreshed timestamp, or `cci task run
check_decision_table_freshness --org <cci_alias>`. Authoring and refresh: [`../decision-tables/SKILL.md`](../decision-tables/SKILL.md).

## 9. Troubleshooting (cross-element)

Deploy and Connect mutation errors are not repeated here; see the *Troubleshooting Decision
Tree* in [`../pricing-wiring/SKILL.md`](../pricing-wiring/SKILL.md) and *Known errors &
conditions* in [`../../../docs/references/expression-set-connect-api-reference.md`](../../../docs/references/expression-set-connect-api-reference.md).
Element-specific errors are in the element files under [`elements/`](./elements/).

| Symptom | Likely cause | Fix |
|---|---|---|
| Plausible but wrong price, no error | Stale decision table [Help] (section 8); missing `CurrencyIsoCode` input on a lookup (multicurrency): with several currency rows for the product, resolution off gives a duplicate-value error (an error, not this symptom) and, on a List Price or Price Tracking step with resolution on, a pick by resolution strategy [Help] and candidate priority [Platform behaviour, traced, via pricing-wiring] that can be another currency's row [inferred]; a Price Adjustment Matrix with Stack or Sequence resolution and Tier Discount lookups behave differently (pricing-wiring); a lone row in another currency prices the line [inferred]; wrong procedure selected [inferred] | Check freshness (section 8); pricing-wiring wrong-currency entry; confirm procedure in Revenue Settings (section 1) |
| Element appears ignored | Not "Include in Output"; condition/list filter excludes the line; output variable overwritten by a later element; another enabled version takes precedence [inferred] (section 2) | Simulate with the waterfall; check ordering ([procedure-anatomy-and-ordering.md](./procedure-anatomy-and-ordering.md)) and the enabled versions (section 2) |
| Only one line fails | Per-line failure (bad adjustment type, no matching table row) [inferred] | Operations Console > Debug Details tab troubleshoots a failed API call [Help] `ind.pricing_operations_console.htm`; expand the line [inferred] |
| Error status, empty error log | A line item was not executed for pricing, so the status is Error while the log is empty [Help] `ind.pricing_understand_and_resolve_api_execution_messages.htm` | Check line filters and procedure plan routing [inferred] |
| Price Waterfall error about Map Line Item | `price_water_fall` unmapped in Map Line Item | Map in Pricing Setting and Map Line Item [Help] `ind.pricing_map_context_tags_in_pricing_procedures.htm` ([`runtime-and-observability.md`](runtime-and-observability.md#observability)) |
| Pricing slow or timing out | Procedure over its 1 min default (max 2 min), element over its 60 s default (max 80 s) [Help] `ind.pricing_limits.htm`; advanced price logs left on, Apex hook callouts, many Map Line Item mappings [inferred] | Disable advanced logs; trim elements; query lean tags; enable parallel execution (an org-wide setting that affects every active procedure, and not with Map Line Item); limits: [`runtime-and-observability.md`](runtime-and-observability.md#pricing-limits) |
| Procedure never invoked | Wrong selection in Revenue Settings vs Salesforce Pricing Setup vs Product Discovery Settings [Help] (section 1); version not active or start date earlier than context definition Effective From [Help, cloning rules]; plan routes elsewhere [inferred] | Section 1; list versions with `list_expression_sets.py` |
| Procedure plan skips procedures | Plan inactive (repo default `procedureplans_active: false`) [Repo], orchestration setting off [Help], rule-based section criteria unmet [inferred] | Check plan version status and Revenue Settings; see pricing-wiring section C |
| Price revision or header discount applied twice | Active plan: the Revenue Settings procedure re-runs, or with `skipOrgSttPricing=true` the plan's distribution procedure re-distributes [Repo, measured] (section 3) | Deactivate the plan version, or keep one pricing procedure per run |
| Waterfall shows only the last procedure | Multiple procedures chained in one plan | Consolidate into one procedure |
| Promotions misapplied after editing tag mappings | Parallel execution caches custom tag mappings at activation [Help] `ind.pricing_procedure_plan_limits.htm` | Deactivate and reactivate |
| Hook change to Start Date/Quantity ignored by validation | ARC validation precedes the pre-pricing hook [inferred] | Set values in the PST payload [inferred] |
| Output resolution stops a line (List Price or Price Tracking) | No Price Book decision-table row for the product | Add the row, refresh the table. For a Price Adjustment Matrix, check its adjustment table instead |
| Per-line pricing errors [Core]: `DUPLICATE_VALUE_FOUND_IN_LOOKUP` (a lookup returned more than one row: List Price, Minimum Price, Bundle Discount and the other lookup-based discount elements incl. Price Adjustment Matrix, Base Rate in rating), `UNEXPECTED_ERROR_DURING_LOOKUP` (the lookup returned errors: List Price, Volume/Tier Discount, Bundle Discount, others), `OVERLAPPING_ADJUSTMENT_TIERS` (Tier Discount, tier range matches more than once; overlapping Volume rows give the duplicate-value error instead, see [volume-and-tier-discount.md](./elements/volume-and-tier-discount.md)), `INVALID_FORMULA` (Formula-Based Pricing, any failure evaluating the formula) | Duplicate rows or overlapping tiers in the decision table or matrix; lookup failure; formula that fails to evaluate | Fix the table data and refresh; fix the formula in the element |
| Save error "Add Pricing Setting as the first element…" or "You can only add one Pricing Setting element…" [Core] | Pricing Setting missing or duplicated | Keep exactly one (see save-time table in procedure-anatomy) |
| Save error `Ensure that the lookup table in the <name> step is valid and try again.` [Core] | Lookup id cannot be resolved from the step; or the element type has no table mapped in the pricing recipe for the procedure's usage subtype (the message then reads "The pricing element type isn’t valid. Use elements that are associated with lookup tables and try again."; Discount Distribution Service is exempt from this check); or the step's table is not among the tables mapped for that type. The recipe check is skipped during package install; Minimum Price has its own table checks | Map the table in the pricing recipe for the procedure's usage subtype (pricing-wiring section A) |
| Bulk price change not reflected | Decision tables not refreshed | Refresh (section 8) |
| Amend/cancel/renew with Order output, or a plain reprice of an existing order, fails with UNKNOWN_EXCEPTION "We couldn't fetch the data for RLM_SalesTransactionContext context definition"; Quote output works | A stock tag the procedure declares with a Quote-lens attribute row and no Order-lens row [Measured: 2026-11-12, 264, scratch, one org; found by bisection] (a custom tag with the same gap is untested); or a custom attribute the procedure reads mapped on `QuoteEntitiesMapping` but not `OrderEntitiesMapping` [Repo]. On that org a plain order reprice (Place with System or Force) failed the same way while Skip and order creation succeeded | Query the procedure's declared tags on the Order lens, halving the set to find the offender, and add a field-less Order-lens row for it. Also map custom attributes on both lenses; `validate_context_plan.py` flags those. Details: [`../rlm-business-apis/backdated-asset-lifecycle.md`](../rlm-business-apis/backdated-asset-lifecycle.md); mappings: [`../context-service/authoring-and-lifecycle.md`](../context-service/authoring-and-lifecycle.md) → *Populate an attribute from org data* |

## Open questions

- Setup labels per edition (Growth vs Advanced) were not compared.
