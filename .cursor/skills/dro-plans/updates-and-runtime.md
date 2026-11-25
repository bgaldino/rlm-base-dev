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
A REST PATCH of the condition JSON to null cleared `ExecuteOnRuleId` and deleted its
generated RuleSet [Measured: 2026-11-17, 264, scratch, one org]. The JSON shape is in
[authoring-and-deployment.md](authoring-and-deployment.md#3-conditions-and-rule-libraries).

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
  freeze scope below. So the flag applies when the flagged step starts. A source rule "no
  changes once step X is done" is met by flagging the step after X, which reaches In
  Progress only when X is complete [inferred from Help]. A build instead flagged each step
  its source rule named, X itself: the step definitions read back with `PointOfNoReturn`
  "Changes Denied" [Measured: 2026-11-18, 264, scratch, one org]; that build didn't read the
  freeze output. By Help's rule, flagging X locks the items when X starts, not when it
  completes [inferred]. Choose by when the source wants the lock to start, and record the
  choice as a decision.
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
  [inferred]. If you flag the step after X, put it on X's technical item; a flag on a step
  of another item locks that item's commercial lines instead [inferred from Help's propagation].
  Where the items come from components of one bundle, a flagged step In Progress denied every
  line of the bundle in the freeze output [Measured: 2026-11-13, 264, scratch, one org], so a
  lock on one item of that bundle alone was not reproducible; other bundles weren't tested.
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

Statements without their own tag are one scratch org, 264, 2026-11-13 [Measured: 2026-11-13,
264, scratch, one org], except the fallout and jeopardy match fields (from describe) and
statements marked as Help's. Statements tagged 2026-11-16 or 2026-11-17 come from later 264
scratch orgs with time-awareness off.
Time-awareness wasn't recorded for the 2026-11-13 runs: no time-awareness setting appeared in the
org's retrieved DRO settings metadata [Measured: 2026-11-13, 264, scratch, one org;
retrieved settings metadata]. Help says it is off by default and can't be turned off once
on [Help: `ind.dro_time_aware_fulfillment_enable`], so a plan that turns it on is outside
these conditions; rerun the amendment and cancel checks there.

