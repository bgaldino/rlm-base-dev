# Pricing Procedures: Runtime and Observability

> Sub-file of `.cursor/skills/pricing-procedures/SKILL.md`. Release 264 / API v68.0. Sources:
> Help `ind.pricing_*` articles (cited inline); core 264 for the runtime model. Not
> live-verified, except the headless pricing action (measured on 2026-11-10 and 2026-11-11,
> below) and the persisted waterfall read (2026-11-11). Companion to [`operations-and-troubleshooting.md`](operations-and-troubleshooting.md), which covers
> procedure selection, Simulate/activate, plans, output resolution, tag mapping, decision-table
> sync and the cross-element symptom table.

How to see what a pricing run did (waterfall, logs, decision explainer, Operations Console,
batch jobs, execution messages) and how a run executes (Place Sales Transaction order, parallel
execution, Apex hooks, the runtime model and guardrails, limits).

## Observability

### API-based verification [Core][inferred from client call shapes]
Endpoint reference: [`docs/api/pricing-business-apis-v68.md`](../../../docs/api/pricing-business-apis-v68.md).
Headless call shapes (v68.0): `POST /connect/contexts` (metadata + data as a JSON string;
returns `contextId`), `POST /connect/core-pricing/price-contexts/{contextId}` with
`{"procedureName": "<name>", "configurationOverrides": {...}}` (returns an `executionId`),
`GET /connect/core-pricing/waterfall/{lineItemId}/{executionId}`, and
`POST /connect/contexts/query-tags` with `{"contextId","tags":[...]}` to read results. Naming a
procedure bypasses the procedure plan. Waterfall needs the waterfall setting on (below). This
multi-call chain is not exercised in this repo; the single-call action below was run by hand
on 2026-11-10 and recorded; no repo script calls it.

The `contextId` is **request-scoped** by default: each HTTP call is a separate Salesforce
request, so running these calls one after another from a script does **not** keep the context
alive, and the price and query calls get an expired handle. `query-tags` is also pilot-gated.
On a normal org, keep the lifecycle in **one request**. Either make one
`POST /services/data/v68.0/actions/standard/runSalesforceHeadlessPricing` call (scriptable): it
takes `contextDefinitionId`, `contextMappingId`, `pricingProcedureId` and `pricingData`, builds
the context, prices it and returns `pricingResult` in the same request, so the default request
scope is enough (`businessObjectType` in `pricingData` must be the SObject the mapping uses). Or
use one Flow that builds the context, runs `runSalesforcePricing` (Flow-only) with its
`contextInstanceId` and `pricingProcedureName`, and reads the tags in the same transaction
[Dev guide `pricing_invocable_actions_parent.htm`, `actions_obj_run_salesforce_headless_pricing.htm`,
`actions_obj_run_salesforce_pricing.htm`]. The multi-call REST path works only with
SESSION scope or context reuse enabled, plus the query pilot. Which path fits which org:
[`../context-service/runtime-and-persistence.md`](../context-service/runtime-and-persistence.md).

**Measured: `runSalesforceHeadlessPricing` against a named procedure** [Measured: 2026-11-10, 264,
QuantumBit scratch org; worked example in
[`elements/commitment-term-discount.md`](elements/commitment-term-discount.md)]:

- Request: `POST /services/data/v68.0/actions/standard/runSalesforceHeadlessPricing` with
  `{"inputs":[{"contextDefinitionId":"<RLM_SalesTransactionContext 11O…>","contextMappingId":"<QuoteEntitiesMapping 11j…>","pricingProcedureId":"<procedure API name>","pricingData":"<JSON string>","skipDiscovery":true,"isSkipWaterfall":true,"persistContext":false,"useSessionScopedContext":false,"displayContext":false,"taggedData":false}]}`.
  Sent with `sf api request rest … --target-org <sf_alias>`, so no token handling.
- `pricingProcedureId` accepts the procedure's **API name**; an inactive procedure fails with
  `Ensure that this procedure has at least one active version.`
