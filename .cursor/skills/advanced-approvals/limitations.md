# Limitations and Open Questions

Read this before relying on Smart Approvals, Preview, email, delegation or Slack, and
before telling anyone how approvals behave where the docs are unclear. Parent:
[advanced-approvals](SKILL.md).

## Setup

- **Settings:** Setup → Approval Settings: Use Flow Approval Process, Use Advanced
  Approvals, the email options, Use Advanced Approval Delegation, Use Dynamic Approval
  Notifications [Help: `ind.approvals_set_up_advanced_approvals`], and the Slack toggles
  [Help: `ind.approvals_turn_on_slack_notifs`]. Email replies are a separate setting, under
  Process Automation Settings [Help: `ind.approvals_set_up_advanced_approvals`].
- **Repo coverage:** the repo ships no settings metadata for these toggles. On a
  QuantumBit build the shipped approval ran end to end with whatever the scratch org
  defaults to [Measured: 2026-11-10, 264].
- **Personas:**
    - Designer: Manage Flow, Approval Designer, Read on Approval Submission.
    - Submitter, reviewer, delegate: Run Flows plus Read on Approval Submission.
    - Administrator: also Approval Admin.

  [Help: `ind.approvals_personas`]. One quote walkthrough says approving needs Approval
  Admin [Help: `ind.approvals_use_advanced_approvals_in_a_quote`]; the personas table says
  otherwise. Test with a reviewer who has no admin permissions.
- **Supported objects:** the docs publish no list of supported objects
  [Help: `ind.approvals_objects_considerations`]. Quotes, orders and custom objects are named
  [Help: `ind.approvals_advanced_approvals`], and contracts have their own setup
  [Help: `ind.sf_contracts_aa_configure`].
- **Sandboxes:** run Match Production License after a release
  [Help: `ind.approvals_environment_setup`].

## Smart Approvals (auto-approval on resubmission)

A step is eligible only if all of these hold [Help: `ind.approvals_smart_approval_limitations`,
`ind.approvals_smart_approvals`, `ind.approvals_smart_or_rule_based_approvals`]:
- conditions are Number or Text, with at most 30 per step and no NOT operator (the
  traced allow-list is wider, see below);
- no evaluation-flow entry or exit condition (that makes the whole flow ineligible);
- no Decision before a stage whose steps start "when the stage starts";
- the earlier submission was Rejected or Recalled, reached at least 2 steps, and had at
  least 1 approved;
- the active flow version hasn't changed since;
- no work item was reassigned during the original submission.

After a full approval, the next submission is a new request, not a resubmission.

The Help limitations article says Number or Text only. The allow-list traced in the
platform source is wider (datatypes and operators below); treat Number and Text as the
documented-safe types and the rest as source-derived, not measured. The 30-condition limit
and the "at least 2 steps reached" and "no reassigned work item" rules are Help-sourced and
were not seen in the traced code.

How it decides [Platform behaviour, traced]:
- A step runs Smart Approval only if its Use Smart Approval input is true and the
  submission is eligible. The earlier submission for the same record and the same flow
  version is the basis only if it was Recalled or Rejected; a new flow version means no basis.
- The basis item is the newest Approved item for that step in the basis submission. If its
  reviewer is inactive, the step goes to manual review. The current assignee is not
  examined: if Smart Approval approves the step, the new item is created already reviewed (`IsAutoReviewed` true), under the
  earlier reviewer, with a system comment.
- Only a step whose flow resolves a condition object is
  evaluated; what makes a step have one was not verified (likely, but not shown, a step
  with entry conditions). Each condition is compared by position
  with its earlier-run counterpart, using the single value the flow resolved for it (no
  totals or per-line comparison); results combine through the step's criteria logic.
- Datatypes: Boolean, Currency, Date, Date/Time, Time, Number, Picklist, Multi-select
  picklist, Text. Operators: less than, greater than, their or-equal forms, equals, not
  equal, starts with, ends with, contains, is null, is blank. Any other operator or type
  (for example In, Not In, Is Empty, Was Set, Is Changed), a NOT in the logic, or an
  evaluation error sends the step to manual review. There is no separate Percent or
  roll-up type.
