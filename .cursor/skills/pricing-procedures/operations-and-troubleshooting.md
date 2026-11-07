# Pricing Procedures: Operations and Troubleshooting

> Release 264 / API v68.0. Sources: Help `ind.pricing_*` articles (cited inline);
> shipped XML and `cumulusci.yml` in this repo. Not live-verified. Generic Expression Set
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
  Expression Set Templates > pick template > Save As (new procedure or new version). [Help]
- Cloning rules: you may assign a custom context definition on Save As; a cloned version
  takes only a version name and number; the clone's start date must be later than the
  context definition's Effective From. [Help]
- Help note: to price quotes and orders, clone the "Revenue Management Default Pricing
  Procedure" template. [Help]
- Permission sets: Salesforce Pricing Design Time User (create/update/delete/clone),
  Salesforce Pricing Run Time User (use). [Help]

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
- Versions: a procedure has versions; when several enabled versions match, the **highest
  rank** wins. [Help] `ind.pricing_set_up_your_discovery_procedure.htm` states this for
  discovery procedures. [Core] The pricing-procedure definition carries the same rank-bearing
  version model (highest-rank enabled version wins); the version-selection query itself was not
  located in core, so confirm on a live org if two enabled versions overlap. An active version cannot be
  edited or deleted through Connect; deactivate first (see expression-sets skill).
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
  enabled; for Apex hooks leave "Exclude Default and Sales Transaction Type Pricing Procedures"
  disabled. Use the same context definition across procedures and the plan. [Help]
- Do not chain several pricing procedures in one plan. Limits [Help]: the waterfall shows only
  the last procedure; Derived Price sees only the Net Unit Price at the end of its own procedure;
  the Inclusive Price "skip pricing" flag does not survive into the second procedure (workaround:
  second procedure checks `InclusivePrice` and stops pricing); with parallel execution on,
  custom tag mappings are cached at activation, so deactivate and reactivate after editing a
  rule library version.
- Repo mechanics (overlays, `placement.afterSubSectionType`, plan-version deactivation) are in
  [`../pricing-wiring/SKILL.md`](../pricing-wiring/SKILL.md) section C. The repo builds the quote
  plan **inactive by default** (`procedureplans_active: false` in `cumulusci.yml`) because an
  active plan doubles price revision and truncates the waterfall; PRM distributor pricing needs
  it on. [Repo] An inactive plan means PST falls back to the Revenue Settings procedure.
  Which of those applies in a given org must be checked live.

## 4. Procedure output resolution

[Help] `ind.pricing_procedure_output_resolution.htm`, `ind.pricing_create_a_procedure_output_resolution_record.htm`,
`ind.pricing_understand_your_resolution_variables.htm`

Picks one definitive price when several candidates exist (multiple price books, stacked
adjustments). Supported only on **List Price, Price Tracking, Price Adjustment Matrix** elements.

| Strategy | Effect |
|---|---|
| Minimum / Maximum | Lowest / highest candidate price |
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