- `pricingData` that worked: a root `SalesTransaction` **object** (not an array) holding the
  lines as an **array** of objects under `SalesTransactionItem`, **no `id` keys** on either node,
  `businessObjectType` `Quote` on the `SalesTransaction` node and `QuoteLineItem` on each
  `SalesTransactionItem`; keys are context **attribute** names (`Product`,
  `ProductSellingModel`, `PricebookEntry`, `Quantity`, `StartDate`, `EndDate`, `UnitPrice`,
  `Discount`, `SubscriptionTerm`, `SubscriptionTermUnit`, `SellingModelType`, `PricingTermUnit`,
  `SalesTransactionItemSource`, …). Values passed inline price the line without any record:
  `ListPrice` still came from the price book entry, and `UnitPrice` was used as the input unit price.
- Line inputs that failed pricing when missing or malformed [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]:
  - `SalesTransactionItemSource` missing: the first step fails with `nulltagName = LineItem`. A
    per-line string such as `PROBE_LINE_1` worked.
  - `PeriodBoundary` missing: `INVALID_PERIOD_BOUNDARY`. `Anniversary` worked.
  - `StartDate` or `EndDate` as a bare date: proration fails with `StartDate and EndDate are
    required`. Date-times (`2027-01-01T00:00:00.000Z`) worked. One Time and Evergreen lines
    priced without an `EndDate`.
- The dev guide sample's mapping (`businessObjectType` `SalesTransaction` with the definition's
  `SalesTransaction` mapping) failed both ways tried (a root object without `id` keys, and a root array with `id` keys):
  `INTERNAL_ERROR: We couldn’t fetch the data for RLM_SalesTransactionContext context definition.
  Try again later or contact your Salesforce admin for help.` [Dev guide:
  `actions_obj_run_salesforce_headless_pricing.htm` shows that sample].
- Response: `outputValues.pricingResult` (and `contextDetails`, `pricingProcessErrors`) come back
  as **JSON strings**, not the nested objects the dev guide sample shows. `pricingResult` is keyed
  by context attribute name (`NetUnitPrice`, `NetTotalPrice`, `PricingTermCount`, `TotalAmount`,
  …); each value carries a `dataPath` of generated ids (`CTX_Quote_1`, `CTX_QuoteLineItem_2`, …,
  in payload order). `pricingProcessStatus` was `Completed`. A line-level failure (for example a
  Term Defined line with no end date and no term: `END_DATE_MISSING`) shows only inside that
  line's `PriceWaterFall` value, while the call still reports `isSuccess: true`.
- `isSkipWaterfall: true` still returned each line's `PriceWaterFall`, with per-step entries (the
  formula step's included); the dev guide defines `true` as *generate* the waterfall, despite the name.
- With `persistContext: false` and inline values, no context is stored and no quote record is
  changed. The run is still recorded as a pricing API execution log (table below).

**Measured: reading a saved line's waterfall** [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch
org]. For a priced quote line, read `QuoteLineItem.PriceWaterfallIdentifier`, a `<ref>:<executionId>`
pair, split it at the last colon, and call `GET /connect/core-pricing/waterfall/<ref>/<executionId>`.
The response lists each step with its `pricingElement` and output values. Calls built from the
line's record id and from a `PricingAPIExecution.ExecutionKey` returned
`FETCH_EXPLAINABILITY_LOG_ERROR`.

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
Bulk load order and packaged export/import: [`../pricing-setup/import-export-and-bulk-data.md`](../pricing-setup/import-export-and-bulk-data.md).

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
(ARC) data; **ARC validation** (skipped when the `validateAmendRenewCancel` request option is false; it defaults to true) [Core]; pricing = pre-pricing Apex hook, pricing logic, post-pricing Apex
hook; persist context; record triggers; sync context out; record-triggered flows. ARC validation
runs **before** the pre-pricing hook, so hook edits to Start Date or Quantity bypass ARC
validation: set them in the request payload instead.

### Parallel execution
[Help] `ind.pricing_execute_pricing_elements_in_parallel.htm`