- **Future-dated steps (setting on).** A step delayed from the previous step's execution
  by two minutes waited, then started. A step waiting on a scheduled date still waited for
  its dependencies. A step on a decomposed technical item with an offset from the source
  line's start date did not wait
  when the line's service date was a month out and the order was dated today; on two further
  orders with the order date and the line service date a month out (the second also with the
  quote line's start dates), a 10-day offset and a 3-minute offset from that date both
  started at plan creation, and the next-run time carried no offset [Measured: 2026-11-13, 264,
  scratch, one org]. On all three orders the decomposed technical lines had null service and
  end dates [Measured: 2026-11-13, 264, scratch, one org], which may explain it [inferred];
  Help doesn't settle it. Don't promise a start-date offset on a technical item; use a
  previous-step delay (the two-minute delay above waited, then started) or a Custom Date step
  on the commercial line (next item).
- **Custom Date ("not before") steps.** A step can run from a custom date: a date or datetime
  tag in the context definition, mapped to a field, with a positive delay
  [Help: `ind.dro_configure_steps_for_future_execution`]. Each point below is
  [Measured: 2026-11-16, 264, scratch, one org] unless tagged otherwise.
  - `CustomBaseExecutionDate` accepts only a tag of the context DRO has selected. Other tags
    are refused at insert with `INVALID_INPUT: Custom Date field contains an invalid
    Date/DateTime context node name.`
  - A fresh build of this repo selects the standard `SalesTransactionContext__stdctx`, so a tag
    on the repo's extended context needs the Setup switch in
    [authoring-and-deployment.md](authoring-and-deployment.md#3-conditions-and-rule-libraries) first.
  - The date resolves only from an item-level tag on the step's own commercial line. Put the
    step in a group bound to the commercial product.
  - On a decomposed technical item the schedule was ignored with no error, before and after the
    switch; so was a header tag (the standard effective date, or a custom header tag). The step
    ran once its dependencies were done, so a configuration-only test still passes.
  - An unresolved step keeps `NextEarliestRunTime` at plan creation.
  - A resolved step goes Scheduled at 00:00 UTC on the date, plus the delay; in a US time zone
    that is the previous evening.
  - For a date before the line start, map a formula field (start minus N days) as an item DATE
    tag and set no delay: the step went Scheduled at exactly that date.
  - `DelayOf` and `DelayUnit` may be null with `CustomDate`.
  - A Scheduled step whose date had passed stayed Pending behind its open predecessor, and
    started about 2 s after the predecessor completed.
  - Due steps started 9–55 s late. Previous-step delays started late, never early.
  - With the standard context, a Custom Date on the commercial line's standard start-date tag
    did schedule, so start plus a positive delay works; it can't reach a date before the start.
  - One-time lines carry no service date, so a date formula needs a fallback such as
    `BLANKVALUE(ServiceDate, Order.EffectiveDate) - N` [Measured: 2026-11-17, 264, scratch, one org].
  - Two hardware lines feeding one Plan-scope Custom Date step gave one step instance
    [Measured: 2026-11-17, 264, scratch, one org].
    [Open: which line's date a Plan-scope step uses when several lines carry the tag.]
  - [Open: whether a context switch moves steps scheduled before it.] [Open: a start
    scheduled hours or more ahead; only starts due within minutes were observed.]
  - The org's `ExecuteOn` picklist read `SourceLineStartDate`, `CustomDate` and
    `PreviousStepExecutionDate`. The developer guide lists `PreviousStepsStartDate` and
    `SourceLineStartDate` [Dev guide: `sforce_api_objects_fulfillmentstepdefinition`]; use the
    target's describe.
- **Amendment decomposition.** An amendment created a new plan holding the full step set,
  not a delta, and a changed quantity was a full replace. One fulfillment asset's quantity
  after the amendment did not match its line's end quantity; unexplained.
  Help lists a No Change action for lines whose attributes and quantity don't change
  [Help: `ind.dro_fulfillment_order_line_item_actions`],
  but on a bundle amendment two of the unchanged lines came through as an add of 1 (fulfillment
  asset 0 to 1) and a cancel of -1 (asset 1 to 0), while another line of the same order was No
  Change [Measured: 2026-11-13, 264, scratch, one org]. So excluding No Change from a scenario
  does not by itself keep unchanged lines from running steps; a later run measured that by
  another route (see **Lifecycle orders** below). On that
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
  assetizable technical product; a custom scope wasn't measured. An Order-scope item recurs on
  every order (measured below, under **Lifecycle orders**). With one Account-scope instance, every line of
  the account that decomposes to the item feeds it [inferred], so an item that must stay one per
  sold line and be changed by later orders has no measured scope: Order Line Item scope keeps
  one per line but whether a later order acts on each was not measured, and neither was a
  custom scope keyed per source line or asset. Record the choice as a decision and count it
  [inferred]. An Account-scope assetizable item can therefore appear on every later order that
  carries a line decomposing to it, with Amend or No Change, and its group's steps compose
  again unless their conditions skip those actions [inferred from the measured actions]; "no
  new instance" doesn't mean "no line". When a step is skipped by its condition and Skip
  Branch is on, Help skips the branch that depends solely on it
  [Help: `ind.dro_define_conditions_for_a_fulfillment_step_to_run`]; decide that per edge.
  Check the line actions on the first later order.
- **Lifecycle orders (amendments and renewals).** One contract on one org ran a new sale, four
  amendments, a renewal and a price-only amendment [Measured: 2026-11-17, 264, scratch, one org;
  manual steps completed by REST update, see the last item]. Its technical items were Order-scope
  (not assetizable) and Order Line Item–scope (assetizable, Always One).
  - With no conditions, every order recomposed the whole step set.
  - Each Order-scope item came back as Add once per order. It was fed by every line that
    decomposes to it, including lines at No Change with quantity 0.
  - Every unchanged commercial line decomposed to its line-scope item as Amend and ran that
    item's steps, although every scenario excluded No Change.
  - The cause: after the first plan completed, its fulfillment assets read quantity 0, Inactive,
    with no state period. Each later line read start 0, end 1, which Help's rule makes Amend.
  - A `StagedAssetize` step completed but didn't activate those fulfillment assets.
    [Open: whether steps completed by the engine or in the plan UI, or current-dated lines,
    activate them; both differed from this run.]
  - Renew lines decomposed as Amend, never Renew, so a scenario's Renew action never matched.
  - A component cancelled to 0 decomposed as Cancel at quantity 0, with no steps because no
    Cancel scenario existed. On the next order it came back as Add at quantity 0.
  - Step conditions on Sales Transaction Item tags evaluated False on a new sale where they were
    true (action Add, positive quantity). Both a UI-made and an API-made one did. With Skip
    Branch on, they also skipped their direct dependents, but a step one dependency further
    still ran [Measured: 2026-11-17, 264, scratch], so don't count on it removing a whole
    chain. Don't use them to filter lifecycle work.
    [Open: a step condition based on fulfillment line items.]
  - The same tags in decomposition-rule conditions worked on a new sale, an amendment, a
    services-only change and a renewal. They evaluate per source line, and an Order-scope item
    is created when any of its rules is true.
  - Conditions that held there: `LineItemQuantity` GreaterThan 0 on a shipment item;
    `SalesTransactionActionType` Equals `Add` on one-time setup items (a tenant, a project);
    none on an order-review item that must run on every order.
  - On line-scope assetizable items, `LineItemQuantity` NotEquals 0 turned each false line into
    a Cancel line at quantity 0 with no steps.
  - On a second org, a reduction (negative quantity) passed NotEquals 0 and composed an Add
    with its activation steps. With GreaterThan 0 instead, unchanged lines and reductions ran
    none of those items' steps, reaching only the unconditioned order-review item [Measured:
    2026-11-17, 264, scratch, a second org].
  - A deprovision (Cancel) scenario on such items would fire for every false line under
    NotEquals 0 [inferred]. Record each line's action and quantity on the first lifecycle order
    before designing conditions.
- **Fallout and jeopardy rules** match on step type, with an optional integration
  definition, flow definition and error code; this is from the rule objects' describe,
  not a run. They act through two decision tables, `FulfillmentFalloutRules` and
  `Fulfillment_Step_Jeopardy_Rule_Decision_Table`. Help says turning the features on creates
  them [Help: `ind.dro_turn_on_features_to_manage_fallout_and_service_level_agreements`].
  - The settings metadata this repo deploys turns both features on but created neither table;
    an off/on toggle through that metadata didn't either [Measured: 2026-11-16, 264, scratch, one org].
  - Switching each feature off and on in Setup created both tables, Active [Measured:
    2026-11-16, 264, scratch, one org; repeated 2026-11-17 on a second org]. The steps are in
    [authoring-and-deployment.md](authoring-and-deployment.md).
  - Without the tables, a failing auto task went Fatally Failed at once with `Fallout Rule is
    misconfigured: Specify valid name for Data set Link`, 0 retries and no queue. Every manual
    step had a null jeopardy threshold and stayed On Time [Measured: 2026-11-16, 264, scratch, one org].
  - The 2026-11-13 org showed the same symptoms (null thresholds on manual steps, zero retries
    on a failed callout, an empty table lookup). This file called them unexplained; missing
    tables are the likely cause [inferred]. A rule existing doesn't show it applied: verify on
    a live step.

  After the Setup toggle and a refresh of both tables [Measured: 2026-11-16, 264, scratch, one
  org; the retry repeated 2026-11-17 on a second org]:
  - A fallout rule (auto task, its flow, the error code the flow returns, Monotonous, 3
    retries, interval 15) retried the failing step 3 times. Each attempt was due 15 minutes
    after the previous failure, so with scheduler latency they ran about 15–16 minutes apart.
  - After the third retry the step went Fatally Failed with `RetryAttempts` 3 and
    `FalloutQueueId` set to the rule's queue. Its `OwnerId` didn't change.
  - So "in the queue" means `FalloutQueueId`. Help's Fatally Failed Fulfillment Steps list view
    filters it by the Queue column, and the queue needs Fulfillment Step as a supported object
    [Help: `ind.dro_fallout_design_and_management`].
  - The auto task's flow must return `isSuccess` false and `fulfillmentStepErrorCode` on its
    fault path. That contract is in Help's Auto Task article `ind.dro_auto_task`, read live; the
    snapshot lacks it. With no matching rule, DRO sets the step Fatally Failed without retrying
    [Help: `ind.dro_fallout_design_and_management`].
  - Help says DRO retries only errors a flow returns through an Auto Task Fault Path and
    does not retry unhandled Apex exceptions
    [Help: `ind.dro_fallout_design_and_management`]. How DRO treats an autolaunched flow
    that ends normally having done nothing is not documented in the snapshot: it reads as a
    success [inferred; live check pending]. A decision with no connector on its Default
    Outcome ends the interview normally, with no error [Flow behavior, not run here].
    A Get Records lookup that finds nothing is not a fault either [Flow behavior, not run here], so a fault connector alone
    cannot report it: the flow tests each lookup result explicitly. The two collection checks use `IsNull`, which assumes an empty result leaves the collection null rather than empty [inferred; not run].
  - `RLM_Assetize_Order_DRO_Fulfillment` reports failure through three output variables,
    `isSuccess` (defaults true), `fulfillmentStepErrorCode` and `fulfillmentStepErrorMessage`.
    Whether DRO reads or surfaces them is not measured. Three failure assignments set
    `isSuccess` false: `Check_Source_Data_Type`'s Default Outcome (a source type that
    matches none of the four rules) sets `RLM_ASSETIZE_UNRESOLVED_SOURCE_TYPE`; a "not found"
    outcome after each of the six Get Records lookups (the `OrderItems` collection path uses none) (`Get_Order_Product`,
    `Get_Fulfillment_Order_Item`, `Get_Fulfillment_Order_Items`, `Get_Source_Relationship`,
    `Get_FOP_Source`, `Get_Order_Product_and_Parent_Id`) sets `RLM_ASSETIZE_SOURCE_NOT_FOUND`;
    a fault connector from each of the 5 action calls and 6 lookups sets `RLM_ASSETIZE_FAULT`
    with the fault text (`$Flow.FaultMessage`). The lookups set
    `assignNullValuesIfNoRecordsFound` true, intended to clear the output on a miss rather than
    leave the previous loop iteration's record; whether that flag has any effect on a lookup
    that stores its output automatically is not measured [inferred; not run], so the
    flow does not rely on it: the explicit null check after each lookup is what fails. A source relationship whose
    `SourceLineItemId` is null counts as not found. The four recognized source types are
    unchanged. Known gaps, kept as live checks: the `OrderItems` collection path has no lookup, so even an all-missing `recordIds` relies on
    the action faulting (`RLM_ASSETIZE_FAULT`) [inferred; not run]; a fulfillment-line `recordIds` collection where only some ids
    are missing still assetizes the ones found (the lookup is null only when all miss; the flow
    cannot compare collection sizes); the `exists` skip above also ends successfully for a
    top-level line it does not recognize; the output of `createOrUpdateAssetFromOrderItem` is
    stored but not read, so per-item errors it returns instead of throwing would not fail the
    step; the two collection paths do not filter component lines [inferred; not run].
    Fault paths catch element errors, not governor-limit errors (`Get_FOP_Source`
    runs one query per loop iteration), which end the interview and do not reach the fault
    connector [Flow behavior; not run here].
  - What `RLM_DetermineDROSourceType` returns, per its Apex and `RLM_DetermineDROSourceTypeTest`:
    one output per input, in input order, so a batch of several interviews gets one result
    each. A non-blank `recordId` decides, even a malformed one; otherwise the first `recordIds`
    element decides and the type name gets an `s` suffix. A missing or malformed deciding id
    (both inputs null, an empty `recordIds`, or a non-Id string) gives a blank output instead
    of an exception; one bad input does not affect the rest of the batch. A null or blank first
    `recordIds` element also gives a blank output (read from the Apex; no test covers it).
  - In the flow, a blank output or any other object name (an Order id gives `Order`, or
    `Orders` from `recordIds`) matches none of `Check_Source_Data_Type`'s four rules, so it takes
    the Default Outcome and `RLM_ASSETIZE_UNRESOLVED_SOURCE_TYPE` [inferred from the flow and
    the class; not run as a flow]. An exception the class does not catch (other than a governor-limit error) would reach the flow as
    a fault on `Determine_DRO_Source_Type` and take `RLM_ASSETIZE_FAULT` [inferred; not run].
  - Two connector-less ends read as intended skips, not failures [inferred from the flow's
    structure]:
    `Has_Parent_Id`'s `Parent_Exists` outcome (a component line is assetized through its
    parent) and the `exists` decision's Default Outcome (the source line was found but is not
    in `Not_Components`; components are removed earlier by `Collection_Filter_1`, so this is
    reached when a top-level line has no `RelatedOrderItemId`, which `Has_Value` tests
    with `WasSet`; whether `WasSet` is false for a queried null field is not established, and
    if it is, a new-sale top-level line skips assetization, so check it live [inferred; not run]). A line that is missing altogether no
    longer reaches `exists`; it fails with `RLM_ASSETIZE_SOURCE_NOT_FOUND`. The step's status, error text and retries for these paths are not yet
    measured [inferred; live check pending].
  - Not yet checked on a live org:
    - Can an AutoTask step launch a flow whose status is Draft, and what does DRO do? The
      flow ships `Draft` in source and no build step activates it (a generic `manage_flows`
      activation could, but none is configured for it). So none of these paths has any
      runtime effect until the flow is activated and a failing step is run live. In this repo only the `mfg-dro` `Convert Order to Asset` step binds it,
      and `mfg-dro` is not wired into `cumulusci.yml`. The `qb-dro` steps all have a blank
      flow name, so no `qb-dro` step binds it; `qb-dro` jeopardy rule `000000002`
      (`FulfillmentStepJeopardyRule.csv`) names it, as does `mfg-dro`'s (`FulfillmentStepJeopardyRule.csv` line 3). What that jeopardy reference does on a
      `qb-dro` build is not measured.
    - For a failed step, read `ExecutionMessage` and `State` on the `FulfillmentStep`, and
      read Help's Auto Task article `ind.dro_auto_task` live for the message output
      variable name it expects, and check whether DRO reads or shows
      `fulfillmentStepErrorMessage` (unverified name).
    - Whether any fallout rule matches these codes. No `qb-dro` step binds the flow, so
      `qb-dro` rule `000000002` (AutoTask, any flow, any code, 3 immediate retries) does not
      apply to it in this repo. `mfg-dro` binds it (`FulfillmentStepDefinition.csv` line 9) but
      its only fallout rule is for `Callout` steps (`FulfillmentFalloutRule.csv`), so the
      step has no matching rule. Help says no matching rule means Fatally Failed without
      retry, and a fresh build creates no fallout decision tables (above), so no retry is
      expected [inferred; not measured]. A no-retry rule for the codes is not added until
      rule matching is measured.
  - A jeopardy rule with its own flow definition matched a manual task through the step's
    `FlowDefinitionName`. The step showed the rule's threshold and a planned completion of
    start plus the estimated duration. The per-flow rule applied although blank-flow manual
    rules also matched.
  - A rule of 4 minutes with a 2-minute threshold took its step from On Time to In Jeopardy at
    start + 2 minutes, then Overdue at start + 4 minutes. Nobody was notified of either.
  - A manual step with no flow name got one of the two blank-flow manual-task rules the repo's
    `qb-dro` plan loads (1 Day / 20 Hours and 1 Day / 12 Hours): the 12-hour one. Give each
    step its own rule rather than rely on overlapping blank rules.
  - A manual task's flow name served only as the rule's key here; a no-op flow per step is
    enough [inferred].

  For planning: a jeopardy rule targets callouts through an integration
  definition and manual or auto tasks through a flow definition, and a blank field applies
  it to every step of that kind [Help: `ind.dro_configure_fulfillment_step_jeopardy_rules`,
  `ind.dro_sla_jeopardy_administration`]; fallout rules cover callouts and auto tasks, with
  retries and a queue for fatally failed steps [Help: `ind.dro_configure_fallout_rules`].
  A step definition carries a `FlowDefinitionName` field whatever its type, empty on every
  manual task in the measured org [Measured: 2026-11-13, 264, scratch, one org; describe and
  query]; a jeopardy rule does match a manual task through it (above). Help names no rule
  for Milestone steps, and a Milestone rule wasn't tested. A separate window or queue per
  step needs its own flow or integration definition per step [inferred]. You set the estimated duration and
  threshold on the jeopardy rule, and the threshold counts back from the duration [Help:
  `ind.dro_configure_fulfillment_step_jeopardy_rules`]. A rule with a blank flow
  definition applies to every manual and auto task, so two manual steps with different windows
  need a flow definition each, or share a window [inferred]. Where a blank-flow rule and a
  per-flow rule both matched, the per-flow rule applied (above). Help describes a
  jeopardy status and notification, names no setting for who is notified, and has no
  reassignment of a late step [inferred from Help's silence]. After editing a fallout or
  jeopardy rule, refresh its decision table [Help: `ind.dro_configure_fallout_rules`,
  `ind.dro_configure_fulfillment_step_jeopardy_rules`]; the steps are in
  [authoring-and-deployment.md](authoring-and-deployment.md).
- **Cancel of a non-assetizable technical line.** Cancelling the bundle's root asset decomposed the copy
  product's line as an Add of quantity 0, not a Cancel, and its Add steps were still created and started; no
  fulfillment asset was created or changed for it, while the assetizable lines decomposed as
  Cancel [Measured: 2026-11-13, 264, scratch, one org]. Design Add steps to tolerate a zero
  quantity [inferred from one run]. Order-scope items can't be assetized [Help:
  `ind.dro_decomposition_scope`], and they composed as Add at quantity 0 on lifecycle orders
  whose source lines were unchanged [Measured: 2026-11-17, 264, scratch, one org]. A step
  that must run when the item is cancelled needs an assetizable item with a Cancel action, or a
  condition on quantity 0 [inferred].
