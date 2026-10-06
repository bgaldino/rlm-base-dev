# Updating DRO Configuration and Handling In-Flight Work

## Capture Scope and Before-State

Resolve the requested change to specific configuration IDs and portable keys.
Inspect all references to affected groups/steps/providers: scenarios, dependencies,
workspace items, amend/cancel groups and runtime step definitions. A workspace
is not an ownership boundary; a group can be used by multiple workspaces/scenarios.

Capture current writable fields, relationship IDs, condition JSON, library/context
alignment, and modification timestamps. Identify active fulfillment requests and
their plans/steps, source orders, current states and compensation/PONR settings.
Inspect the target describes before composing queries; use
[objects-and-relationships.md](objects-and-relationships.md) for known links.
Extract to a separate location using [csv-and-sfdmu.md](csv-and-sfdmu.md), and
include advanced fields missing from the shipped export plan when they matter.

Prepare a field-level delta with object/key/target ID, old value, new value,
create/update/clear/remove action, shared consumers and verification. Missing
desired-state fields mean preserve, not clear. Missing desired-state rows mean
preserve, not delete. A rename is an update to the discovered ID, not a new
Name-keyed Upsert that silently duplicates the old configuration.

## Choose the Change Route

| Situation | Route |
| --- | --- |
| New independent configuration | Scoped CSV/SFDMU plan after prerequisites |
| Exclusive existing configuration, compatible change | Small delta dataset with verified matching, or targeted API update |
| Shared configuration or incompatible behavior with active consumers | New groups/steps with distinct keys; retarget only intended scenarios for future submissions |
| Explicit null clear, rename, ambiguous portable key or loader gap | Targeted update to the uniquely discovered target ID |
| Remove referenced configuration | Review consumers/runtime usage and supported deletion behavior; obtain explicit destructive-action authorization |
| Change active order fulfillment | Supported runtime action/transaction workflow; separate from configuration writes |

When creating a replacement graph, remap its internal dependencies and compensation
group references, retain intentional external edges, and create prerequisites
before retargeting scenarios. Keep old definitions while existing consumers need
them. Replacement grouping is a deployment technique, not a platform promise of
versioned plan execution. Verify future and existing plan behavior separately.

Check before-state again immediately before applying, especially for shared records.
If another actor changed affected values/edges, re-read and recompute the delta.
Do not overwrite intervening work based on a stale extract.

## Explicit Clears and Conditions

Blank CSV cells do not establish that SFDMU clears a target field. Use verified
loader null handling in a disposable org, or a standard REST PATCH with explicit
JSON null to the selected ID when the field is nillable/updateable.

For example, after confirming provider clearance and `StepType=ManualTask` are
compatible with the target's validation and existing dependencies:

```http
PATCH /services/data/v68.0/sobjects/FulfillmentStepDefinition/<target-step-id>
Content-Type: application/json

{"StepType":"ManualTask","IntegrationDefinitionNameId":null}
```

Authenticate through an existing authorized API session, with the target's
supported API version. Do not expose tokens or put them in `sf` CLI arguments.
Read back both fields and check that dependent relationships remain intact.
If state propagation restricts a step-type change, plan the required propagation
change explicitly; do not clear unrelated behavior merely to make the write pass.
For `PropagateStateToDependentStep`, Help's **None** choice may be represented by
a null/omitted value rather than a literal API picklist value. Inspect target
picklists and nullability before setting or clearing it; verify the resulting behavior.

For conditions, update the corresponding JSON field through its supported surface.
The platform processes condition creation, updates and removal, including removal
of associated rule artifacts where applicable. Verify generated references and true/false
evaluation on the target; do not clear a raw RuleSet lookup and assume the condition
was removed, or manually copy internal rule tables across orgs.

The repository's `update_product_fulfillment_decomp_rules` task updates **all**
decomposition rules. It is not a safe general repair command for a scoped update.
If condition wiring fails, inspect the affected record, JSON resources, configured
context and active rule library before attempting a repair.

## Failure, Removal and Recovery

SFDMU/API/metadata operations can leave a partial change. Keep a record of successful
writes, created IDs, previous values, and the first failing operation. Stop dependent
writes after failure. For timeouts or uncertain results, query target state before
retrying, rather than inserting a second copy.

