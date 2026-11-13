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
PATCH /services/data/v<api-version>/sobjects/FulfillmentStepDefinition/<target-step-id>
Content-Type: application/json

{"StepType":"ManualTask","IntegrationDefinitionNameId":null}
```

Replace `<api-version>` with a version supported by the target org. Authenticate
through an existing authorized API session. Do not expose tokens or put them
in `sf` CLI arguments.
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
requests separately. The following routes are grounded in the linked documentation
snapshot; check the matching release guide and target API version before use:

| Intent | Supported route and guard |
| --- | --- |
| Submit an order for decomposition/orchestration | Existing submission Flow, or `POST /services/data/v<api-version>/actions/standard/submitSalesTransaction`; read the action input contract before constructing a request |
| Freeze an in-flight transaction | `POST /services/data/v<api-version>/actions/standard/freezeSalesTransaction`, with `salesTransactionId`; inspect plan until Frozen or a terminal failure/timeout |
| Unfreeze | `POST /services/data/v<api-version>/actions/standard/unfreezeSalesTransaction`; read current input contract and inspect resulting state |
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
- **PONR:** Help sets the Point of No Return state when a step marked PONR goes In
  Progress, and spreads it within the bundle: a commercial parent to its children, a
  commercial child to its parent, and a technical item to the commercial items associated
  with it [Help: `ind.dro_point_of_no_return_state_propagation`]. Items in the same order
  but outside the bundle stay changeable [Help:
  `ind.dro_considerations_for_changing_in_flight_orders`], which matches the measured
  freeze scope below. So a source rule "no changes once step X is done" means marking the
  step after X, which reaches In Progress only when X is complete [inferred from Help].
  The submission action documents an override, but it is never an automatic
  workaround for an invalid change. Help says an order past PONR can't be cancelled or
  amended [Help: `ind.dro_point_of_no_return_state_propagation`], but a later amendment of the
  asset through the plain amend route was accepted with the flag set (below), so a source rule
  that must also stop asset amendments or cancellations needs its own validation [inferred].
  Where activation creates assets and billing schedules, the supplemental route refused the
  activated order for those reasons before any PONR check, and a Draft order could not be
  submitted to the plan [Measured: 2026-11-13, 264, scratch, one org; see PONR scope below].
  On such a build no in-flight change reaches a PONR check, so assert the flag and the freeze
  output's per-line allowed flags, and carry a "no change after step X" rule that must hold
  in a validation on the asset-amendment path [inferred]. A PONR flag on a Milestone step did
  apply: the Milestone, the plan's only flagged step, completed within the second it started,
  and freezing the order then denied changes to its line [Measured: 2026-11-13, 264, scratch,
  one org; freeze output]. Help applies the state at In Progress and names no Milestone case.
  A flagged Milestone with no unmet dependency therefore closes its line from plan start; one
  that depends on X would close it when X completes, since a blocked Milestone completed about
  a second after its predecessor ([examples-and-grounding.md](examples-and-grounding.md))
  [inferred].
- **PONR flag placement:** the flag set on a step definition was copied onto the step at
  plan creation, on a Pending dependent step as well as an In Progress one
  [Measured: 2026-11-13, 264, scratch, one org]. The copied flag marks where the state will
  apply; Help's state applies when the step goes In Progress (above), not when the flag is
  copied [inferred].
  Two amendments placed through the plain amend route, one with the flag set, were both
  accepted with no refusal [Measured: 2026-11-13, 264, scratch, one org]; that route showed
  no enforcement, and enforcement itself was not tested.
- **PONR scope (freeze output).** Freezing the order returned an allowed flag per order item.
  With a PONR step In Progress on one child of a bundle, every line of that bundle was denied,
  root and sibling included; a PONR step In Progress on a standalone line denied only that line, not a bundle in
  the same order, and a separate, earlier control order with no PONR step (its callout had failed and its other
  steps were Pending) froze to Frozen with every line allowed [Measured: 2026-11-13, 264,
  scratch, one org]. A supplemental quantity change on the activated order was refused with
  two stated reasons, that its order products had been converted to assets and had billing
  schedules; no PONR refusal was observed [Measured: 2026-11-13, 264, scratch, one org], so whether the route enforces the PONR is still
  untested. A plain freeze, with no force-freeze-during-execution option applied, left a plan
  with a step In Progress Freezing, not Frozen
  [Measured: 2026-11-13, 264, scratch, one org].
- **Order-wide scenarios:** Help documents different post-submission modification
  limits from product/classification scenarios; do not assume every change applies.

## Measured Runtime Behaviour

Each item is one scratch org, 264, 2026-11-13 [Measured: 2026-11-13, 264, scratch, one org],
except the fallout and jeopardy match fields (from describe) and statements marked as Help's.
Time-awareness wasn't recorded for these runs: no time-awareness setting appeared in the
org's retrieved DRO settings metadata [Measured: 2026-11-13, 264, scratch, one org;
retrieved settings metadata]. Help says it is off by default and can't be turned off once
on [Help: `ind.dro_time_aware_fulfillment_enable`], so a plan that turns it on is outside
these conditions; rerun the amendment and cancel checks there.

- **Future-dated steps (setting on).** A step delayed from the previous step's execution
  by two minutes waited, then started. A step waiting on a scheduled date still waited for
  its dependencies. A step with an offset from the source line's start date did not wait
  when the line's service date was a month out and the order was dated today; on two further
  orders with the order date and the line service date a month out (the second also with the
  quote line's start dates), a 10-day offset and a 3-minute offset from that date both
  started at plan creation, and the next-run time carried no offset [Measured: 2026-11-13, 264,
  scratch, one org]. On all three orders the decomposed technical lines had null service and
  end dates [Measured: 2026-11-13, 264, scratch, one org], which may explain it [inferred];
  Help doesn't settle it. Don't promise a start-date offset; use a previous-step delay
  instead (the two-minute delay above waited, then started).
- **Amendment decomposition.** An amendment created a new plan holding the full step set,
  not a delta, and a changed quantity was a full replace. One fulfillment asset's quantity
  after the amendment did not match its line's end quantity; unexplained.
  Help lists a No Change action for lines whose attributes and quantity don't change
  [Help: `ind.dro_fulfillment_order_line_item_actions`],
  but on a bundle amendment two of the unchanged lines came through as an add of 1 (fulfillment
  asset 0 to 1) and a cancel of -1 (asset 1 to 0), while another line of the same order was No
  Change [Measured: 2026-11-13, 264, scratch, one org]. So excluding No Change from a scenario
  or condition does not by itself keep unchanged lines from running steps [inferred]. On that
  order the unchanged lines' pairs netted to zero (1 and -1), and the changed line's did not
  (an add of 7 and a cancel of -5, asset 0 to 7 and 5 to 0). A condition on the action alone
  can't separate them; whether a condition can read the pair's net quantity was not measured.
  Record each technical line's action, quantity and fulfillment asset start and end quantities
  on the first amendment before designing for it.
- **An item across orders.** On a later new-sale order for the same account [Measured:
  2026-11-13, 264, scratch, one org]: an assetizable technical product with Account scope
  got Amend on the fulfillment asset an earlier order had created (the line's fulfillment
  asset start and end quantities read 1 and 2); another assetizable Account-scope item got No Change on its existing
  asset; a non-assetizable Account-scope item got Add with no asset. The source
  relationship's `Action` read Add for all three, so read `FulfillmentOrderLineItem.Action`,
  not the relationship. Help sets the line to Amend whenever it differs from its fulfillment
  asset, whatever the order line's action [Help: `ind.dro_fulfillment_order_line_item_actions`].
  Help defines Account scope as one instance across the account's orders and Order scope as
  one per order, which can't be assetized [Help: `ind.dro_decomposition_scope`]. So work
  that must act on an item an earlier order created needs a scope that spans orders, on an
  assetizable technical product; a custom scope wasn't measured, and an Order-scope item
  recurs on every order [inferred from Help]. An Account-scope assetizable item can therefore
  appear on every later order that carries a line decomposing to it, with Amend or No Change,
  and its group's steps compose again unless their conditions skip those actions [inferred
  from the measured actions]; "no new instance" doesn't mean "no line". When a step is
  skipped by its condition and Skip Branch is on, Help skips the branch that depends solely
  on it [Help: `ind.dro_define_conditions_for_a_fulfillment_step_to_run`]; decide that per
  edge.
  Check the line actions on the first later order.
- **Fallout and jeopardy rules** match on step type, with an optional integration
  definition, flow definition and error code; this is from the rule objects' describe,
  not a run. Measured on the org's steps: a step's jeopardy threshold was null on
  manual steps, and a failed callout step (credential missing) showed zero retries
  although a retry rule exists; both unexplained. A rule existing doesn't show it applied: verify on a live
  step. A decision-table lookup returned nothing, so the freshness link for these rules
  was not tested. For planning: a jeopardy rule targets callouts through an integration
  definition and manual or auto tasks through a flow definition, and a blank field applies
  it to every step of that kind [Help: `ind.dro_configure_fulfillment_step_jeopardy_rules`,
  `ind.dro_sla_jeopardy_administration`]; fallout rules cover callouts and auto tasks, with
  retries and a queue for fatally failed steps [Help: `ind.dro_configure_fallout_rules`].
  A step definition carries a `FlowDefinitionName` field whatever its type, empty on every
  manual task in the measured org [Measured: 2026-11-13, 264, scratch, one org; describe and
  query]; whether a jeopardy rule then matches a manual task through it was not run. Help
  names no rule for Milestone steps. A separate window or queue per step needs its own
  flow or integration definition per step [inferred]. A source's "at risk after N" needs a
  decided estimated duration, because the threshold counts back from it [Help:
  `ind.dro_configure_fulfillment_step_jeopardy_rules`]. Help describes a jeopardy status and
  notification, names no setting for who is notified, and has no reassignment of a late
  step [inferred from Help's silence]. After editing a fallout or jeopardy rule, refresh its
  decision table [Help: `ind.dro_configure_fallout_rules`,
  `ind.dro_configure_fulfillment_step_jeopardy_rules`]; the steps are in
  [authoring-and-deployment.md](authoring-and-deployment.md).
- **Cancel of a non-assetizable technical line.** Cancelling the bundle's root asset decomposed the copy
  product's line as an Add of quantity 0, not a Cancel, and its Add steps were still created and started; no
  fulfillment asset was created or changed for it, while the assetizable lines decomposed as
  Cancel [Measured: 2026-11-13, 264, scratch, one org]. Design Add steps to tolerate a zero
  quantity [inferred from one run].
- **Dependency across order items.** A plan-scope step whose dependency was set at line scope
  waited for every instance across the order items, not one line [Measured: 2026-11-13, 264, scratch, one org]. Help says a
  dependency between line-scope steps pairs steps of the same line only; that pairing was not
  measured, and neither was the cross-plan scope.
  Whether a dependent step waits when its predecessor's item isn't on the order (an optional
  product left off) is unmeasured; check it on the first order of each shape before
  relying on it.
  The measured run completed manual steps by setting their state directly; the engine
  accepted it, but that is not a documented route, so don't use it as a recipe for a live
  order.

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