- **Dependency across order items.** A plan-scope step whose dependency was set at line scope
  waited for every instance across the order items, not one line [Measured: 2026-11-13, 264, scratch, one org]. Help says a
  dependency between line-scope steps pairs steps of the same line only; that pairing was not
  measured, and neither was the cross-plan scope.
  When a predecessor's item wasn't on the order (its decomposition condition was false), a step
  that depended on it at Plan scope ran without waiting: the edge was dropped [Measured:
  2026-11-17, 264, scratch, one org]. An optional product left off should behave the same
  [inferred]; check it on the first order of each shape before relying on it.
- **Completing manual steps.** The measured runs completed manual steps by a REST update of
  the step record's state; the engine accepted it on scratch orgs [Measured: 2026-11-13,
  2026-11-16 and 2026-11-17, 264, scratch]. It is not a documented route: use it on a scratch
  org only, never on a live order, and complete live steps in the plan UI.
  One update to Completed, sent before the engine had created the step's task, left the step
  Fatally Failed ("State not supported: Completed"); recovery wasn't measured
  [Open: which record or state shows the task exists]. Setting the
  step's `NextEarliestRunTime` to now released a Custom Date step early; that is undocumented too, so scratch orgs only [Measured:
  2026-11-17, 264, scratch].
  Plans completed this way left their line-scope fulfillment assets inactive (see
  **Lifecycle orders**), so a test that reads fulfillment-asset state needs steps completed by
  the engine or in the plan UI [inferred].
  Nothing reacts to a step's completion: a describe of `FulfillmentStep` returns `triggerable`
  false [Measured: 2026-11-18, 264, scratch]. Put follow-on work in a later step, or leave it to a person.