- Range test as coded: each condition becomes a lower and upper bound from its left and
  right sides (for less than, less or equal, equals, not equal and the text operators lower = left,
  upper = right; for greater than and greater or equal, lower = right, upper = left; is null and is blank use the left side for
  both). A condition passes only when the earlier approved range contains the new one and its
  evaluation succeeded; for Text, Picklist and Multi-select picklist both bounds must match,
  ignoring case. The step's criteria logic combines the results [Platform behaviour,
  traced]. The results match the left side being the evaluated value, so the new range must sit inside the
  earlier approved one [Measured: 2026-11-12, 264, scratch]. With "value > threshold", a
  resubmission auto-approves when the new value is lower than or equal to the approved value
  and goes to review when it is higher; with "value < limit", it auto-approves when the new
  value is higher or equal and goes to review when it is lower. Equal auto-approved in both runs.
  Limits of the measurement: Number conditions only; an admin acted on every item; Smart
  Approval was on through the shipped flow's step input, and the Setup page was not read.
  Other types and operators are still unmeasured.
- A step Smart Approval auto-approves completes as Approved, so a later step reading its
  outcome sees Approved: the auto-reviewed item posts an Approve decision [Platform behaviour, traced]. A later step whose entry
  condition reads the earlier step's decision = Approve started after the earlier step was
  auto-approved [Measured: 2026-11-12, 264, scratch]. Conditions listed in the step's Smart Approval Skip Conditions are left out of the
  Smart Approval comparison [Help: `ind.approvals_turn_on_smart_approvals`]: each counts as
  passing under AND logic and as failing under OR logic [Platform behaviour, traced]. The
  Help FAQ (`ind.sf_contracts_aa_faq`) says listing a condition there forces a review; the
  trace contradicts that for AND logic, where a skipped condition can only help the step
  auto-approve. Under OR the step auto-approves only if a condition that is not skipped
  passes, so skipping turns an auto-approval into a review only when every condition that
  would have passed is skipped; with every condition skipped the step always goes to
  review. Custom
  criteria logic is not covered by the trace. To force a review, turn Use Smart Approval
  off for the step.

## Preview

- Works only with the Autolaunched Flow Approval Process (No Trigger) type.
- Skips steps whose entry conditions depend on asynchronous evaluations, such as subflows
  in background steps.
- Treats every referenced step as a required dependency, without telling AND from OR.
- Doesn't show dependencies across chains, and fails on approvers of type Resource.

[Help: `ind.approvals_preview_feature_limitations`]. A real submission is the test.

To see the values a background data flow passes, run that flow on its own
([actions-and-objects.md](actions-and-objects.md) → Read the approval data)
[Measured: 2026-11-12, 264], rather than the Help's workaround of mock output values, which
edits the flow [Repo: `docs/features/composable-quote-approvals.md`].

## Email and alerts

- Eight notification reasons. One template per flow, step and reason
  [Help: `ind.approvals_email_templates`, `ind.approvals_email_notification_behavior`].
- The template must be Available for Use, and its entity must match the record.
- Deselect "Don't send approver notifications" on the step to get emails.
- Queue emails go to at most 1,000 recipients.
- The repo's alert rows go in `datasets/sfdmu/qb/en-US/qb-approvals` (`sfdmu-data-plans`).

## Delegation, Slack, execution

- **Delegation:** one active delegation per reviewer; delegations can't overlap and
  can't be deleted (end them instead); delegates get no Slack notifications
  [Help: `ind.approvals_delegation_considerations`].
- **Errored runs:** usually two steps locking the same record, or a work-item screen that
  failed to render. Check Paused and Failed Interviews
  [Help: `ind.approvals_approval_process_execution`].