Restore prior writable fields and scenario bindings only after checking intervening
changes and consumers. Newly created records can be removed only if no configuration
or runtime references need them and deletion is authorized. Respect child-before-parent
removal, parent-delete cascades and generated RuleSet cleanup. Do not offer rollback
of an executed callout, completed manual work, or submitted order as a database restore.
Those effects need business compensation through supported workflows.

Refresh affected fallout/jeopardy decision-table data after successful rule changes,
including restores. Record recovery steps actually performed and remaining work.

## Supported Runtime Actions

Design-time edits do not by themselves constitute an amendment of a submitted order.
Use an authorized test order to establish future-plan composition; inspect existing
requests separately. The following routes are grounded in the captured 264 guide:

| Intent | Supported route and guard |
| --- | --- |
| Submit an order for decomposition/orchestration | Existing submission Flow, or `POST /services/data/v68.0/actions/standard/submitSalesTransaction`; read the action input contract before constructing a request |
| Freeze an in-flight transaction | `POST /services/data/v68.0/actions/standard/freezeSalesTransaction`, with `salesTransactionId`; inspect plan until Frozen or a terminal failure/timeout |
| Unfreeze | `POST /services/data/v68.0/actions/standard/unfreezeSalesTransaction`; read current input contract and inspect resulting state |
| Amend/cancel in-flight fulfillment | Supported supplemental-order/submission workflow; inspect configured amend/cancel groups and PONR before submitting |
| Retry an AutoTask/callout, complete an eligible step | Available actions in the orchestration-plan UI; inspect step state/eligibility and action result; do not invent an undocumented REST route |

Read the linked [action sources](examples-and-grounding.md) and target action
description for required parameters, not just the route names. Standard REST
invocable actions use an `inputs` array; API authentication and action execution
must follow the existing authorized tool/session. For a simple freeze, the documented
input is shaped as `{"inputs":[{"salesTransactionId":"<transaction-id>"}]}`.

Runtime changes require authorization for the actual action and affected transaction,
including force completion or PONR override. Reuse existing authorization; do not
introduce a blanket extra approval for ordinary configuration updates.

- **Freezing is not Frozen:** in-progress steps can keep a plan Freezing; an
  in-flight change requires Frozen. Bound waits and report steps preventing it.
- **Force freeze:** `ForcePlanFreezeDuringExecution` can allow forceful completion;
  understand and authorize its business effects before use.
- **Compensation:** amended/canceled completed steps are not automatically recreated
  or rerun. Configured Amend/Cancel Step Groups provide the compensating steps.
  Check reverse compensation and propagated states when relevant.
- **PONR:** a bundle reaching Point of No Return restricts its changes; inspect
  scope. The submission action documents an override, but it is never an automatic
  workaround for an invalid change.
- **Order-wide scenarios:** Help documents different post-submission modification
  limits from product/classification scenarios; do not assume every change applies.

## Update Acceptance Scenarios

| Scenario | Required evidence |
| --- | --- |
| Add a prerequisite step | New definition and edge exist; combined graph has no cycle; new plan waits on the correct scoped predecessor |
| Change condition | JSON/generated references agree; representative true and false cases select/skip expected steps |
| Clear provider or custom scope | Field is null after read-back, new step/scope behavior is correct, unrelated fields preserved |
| Ambiguous Name/SKU | Operation stops before write; choose/discover an unambiguous identity |
| Cycle/self-dependency | Reject before deployment, including cycles introduced through existing edges |
| Missing Flow/provider/context tag | Report missing prerequisite; no successful-composition claim |
| Shared group | Unrelated scenarios unchanged; selected scenario uses replacement; active requests inspected |
| Supplemental amend/cancel | Plan state, compensation groups and resulting step states match documented behavior |
| Interrupted/partial load | Successful writes reconciled, no duplicate retry, recovery/outstanding work recorded |

Report target identity, configuration delta, before/after evidence, request/plan IDs,
and three independent statuses: configuration verified, runtime composition verified,
end-to-end fulfillment verified. Include a concrete reason for anything unverified.