## Tenant Provisioning Callout Step (qb-dro)

`qb-dro` ships the Callout step `Stage New Tenant for Provisioning - Platform`
(`RLM_DFOTenantProvisioningCallout`, posting to `callout:RLM/services/apexrest/QuantumBitTenantEnvironment/createNewTenant`).
This repo ships neither the `RLM` named credential nor the REST resource. On a fresh 264 `dro` build
[Measured: 2026-11-25, 264, scratch, one org]:
- The step is wired and ran when the order was activated (its start time equalled plan creation) on new-sale orders
  containing `QB-API-MGMT` (decomposition rule to `QB-DRO-APIPLAT`, scenario `API Platform to Provisioning`, step group
  `Platform`). Neither the rule nor the step has a condition. `QB-API` and `QB-API-FLEX` orders did not reach it. Amend,
  renew and cancel orders (the scenario lists them) were not run. That the step ran synchronously in the activation
  transaction is [inferred].
- It failed on its first attempt, straight away. The debug log shows `CALLOUT_REQUEST` to the `callout:RLM/...` endpoint, then
  `System.CalloutException: ... the named credential "RLM" might not exist`. The step is `FatallyFailed` with
  `RetryAttempts` 0. The class returns `isSuccess=false` (code 503) on that path [inferred from the class]; the log does
  not show the returned value. The 0 retries are attributed to the missing decision tables below [inferred], meaning the shipped Callout fallout
  rules (3 retries and 1 retry, Immediate) were not applied [inferred]; their effect once the tables exist was not
  measured.