Salesforce Pricing Setup > Parallel Execution (needs the Salesforce Pricing Design Time permission) applies to **all** active procedures called from
Headless/Pricing APIs. Core: a procedure containing a Price Propagation or Apex Action element runs sequentially (Help is silent on this), and core leaves Map Line Item and Pricing Setting steps out of the parallel task graph [Core]. Independent elements (no output feeding another's input) run together;
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
- Delta pricing: see [Delta pricing](#delta-pricing).
- **Parallel execution:** the procedure is split into per-element tasks; independent tasks run on a
  bounded thread pool (per-request and org-wide thread caps are org values). Apex Action and Price
  Propagation elements are not eligible, and one of either makes the whole procedure run
  sequentially (runtime log: "Dependency Graph is not eligible for parallel execution"). Map Line Item (Breakdown Line Mapping) and Pricing Setting steps are skipped when the task graph is built
  (prerequisites, not parallelized) and do not block the other elements; Help still requires parallel execution off to use Map Line Item. Price Revision additionally dispatches ramp groups in parallel only when the
  procedure has at least 4 compound ramp groups; fewer run sequentially (threshold constant of 4 read in core).
- **Guardrails:** exceeding the procedure max runtime or element max runtime throws a timeout
  error that fails the call; saving a procedure over the max element count or exceeding the max
  procedure count is rejected at design time. Limits are org values (table below); the
  element-count check and both runtime-timeout checks are skipped only when an internal
  performance-environment gate is open (not a production path); the procedure-count check is not gated [Core].
- Version selection rank: [`operations-and-troubleshooting.md`](operations-and-troubleshooting.md) → section 2.

### Delta pricing

Delta pricing is an org setting (Setup > Revenue Settings > Delta Pricing for Quotes and Orders)
[Core], off unless enabled; its platform declaration marks it beta [Platform behaviour, traced],
though neither Help nor the Metadata API reference says so (Setup label not checked). Delta
pricing applies only when all of these hold: the org setting is on and Dual Persistence mode is
off; the request is a PATCH of a Quote, Order or Cart with System pricing; the header's calculation
status is Completed with Pricing or Completed with Tax (a Cart: Completed with Pricing only) with no
validation errors; and the transaction tracks its updates. Force pricing, Reprice All and any other
request reprice every line [Platform behaviour, traced]. Under delta
pricing, unchanged lines are skipped unless they depend on a changed line or the step always runs
(aggregation, discount distribution, compound uplift in Price Revision) [Platform behaviour,
traced]. The repo enables it in `config/project-scratch-def.json` and most `orgs/*.json` (not
dev-mfg or the TFID shapes), and `prepare_rlm_org` deploys it as true from the pre settings bundle
on every build, including shapes whose definition does not set it, so an org built by
`prepare_rlm_org` has it on [Repo]. Its documented default is false [Metadata API:
`meta_revenuemanagementsettings`], so an org that does not set it has it off. When it applies, the
run mode (set through configuration overrides; the waterfall reports execution mode "Delta
Pricing") starts all non-deleted lines skipped, updated lines become roots of the dependency
graph, and lines derived from them are found and repriced: a partial PATCH reprices the edited
lines plus the lines that depend on them and skips the rest; which relations count as a dependency
was not traced [Platform behaviour, traced].
A deleted line gets error `LINE_ITEM_DELETED_IN_CONTEXT` and is not priced; Map Product and Rule
Fetch also handle deleted lines in discovery, and Asset Discovery runs only when a derived line or
contributor was updated or deleted.
Applied automatically to updates that have no validation errors and follow a successful pricing run,
otherwise a full reprice [Help]. When delta skipping does not apply, every line reruns [Platform
behaviour, traced]. Two Place PATCHes with System pricing re-applied the compound uplift to the
stored `NetUnitPrice` of the uplifted ramp lines after the first segment (untouched lines in both
PATCHes, and in the 2026-11-12 PATCH the patched line as well), unrounded, with `TotalPrice`
unchanged. One changed `UnitPriceUplift` on four non-software lines (configuration method Force,
rules on) [Measured: 2026-11-11, 264, scratch]. The other patched one line with no field change
(configuration Skip), with delta pricing on (read from the org), and changed no line's waterfall id
[Measured: 2026-11-12, 264, scratch; one org]. In the second PATCH no line's waterfall id changed;
that and the unchanged totals in both do not fit a full procedure rerun, and what moved
`NetUnitPrice` on the stored net in these PATCHes is not traced. When Price Revision runs twice over
the same lines in one execution (for example a procedure plan plus the default procedure, when Skip
Default and Sales Transaction Type Pricing Procedures is off), the uplift applies twice [Platform
behaviour, traced]. Reprice All restored correct prices [Measured: 2026-11-11, 264, scratch]. Help:
"If the pricing procedure uses delta pricing and you enable Compound Uplift, the Price Revision
element reprices every line in the ramp group each time it runs, regardless of the delta pricing
setting. This behavior applies only to lines that use Compound Uplift. Delta pricing behaves
normally for lines that do not use it." [Help:
`ind.pricing_use_the_price_revision_element_in_a_pricing_procedure.htm`]. Reprice All runs a full
recalculation whatever the delta setting [Help: `ind.qocal_reprice_all_quotes_and_orders.htm`]; it
was not re-run after the 2026-11-12 PATCH, so re-read every segment's `NetUnitPrice` against
`TotalPrice` afterwards. [Help] `ind.qocal_use_delta_pricing_for_quotes_and_orders.htm`:
recalculates modified lines and their dependents; incompatible with Dual Persistence mode.

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
| Map Line Item mappings | 70 | 1 | 100 |
| Assignment context tag mappings | 20 (core default 25 [Core]; see [assignment](elements/assignment.md)) | 1 | 50 |
| Line items per pricing execution (org value, API 262+) | 1000 | 1000 | 3000 |
| Sub-lines (breakdown lines) per pricing execution (API 262+) | 2000 | 1000 | 3000 |
| Threads per parallel request | 5 | 1 | 20 |
| Variables in an expression set (API 242+) | 1000 | 1 | 5000 |
| Steps in an expression set (API 242+) | 200 | 1 | 250 |
| Conditions per step (API 242+) | 200 | 1 | 200 |
| Business elements in an expression set (API 242+) | 50 | 1 | 200 |
| Context tags used in an expression set (API 248+) | 200 | 0 | 400 |
| Local list node depth in an expression set (API 262+) | 6 | 0 | 6 |
| Multi-hit decision tables per expression set version (API 264+; can differ per process type) | 10 | 1 | 25 |
| Price impacting attributes per product | 25 | 1 | 50 |
| Contributing products per derived product | 40 | 1 | 50 |
| Assets associated with one contributing asset | - | - | 50 |

The pricing-procedure count, duration and element rows, element active duration, the
price-impacting attributes row and the line-item, sub-line and thread rows match core org-value
defaults and bounds; discovery procedures per org use the same procedure-count value [Core]; Map Line
Item mappings (default 70, min 1, max 100) also match the pricing settings org value, enforced at save with "The limit of {0} mappings that can be added to the Map Line Item element was reached in the org. Delete some mappings and try again." [Core]. The expression-set rows (variables through multi-hit decision tables) are Expression Set Builder org values, not on the pricing Help page; defaults, bounds and minimum API versions are from core [Core]. Core disagrees with Help on these rows: Assignment mappings
default 25 (Help: 20); contributing products org value default 500, max 2000 (Help: 40/50);
assets per contributing asset org value default 100, max 1000 (Help: 50); discovery elements
and discovery duration reuse the pricing element and procedure org values (max 200 elements)
rather than Help's 2-100 and 10 s, with discovery-specific error messages [Core]. Treat Help as the published number and verify on the org
before relying on either.

The Record Action cap ("You can add up to {0} Record Action elements to an expression set.") is a fixed 10, not an org value, and its only check is in the event-orchestration usage type; pricing procedures do not hit it [Core].

Other limits [Help]: no children of sibling nodes in any context definition; element logic is
restricted to tags at Transaction Item and Transaction Header level; Connect REST returns
numbers >= 10,000,000 in plain decimal; the Invocable Headless API returns values below 0.000001
in scientific notation; stored trailing zeros are returned at full precision.

## Open questions

- Help does not list API execution message strings; core keeps them as localized labels keyed
  by code (for example `INVALID_PRICE_REVISION_FORMULA`), so a catalog needs a live sample.