Headless API verification, the price waterfall and its persistence and tag mapping, price logs
and advanced price logs, the decision explainer, the Revenue Cloud Operations Console, price
history tracking, pricing adjustment batch jobs and API execution messages are in
[`runtime-and-observability.md`](runtime-and-observability.md#observability).

## <a name="6-execution"></a>6. Execution

The Place Sales Transaction order of execution, parallel execution, Apex hooks, the runtime model
and guardrails (delta pricing, timeouts) and the pricing limits table are in
[`runtime-and-observability.md`](runtime-and-observability.md#execution).

## 7. Context tag mapping

[Help] `ind.pricing_map_context_tags_in_pricing_procedures.htm`, `ind.pricing_add_context_tags_automatically_to_your_pricing_elements.htm`

Tags bind procedure variables to context definition fields; without them the procedure cannot
read input or write results. Pricing Setting (first element, common variables) and Map Line Item
(precise line/sub-line mapping) do the mapping. "Auto Populate Context Tags" (Einstein, needs
Prompt Template User) suggests mappings with a confidence score; unsupported on Discount
Distribution Service, Formula Based Pricing, Stop Pricing. Context definition authoring and
tag lifecycle: [`../context-service/SKILL.md`](../context-service/SKILL.md). An
`Invalid tag attribute name key` error means a tag name being used isn't defined on the context
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
complete sync). Verify with the Last Refreshed timestamp. Authoring, refresh and freshness
checks: [`../decision-tables/SKILL.md`](../decision-tables/SKILL.md).

## 9. Troubleshooting (cross-element)

Deploy and Connect mutation errors are not repeated here; see the *Troubleshooting Decision
Tree* in [`../pricing-wiring/SKILL.md`](../pricing-wiring/SKILL.md) and *Known errors &
conditions* in [`../../../docs/references/expression-set-connect-api-reference.md`](../../../docs/references/expression-set-connect-api-reference.md).
Element-specific errors are in the element files under [`elements/`](./elements/).

| Symptom | Likely cause | Fix |
|---|---|---|
| Plausible but wrong price, no error | Stale decision table; missing `CurrencyIsoCode` input on a lookup (multicurrency); wrong procedure selected | Check freshness (section 8); pricing-wiring wrong-currency entry; confirm procedure in Revenue Settings (section 1) |
| Element appears ignored | Not "Include in Output"; condition/list filter excludes the line; output variable overwritten by a later element; another enabled version takes precedence (rank; unconfirmed for pricing procedures, see section 2) | Simulate with the waterfall; check ordering ([procedure-anatomy-and-ordering.md](./procedure-anatomy-and-ordering.md)) and the enabled versions (section 2) |
| Only one line fails | Per-line failure (bad adjustment type, no matching table row) | Operations Console > Debug Details > expand the line |
| Error status, empty error log | Line never executed for pricing | Check line filters and procedure plan routing |
| Price Waterfall error about Map Line Item | `price_water_fall` unmapped in Map Line Item | Map in Pricing Setting and Map Line Item ([`runtime-and-observability.md`](runtime-and-observability.md#observability)) |
| Pricing slow or timing out | Procedure over 1 min (max 2), element over 60 s (max 80 s); advanced price logs left on; Apex hook callouts; too many Map Line Item mappings | Disable advanced logs; trim elements; query lean tags; enable parallel execution (not with Map Line Item); limits: [`runtime-and-observability.md`](runtime-and-observability.md#pricing-limits) |
| Procedure never invoked | Wrong selection in Revenue Settings vs Salesforce Pricing Setup vs Product Discovery Settings; version not active or start date earlier than context definition Effective From; plan routes elsewhere | Section 1; list versions with `list_expression_sets.py` |
| Procedure plan skips procedures | Plan inactive (repo default `procedureplans_active: false`), orchestration setting off, rule-based section criteria unmet, or "Exclude Default and Sales Transaction Type Pricing Procedures" on | Check plan version status and Revenue Settings; see pricing-wiring section C |
| Waterfall shows only the last procedure | Multiple procedures chained in one plan | Consolidate into one procedure |
| Promotions misapplied after editing tag mappings | Parallel execution caches custom tag mappings at activation | Deactivate and reactivate |
| Hook change to Start Date/Quantity ignored by validation | ARC validation precedes the pre-pricing hook | Set values in the PST payload |
| Output resolution stops a line (List Price or Price Tracking) | No Price Book decision-table row for the product | Add the row, refresh the table. For a Price Adjustment Matrix, check its adjustment table instead |
| Bulk price change not reflected | Decision tables not refreshed | Refresh (section 8) |
| Amend/cancel/renew with Order output fails with UNKNOWN_EXCEPTION "We couldn't fetch the data for RLM_SalesTransactionContext context definition"; Quote output works | A custom attribute the procedure reads is mapped on `QuoteEntitiesMapping` but not `OrderEntitiesMapping` [Repo] | Map it on both lenses; `validate_context_plan.py` flags it ([`../context-service/authoring-and-lifecycle.md`](../context-service/authoring-and-lifecycle.md) → *Populate an attribute from org data*) |

## Open questions

- Rank-based selection for pricing procedures: not confirmed in core (see section 2).
- Behavior of PST with the quote plan inactive: confirm live.
- Exact Setup labels may differ per edition (Growth vs Advanced).