- It stalls the billing chain. Receive Key + Assign to Asset and Provision Licensing/Features depend on it;
  Provision Licensing/Features gates Initiate Billing (and Activate Tokens, not on these plans), which gates Post Invoice,
  which gates Receive Payment. All stayed `Pending` and the plan stayed `InProgress`.
- `ExecutionMessage` showed `Fallout Rule is misconfigured: Specify valid name for Data set Link`, not the exception text,
  on a build with no fallout or jeopardy decision tables (see **Fallout and jeopardy rules** above); the tables are the
  likely cause [inferred]. The exception text was visible only in the debug log. Whether it surfaces with the tables
  present was not measured. The measured failure is the `CalloutException` path; whether the non-2xx branch of the class
  (todo 381) also ends the step `FatallyFailed` once the tables exist was not measured.
- Fulfillment orders stayed `Draft` for every order on that build, including an order whose plan had no failed step, so a
  Draft fulfillment order is not evidence about a step. Why they did not leave Draft was not measured.
- An earlier check concluded the step was "not wired" from Draft fulfillment orders and zero `FlowOrchestrationInstance`
  records. Both signals are uninformative here (see **Verify a DRO Step on a Fresh Build**, below).

Open decision (todo 419, item 3): ship a credential and target, point the step at a mock provider, or
remove or condition the step. This section records behaviour, not a fix.

