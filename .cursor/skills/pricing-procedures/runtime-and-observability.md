# Pricing Procedures: Runtime and Observability

> Sub-file of `.cursor/skills/pricing-procedures/SKILL.md`. Release 264 / API v68.0. Sources:
> Help `ind.pricing_*` articles (cited inline); core 264 for the runtime model. Not
> live-verified. Companion to [`operations-and-troubleshooting.md`](operations-and-troubleshooting.md), which covers
> procedure selection, Simulate/activate, plans, output resolution, tag mapping, decision-table
> sync and the cross-element symptom table.

How to see what a pricing run did (waterfall, logs, decision explainer, Operations Console,
batch jobs, execution messages) and how a run executes (Place Sales Transaction order, parallel
execution, Apex hooks, the runtime model and guardrails, limits).

## Observability

### API-based verification [Core][inferred from client call shapes]
Headless sequence for a scripted check (v68.0): `POST /connect/contexts` (metadata + data as a
JSON string; returns `contextId`), `POST /connect/core-pricing/price-contexts/{contextId}` with
`{"procedureName": "<name>", "configurationOverrides": {...}}` (returns an `executionId`),
`GET /connect/core-pricing/waterfall/{lineItemId}/{executionId}`, and
`POST /connect/contexts/query-tags` with `{"contextId","tags":[...]}` to read results. The
`contextId` is request-scoped; chain these in one script. Naming a procedure bypasses the
procedure plan. Waterfall needs the waterfall setting on (below). Not exercised in this repo.

| Capability | Enable / find | Notes |
|---|---|---|
| Price waterfall | Salesforce Pricing Setup > Activate Price Waterfall for API responses | `ind.pricing_enable_price_waterfall.htm` |
| Waterfall persistence | Same page > Price Waterfall Persistence | Stores each calculation step; `ind.pricing_set_price_waterfall_persistence.htm` |
| Waterfall tag mapping | Map `price_water_fall` in **both** Pricing Setting and Map Line Item | Else error below; `ind.pricing_map_context_tags_in_pricing_procedures.htm`. Shipped Pricing Setting maps `PriceWaterfall` to `price_water_fall`. [Repo] |
| Waterfall setup objects | Setup > Decision Explainer | Subtype Definition, Business Process Type Definition, Explainability Action Definition/Version; `ind.pricing_view_setup_objects_price_waterfall.htm` |
| Price Logs Capture | Salesforce Pricing Setup > Price Logs Capture | Turning it on auto-enables waterfall and persistence (logs derive from waterfall data); `ind.pricing_set_up_price_logs_capture.htm` |
| Advanced price logs | Salesforce Pricing Setup > Advanced Price Log Settings | Per-element input values and exceptions (Attribute-Based, Derived, Price Propagation, Pricing Promotion). Needs Salesforce Pricing Admin. Turn off after debugging (performance). Read via Pricing Waterfall API; `ind.pricing_advanced_price_log_settings.htm` |
| Decision explainer | Setup > Decision Explainer: Expression Set Message Token, Explainability Message Template (Step Type Business Element, Usage Type Pricing) | Then in the Builder: deactivate, refresh, element gear > Show decision explainer, pick success/failure templates, map tokens (`${TokenName}`) to tags; `ind.pricing_configure_decision_explainer_for_price_waterfall.htm` |
| API execution logs | App Launcher > Revenue Cloud Operations Console | Every headless/pricing API run (discovery and pricing) incl. failures; Details and Debug Details tabs. Deleting a log removes it from PricingAPIExecution / PricingProcessExecution but the waterfall still shows it; `ind.pricing_view_pricing_api_execution_logs.htm` |
| Price history tracking | Salesforce Pricing Setup > min/max price tracking, duration | Max 30 days, default 7. Changing it resets the daily history jobs; avoid; `ind.pricing_set_price_history_tracking.htm` |

### Pricing adjustment batch jobs

[Help] `ind.pricing_pricing_adjustment_batch_jobs.htm`, `ind.pricing_perform_pricing_adjustment_batch_job.htm`,
`ind.pricing_execute_failed_pricing_batch_jobs.htm`, `ind.pricing_view_pricing_adjustment_batch_job_logs.htm`

Bulk price edits from list views/related lists of Price Book Entry, Attribute Based Adjustment,
Bundle Based Adjustment, Price Adjustment Tier. Update types: Amount, Percentage, Override
(negative number to decrease). Max 200 records per batch; run one job at a time. Price
adjustment schedules need effective dates; price book entries do not. Failed or partial jobs:
App Launcher > Price Adjustment Batch Jobs > Related > Pricing Adjustment Batch Job Log, edit
records, Rerun. After bulk price changes, refresh decision tables ([`operations-and-troubleshooting.md`](operations-and-troubleshooting.md) → section 8).

### API execution messages