- **Concurrent reviews:** when two group members review at once, the first wins and the
  second is rejected.

## Open questions (not settled by the docs or a measured run)

- Where "First Response" vs "All Must Approve" is configured for a group or queue step.
- Whether approving and recalling need Approval Admin, or only Run Flows plus Read. For
  recall, the dev guide requires Approval Admin plus being the submitter, while the Help
  personas table gives submitters Run Flows plus Read. For approving, only the Help quote
  walkthrough requires Approval Admin. Measured runs used an admin holding Approval Admin
  (through its profile and `RLM_CLM`), which the personas table allows to review any work item, so they don't
  settle what an ordinary reviewer needs.
- Which Approval Settings a fresh scratch org has on, and whether Metadata API can set them.
- Whether a Resource-type approver works at runtime, and whether there is a
  manager-hierarchy approver.
- Whether a roll-up summary or Percent condition passes the Smart Approvals type check
  [inferred: the flow resolves it to Number or Currency; not verified].
- Whether `ApprovalDelegation` appears once delegation is turned on.
- Whether `ActionInput__CanUseSmartApproval` is the Use Smart Approval setting; the docs don't
  name the input. With it `false` on
  every step, a resubmission after a rejection at the second step (the first approved)
  opened a new first-step work item, `Assigned`, `IsEligibleForSmartApproval` false
  [Measured: 2026-11-12, 264], as expected if it is the Use Smart Approval setting. With it
  `true` (as the shipped steps set it), resubmissions auto-approved a step that was approved in the earlier submission and whose
  range still held, and the step rejected there went to review again
  [Measured: 2026-11-12, 264, scratch]; the Approval Settings page was not read.
  Traced: Smart Approval is switched on per approval step by its Use Smart Approval input
  (stored on the work item as Eligible for Smart Approval). Of the eligibility rules above, the
  trace confirms two: Smart Approval does not apply when the flow has a Decision path leading to
  an approval step without entry conditions, or an evaluation-flow entry or exit determination
  [Platform behaviour, traced; Help: `ind.approvals_smart_approval_limitations`]. Help's
  "Turn On Smart Approvals" step is not mapped to this input: not established whether an
  organization-wide setting also gates it.
- Whether a line's margin values reflect a header discount that `DiscountDistributionService`
  spreads to lines; the shipped procedure computes margin before the header discount steps.
- `ApprovalWorkItem` standard fields and sObject `update()`: the Help says they can't be
  updated [Help: `ind.approvals_design_build_activation`]; the dev guide lists `update()` and
  marks `ApprovalChainName` and the Smart Approval fields updatable
  [Dev guide: `adv_approvals_capture_fields_on_approvalworkitem`]. A user or Apex update of
  the standard fields (status, assignee, reviewer, comments, chain name, Smart Approval fields
  and the rest) is refused with an insufficient-access or read-only error; custom fields you
  add to the object can be updated. Approve, reject and reassign through the approval actions
  instead [Platform behaviour, traced]. Not run live.
- How to tell a round's bulk line discount from an individual line override. No documented
  field or flag records which edit set a line's discount, and the repo ships none. A mapped line
  field written with the discount by an API applier survived a deep clone, and a header custom
  field reset on it [Measured: 2026-11-12, 264, scratch, one org]
  ([matrix-modeling.md](matrix-modeling.md)); whether such a marker stays
  accurate after a rep's later edit, or when set by a bulk edit or a flow, is unmeasured. Also unmeasured: whether a discount entered on a group row stays
  on the group's `Discount` field or is written to each line's `Discount`, which the shipped
  level bands.
- On an amendment quote: which other records could give the contract value after the change, for a
  threshold that must read it (the quote's own totals carry the change); and whether the
  shipped discount level fires on amendment lines, which depends on what their `Discount`
  field carries. A contract value summed from prior activated orders by the quote's account
  worked [Measured: 2026-11-12, 264, scratch, one org] ([matrix-modeling.md](matrix-modeling.md));
  other sources are untried.