## Verify a DRO Step on a Fresh Build

1. Pick the order by decomposition, not by guess. Query `ProductFulfillmentDecompRule` (source to destination product,
   and `SourceProductClassificationId`, since some rules match a classification) and `ProductFulfillmentScenario`
   (`FulfillmentStepDefnGroupId`, `ProductId`, `ProductClassificationId`), then the step definitions in that
   group (`FulfillmentStepDefinition.StepDefinitionGroupId`, and `ExecuteOnConditionData`/`ExecuteOnRuleId` for a condition).
   Choose an order whose product decomposes to a product with a scenario in the step's group.
2. Activate the order. For QB, `scripts/build_quote_to_asset.py --org <sf_alias> --accounts "<one account>" --sku <SKU> --start <today> --skip-usage-verify`
   builds quote, order and activation headlessly (its default is two accounts and a 2026-06-01 start). A direct
   `OrderItem` create could not set `ProductSellingModelId` [Measured: 2026-11-25, 264, scratch, one org].
3. Read the result by the order id, as `FulfillmentPlan.SourceIdentifier` (`SourceType` was `StandardOrder` there; a plan
   sourced from order items would carry an OrderItem id [inferred from `RLM_AccountUtilities`, which queries both
   source types], so then use `SourceIdentifier IN ('<orderId>', <orderItemIds>)`):

   ```bash
   sf data query --target-org "<sf_alias>" --query "SELECT Id, Name, State, SourceType FROM FulfillmentPlan WHERE SourceIdentifier = '<orderId>'"
   sf data query --target-org "<sf_alias>" --query "SELECT Name, State, StepType, ExecutionMessage, RetryAttempts, NextEarliestRunTime FROM FulfillmentStep WHERE FulfillmentPlan.SourceIdentifier = '<orderId>'"
   ```

4. Do not use fulfillment-order `Status` (it stayed `Draft` regardless of plan state) or
   `FlowOrchestrationInstance` (its count stayed 0 for plans that ran; the plans are `FulfillmentPlan`/`FulfillmentStep` records [inferred])
   as the signal [Measured: 2026-11-25, 264, scratch, one org].
   In the measured run the step's `ActualStartDate` equalled the plan's `CreatedDate` and no non-test `AsyncApexJob`
   existed [Measured: 2026-11-25, 264, scratch, one org]; that it ran at activation rather than from a queued job is
   [inferred], since DRO's own async work need not appear as an `AsyncApexJob`.
5. For a Callout or Auto Task step whose `ExecutionMessage` is the fallout `Data set Link` text, the underlying error is
   not in the record. Check that the fallout and jeopardy decision tables exist, and read the real error from a debug
   log (trace flag on the activating user).

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