[Help] `ind.pricing_understand_and_resolve_api_execution_messages.htm` (article title "Resolve
API Execution Errors"). The
article gives guidance, not a message catalog; summary of what it states:

| Situation | Where to look / meaning |
|---|---|
| One line item fails, others succeed | Expand the line item under Debug Details > Pricing Procedure; failure is per line (example: wrong Adjustment Type on a Manual Discount fails only that line) |
| Derived price call fails | Check Debug Details > Discovery Procedure (JSON) and Pricing Procedure separately |
| Error status but empty error log | A line item was never executed for pricing |
| "Specify a context tag for the Price Waterfall variable in the Map Line Item element when price waterfall is enabled and setup in the Pricing Settings element." | Waterfall on but Map Line Item lacks the `price_water_fall` mapping [Help] |

## Execution

### Place Sales Transaction order of execution
[Help] `ind.pricing_understand_the_order_of_execution_for_place_sales_transaction.htm`

Save header; header triggers; sync context data in; hydrate; configuration; resolve Amend/Renew/Cancel
(ARC) data; **ARC validation**; pricing = pre-pricing Apex hook, pricing logic, post-pricing Apex
hook; persist context; record triggers; sync context out; record-triggered flows. ARC validation
runs **before** the pre-pricing hook, so hook edits to Start Date or Quantity bypass ARC
validation: set them in the request payload instead.

### Parallel execution
[Help] `ind.pricing_execute_pricing_elements_in_parallel.htm`

Salesforce Pricing Setup > Parallel Execution applies to **all** active procedures called from
Headless/Pricing APIs. Independent elements (no output feeding another's input) run together;
list filters run sequentially, elements inside them in parallel; waterfall sequence tags change
but execution order does not. **Map Line Item does not support parallel execution**: disable it
to use that element.

### Apex hooks
[Help] `ind.pricing_customize_pricing_procedures_with_apex_hooks.htm`, `ind.pricing_apex_hooks_best_practices.htm`

- Class implements `RevSignaling.SignalingApexProcessor`; add as an Apex-type section in the
  procedure plan, prehooks above and posthooks below the Pricing Procedure section.
- Apex must be the first or last element of the plan sequence (Revenue Management process type).
- No DML in hooks (stale context). External callouts only when PST is triggered from the UI or
  PST API (not Apex/Flow), and not with Double Persist; they hurt performance, no SLO.
- Governor limits are cumulative; retrieve only needed data (heap).
- Prefer `leanerQueryTags` over `queryTags`; query specific tags (`LineItem`,
  `ItemProductCode`, ...) not broad `SalesTransactionItem`; request `LineItem$DmlStatus` as its
  own tag and skip DELETED items. `leanerQueryTags` returns `leanerQueryTagResult` plus a shared
  `recordsInfo` list indexed by `recordIdIndexesForPath` (0 transaction, 1 item, 2 detail).

### Runtime model and guardrails [Core]
- Per request: validate context, resolve the procedure (no procedure named: the active pricing
  recipe's default procedure), then execute elements in order. Each element runs list operation,
  payload update (decision-table lookup), calculate. The waterfall is assembled at the end and
  written back to the context.
- **Delta pricing:** a procedure-level run mode in which unchanged lines carry forward prior results
  and only changed or deleted lines are priced; elements receive deleted lines too in this mode.
  Compound Price Revision still reprices every line of a ramp group (see its element file).
- **Parallel execution:** the procedure is split into per-element tasks; independent tasks run on a
  bounded thread pool (per-request and org-wide thread caps are org values). Apex hooks, Price
  Propagation and Breakdown Line Mapping are not run in parallel. Price Revision additionally
  dispatches ramp groups in parallel only from 4 groups up.
- **Guardrails:** exceeding the procedure max runtime or element max runtime throws a timeout
  error that fails the call; saving a procedure over the max element count or exceeding the max
  procedure count is rejected at design time. Limits are org values (table below); a platform
  gate can skip validation.
- Version selection rank: [`operations-and-troubleshooting.md`](operations-and-troubleshooting.md) → section 2.

### Pricing limits
[Help] `ind.pricing_limits.htm` (raise via Support ticket)

| Value | Default | Min | Max |
|---|---|---|---|
| Discovery procedures per org | 2000 | 1 | 10000 |
| Discovery procedure active duration | 10 s | 1 s | 60 s |
| Pricing procedures per org | 2000 | 1 | 10000 |
| Pricing procedure active duration | 1 min | 1 s | 2 min |
| Elements per discovery procedure | 50 | 2 | 100 |
| Elements per pricing procedure | 200 | 2 | 200 |
| Element active duration | 60 s | 4 ms | 80 s |
| Map Line Item mappings | 70 | - | 100 |
| Assignment context tag mappings | 20 | - | 50 |
| Price impacting attributes per product | 25 | 1 | 50 |
| Contributing products per derived product | 40 | 1 | 50 |
| Assets associated with one contributing asset | - | - | 50 |

Other limits [Help]: no children of sibling nodes in any context definition; element logic is
restricted to tags at Transaction Item and Transaction Header level; Connect REST returns
numbers >= 10,000,000 in plain decimal; the Invocable Headless API returns values below 0.000001
in scientific notation; stored trailing zeros are returned at full precision.

## Open questions

- Help does not list API execution message strings; core keeps them as localized labels keyed
  by code (for example `INVALID_PRICE_REVISION_FORMULA`), so a catalog needs a live sample.
