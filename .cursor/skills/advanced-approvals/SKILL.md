---
name: advanced-approvals
description: >-
  Model, build, run and verify Revenue Cloud Advanced Approvals: approval
  workflows on Flow Orchestration, serial and parallel chains, an approval matrix
  with cumulative levels, conditions on quote and line values, submission,
  review, recall, rejection and resubmission, Smart Approvals, notifications, and
  the repo's shipped quote approval (RLM_Quote_Smart_Approval, the approval-flags
  pricing overlay, qb-approvals). Use when adding an approval dimension, mapping
  a customer's sign-off matrix, debugging a submission, or testing approvals
  headlessly. Pricing-side level calculation: pricing-procedures and
  expression-sets.
---

# Advanced Approvals — Modeling, Building and Verifying Approvals

Use this skill to turn a sign-off policy ("over 15% needs a Director; below 50% margin
needs a Director; over $8M needs the VP") into Revenue Cloud Advanced Approvals. It also
covers running and checking a submission, and extending the approval workflow this repo
already ships. Claims are tagged: `[Help: <article>]` and `[Dev guide: <article>]` from
`docs/salesforce/264/`, `[Repo: <path>]`, and `[Measured: <date>, 264]` for a live run on a
scratch org built by this repo.

## Quick Rules

1. **Advanced Approvals runs on Flow Orchestration**, so Flow Orchestration's limits apply
   [Help: `ind.approvals_advanced_approvals`]. An approval workflow is an orchestration flow
   of stages and steps: background steps run flows, and approval steps assign work items
   [Help: `ind.approvals_example_configure_an_approval_workflow`].
2. **Reduce every condition to a single flow-resolved value of a supported type (Number or
   Text is the documented-supported type) before the approval stage.**
   - Conditions can test a background step's outputs, another step's outputs (the shipped
     Director step reads `Manager_Approver.Outputs.approvalDecision`) and flow formulas. Line
     values aren't one of those, so aggregate them (a maximum level, a count of lines breaking
     a guard) into quote-level numbers in a background step or a roll-up first.
   - Smart Approvals: the Help says Number or Text only and no NOT operator
     [Help: `ind.approvals_smart_approval_limitations`]. The traced allow-list is wider
     (datatypes and operators in [limitations.md](limitations.md) → Smart Approvals);
     treat Number and Text as the documented-safe types.
3. **Model "each level also needs the levels below" as one serial chain.** Step N starts
   when the level is at least N and step N−1 was approved. Give each independent
   dimension its own chain name so it runs in parallel. The repo ships this
   [Repo: `docs/features/composable-quote-approvals.md`].
4. **Give every stage with conditional steps a custom exit condition:** "(completed OR not
   triggered)" per step, plus a rejection shortcut. Otherwise the stage waits forever for
   steps that never started [Help: `ind.approvals_use_the_stage_exit_condition`].
5. **Submit by starting the approval flow.** The approval invocable actions are cancel,
   override, reassign, recall, review and `getPreviousRelaRecDetails`; none submits
   [Dev guide: `advanced_approvals_invocable_actions_parent`].
    - The repo uses the invocable Apex `RLM_AA_Submit_Approval`.
    - Review, override, reassign, recall and cancel have standard actions
      ([actions-and-objects.md](actions-and-objects.md)).
    - The Help says standard fields on approval objects can't be written through the sObject
      APIs [Help: `ind.approvals_design_build_activation`], but the dev guide lists `update()`
      on `ApprovalWorkItem` for a few fields
      [Dev guide: `adv_approvals_capture_fields_on_approvalworkitem`]. A direct update of the
      standard fields is refused; custom fields you add can be updated [Platform behaviour,
      traced, not run live]. Use the actions ([limitations.md](limitations.md)).
6. **Extend the shipped workflow rather than adding a second one.** Follow the nine-step
   recipe in `docs/features/composable-quote-approvals.md` → Adding A New Approval Dimension;
   it is the one list to keep current. The two steps most often missed:
    - the `Requires_Approval` decision must test the new step's trigger, or a quote that
      triggers only the new dimension skips approval and goes straight to Approved;
    - the stage's `exitConditionLogic` needs a `(completed OR not triggered)` clause for
      the new step, or the stage can exit before it runs.
7. **Reprice before you submit.** Line levels are written by the pricing procedure on each
   reprice; there is no staleness guard [Repo: `datasets/expression_set_overlays/README.md`].
8. **Verify with a real submission, not only Preview.** Preview doesn't show steps whose entry
   conditions depend on asynchronous evaluations, such as a background step's subflow, and
   doesn't tell AND from OR [Help: `ind.approvals_preview_feature_limitations`].
   Check work items, statuses and the quote status after each action
   ([actions-and-objects.md](actions-and-objects.md) → headless test).

## DO NOT

- **DO NOT** let reps edit a stored approval level. The repo makes
  `RLM_Approval_Level_Calc__c` read-only, because a rep who could edit it could lower it
  before submitting [Repo: `docs/references/revenue-cloud-permissions.md`].
- **DO NOT** put a Decision before a stage whose steps start "when the stage starts" if you
  want Smart Approvals. Use explicit entry conditions instead. Avoid evaluation-flow
  conditions too; both make the flow ineligible [Help: `ind.approvals_smart_approval_limitations`].
- **DO NOT** hard-code user, group or queue IDs in an orchestration you package or deploy
  between orgs [Help: `ind.approvals_add_an_approval_button_for_sales_reps`]. Assign by group
  name, as the repo does.
- **DO NOT** expect to choose the submitter. In one run that started the flow over REST with
  another user's ID in the `submitter` input, `SubmittedById` was still the running user
  [Measured: 2026-11-10, 264]; the repo's Apex bridge always passes the running user.
  `submitter` is a predefined variable of the Autolaunched Flow Approval Process type
  [Help: `ind.approvals_example_configure_an_approval_workflow`]; the shipped flow doesn't
  read it. (In an *autolaunched* flow started by a quick action,
  `$User` is the Automated Process User [Help: `ind.approvals_add_an_approval_button_for_sales_reps`];
  the repo's quick action launches a screen flow, which runs as the user.)
- **DO NOT** confuse "dynamic approvals" with dynamic routing. In the docs it means
  AI-written notification summaries [Help: `ind.approvals_turn_on_dynamic_approvals`].
- **DO NOT** confuse this feature with the legacy Salesforce CPQ "Advanced Approvals"
  managed package.

## Entry Conditions

| Situation | Use |
|---|---|
| Add an approval dimension to the shipped quote approval (margin, deal size, quote validity) | This skill → [matrix-modeling.md](matrix-modeling.md), then `docs/features/composable-quote-approvals.md` |
| Map a customer's sign-off matrix onto approvals | This skill → [matrix-modeling.md](matrix-modeling.md) |
| Approvals across negotiation rounds (each round a cloned quote) | `quote-negotiation-rounds` |
| Submit, approve, reject, recall or inspect a submission; test headlessly | This skill → [actions-and-objects.md](actions-and-objects.md) |
| Smart Approvals, preview, email, delegation limits; what's still unknown | This skill → [limitations.md](limitations.md) |
| Change how the line approval level is computed | `pricing-procedures` and `expression-sets` (the `approval_flags.json` overlay) |
| Map a field into the pricing context | `context-service` (`datasets/context_plans/Approvals`) |
| Load or change alert definitions | `sfdmu-data-plans` (`datasets/sfdmu/qb/en-US/qb-approvals`) |
| Approval objects and fields | `revenue-cloud-data-model` → `domains/approvals.md` |

## What the repo ships

With the `quantumbit` and `approvals` flags on, `prepare_rlm_org` builds a working quote
approval (the alert definitions also need `qb`; all three default to true) [Repo: `cumulusci.yml`, `docs/features/composable-quote-approvals.md`].
This table is a snapshot as of 264 and will age. To see what ships now, run
`grep -n -i approv cumulusci.yml` for the tasks, flows and flags, and
`grep -rl "<processType>ApprovalWorkflow" unpackaged` for the approval orchestrations:

| Piece | What it does |
|---|---|
| `unpackaged/post_approvals` (`deploy_post_approvals`) | Fields (`Quote.RLM_Approval_Level__c`, a MAX roll-up of `QuoteLineItem.RLM_Approval_Level_Calc__c`; `RLM_Approval__c` flag; `RLM_Approval_Status__c`; `RLM_Payment_Terms__c`), the flows, the `RLM_Submit_for_Approval` quick action, the Apex bridge, the `RLM_Approvals` permission set |
| `datasets/expression_set_overlays/approval_flags.json` (`apply_approval_flags_overlay`) | Sets each line's level from its discount on every reprice: 15% to under 25% → 1 Manager, 25% to under 35% → 2 Director, 35% to under 100% → 3 VP |
| `datasets/context_plans/Approvals` (`apply_context_approvals`) | Maps the two line fields into `RLM_SalesTransactionContext` so pricing can write them |
| `RLM_Quote_Smart_Approval` (orchestration) | Background data step → approval stage with a Discount chain (Manager → Director → VP, cumulative) and a Finance chain (payment terms other than Net 30) → Approved or Rejected stage. Level 0 with Net 30 skips approval |
| `force-app/main/default/groups/` | The `Manager`, `Director` and `VP` public groups the steps assign to, shipped with no members; no task adds members |
| `RLM_AA_Reset_Quote_Status` (record-triggered on `ApprovalSubmission`) | Sets the quote's `RLM_Approval_Status__c` to `Recalled` on recall and clears it on cancel. The shipped orchestration has no recall path and nothing that runs on cancel |
| `datasets/sfdmu/qb/en-US/qb-approvals` + `create_approval_email_templates` | Lightning email templates and the alert definitions that link them to steps |

The approval-flags bands are fixed in the overlay, so a source banded differently can't use
`Quote.RLM_Approval_Level__c` as its discount level: against one such policy it put two
quotes one level below the policy [Measured: 2026-11-12, 264]. Band the source's own
thresholds in the approval data flow, from each line's `Discount` in a line loop
([matrix-modeling.md](matrix-modeling.md) §2), or change the overlay's bands for every
build (the design doc's Verification Checklist).

Measured end to end on a QuantumBit build [Measured: 2026-11-10, 264]:
- A 30% line discount priced to level 2 ("Director"), 20% to level 1, and 5% to level 0.
- Submitting a level-2 quote created one Discount work item (Manager). The Director item
  appeared only after the Manager approved. After the Director approved, the submission
  and the quote were both Approved.
- Rejecting the Discount item while a Finance item was open set the Finance item to
  Withdrawn, and the submission and the quote to Rejected.
- A level-0 quote with Net 30 was Approved at once.
- Recall set the submission and its work item to Recalled, and the quote to Recalled.
  Resubmitting created a new submission, and approving it set the quote to Approved.
  Cancel set the submission and work item to Canceled and cleared the quote's status
  [Measured: 2026-11-10, 264, with `RLM_AA_Reset_Quote_Status`]. Before that flow
  shipped, recall left the quote at Pending.

## Sub-files

- [matrix-modeling.md](matrix-modeling.md): read when mapping a sign-off matrix. It covers
  levels, multiple dimensions, line conditions, margin and deal size, and where to compute
  each value.
- [actions-and-objects.md](actions-and-objects.md): read when submitting or acting on
  approvals, querying them, or testing headlessly. It covers objects, actions,
  permissions and the measured behaviour.
- [limitations.md](limitations.md): read before relying on Smart Approvals, Preview, email,
  delegation or Slack. It also lists the questions the docs leave open.

## Examples

**Add a margin dimension to the shipped approval.** The policy: blended margin below 55%
needs a Manager, below 50% a Director, below 45% the VP.
- First: margin is a third dimension beyond Discount and Finance, and the design doc makes
  externalizing threshold policy a prerequisite for that
  [Repo: `docs/features/composable-quote-approvals.md`]. Do it first, or agree and record the
  exception; the steps below don't show it.
- Compute the quote margin in the pricing procedure, or in the approval data flow, and
  convert it to a level 0–3 number (`MarginApprovalLevel`) in `RLM_Quote_Approval_Data`.
- Take the overall level as the maximum of the discount and margin levels
  (`ApprovalLevel`), returned by `RLM_Quote_Approval_Data` and declared as an output on the
  `QueryApprovalData` step (`outputConfigParams`, like the shipped outputs), and drive the
  one serial chain from it. Everything that reads
  `DiscountApprovalLevel` must switch to `ApprovalLevel`: the three step entry conditions,
  the `Requires_Approval` decision, and the stage's "not triggered" exit conditions (2, 4
  and 6). Otherwise a margin-only quote skips approval, or the stage exits before anyone
  approves.
- Or give margin its own chain if it needs its own sign-off, following Quick Rule 6.
- Reprice before testing.
- [matrix-modeling.md](matrix-modeling.md) walks through the choices.

**Find out why a quote is stuck at Pending.** Query its `ApprovalSubmission` and work
items:
- An `InProgress` submission with no `Assigned` item, after allowing a few seconds for the
  asynchronous orchestration, usually means the stage's exit logic waits on a step that
  never started: it requires that step to be completed, with no "not triggered"
  alternative (Quick Rule 4). Check the stage exit logic against the flow, and Paused and Failed
  Interviews [Help: `ind.approvals_approval_process_execution`].
- A `Recalled` or `Canceled` submission with the quote still at Pending means
  `RLM_AA_Reset_Quote_Status` didn't run: check that it's active and deployed
  (`deploy_post_approvals`).

## Validation Checks

- `cci flow run prepare_approvals --org <cci_alias>` succeeds, and a rerun is idempotent
  [Repo: `docs/features/composable-quote-approvals.md` → Verification Checklist].
- A rerun is idempotent only if no flow gets a new version. An mdapi redeploy of an unchanged
  autolaunched flow (a generated approval data flow) made a new version every time until the
  file was byte-identical to a retrieved copy; the approval orchestration redeployed without
  a new version [Measured: 2026-11-12, 264]. The deploy compares the file with the stored
  form, where named lists (formulas, constants, text templates, decisions, assignments,
  stages and similar) are sorted by name ignoring case; the file is read in its own order and
  strings must match exactly, so a file whose named lists are out of name order, or whose
  strings differ, counts as changed [Platform behaviour, traced]. Which property differed in
  the measured run is not established, and a numeric literal compares as a number (other
  numeric properties were not audited), so the trace gives no support for a `0.0` rule for
  those literals; a string-typed value holding a number would differ on `0` versus `0.0`. An Active latest version plus an identical file
  creates no version; for a file deploy of an unversioned flow name, a changed file over a Draft (or
  InvalidDraft) latest version overwrites it in place and one over an Active or Obsolete
  latest version creates a new one; a versioned name uses a separate path (not traced to a
  rule); a change set always creates a new version; a deploy requesting
  Active over a non-Active latest version counts as changed. A deploy that does not request
  Active compares against the stored status, so a status-only change to Draft over an Active
  flow is not a change [Platform behaviour, traced]; measured, it created no version and the
  flow stayed Active [Measured: 2026-11-12, 264, scratch]. Deploying an
  approval flow as Active in a production org needs the org setting that lets flows deploy
  as active (the repo's Apex test skip messages call it Deploy-as-active); a non-production org allows it regardless. Without it,
  deploy as Draft and activate separately [Platform behaviour, traced; production gating is
  not measured]. In a scratch org built by this repo the setting read off (Metadata API field
  `enableFlowDeployAsActiveEnabled` in FlowSettings; a fresh org was not read separately); a changed approval orchestration
  deployed as Active still became the new Active version and the old one became Obsolete, and
  an unchanged redeploy as Active created no version. A redeploy with only the status changed
  to Draft over an Active flow also created no version and did not deactivate the flow
  [Measured: 2026-11-12, 264, scratch; non-production]. Steps inside
  orchestrated stages keep their saved order, a possible reason an orchestration redeploys
  unchanged; that is not proven for the measured run. For a new or generated flow, deploy it, retrieve it and commit the retrieved form. Compare
  `SELECT VersionNumber, Status FROM Flow WHERE Definition.DeveloperName = '<flow>'`
  (Tooling API) before and after a rerun. A new version of the approval orchestration flow
  also ends Smart Approvals eligibility for resubmissions
  [Help: `ind.approvals_smart_approval_limitations`].
- The approval-flags overlay and the approvals context plan are applied by
  `prepare_approvals_pricing`, not `prepare_approvals`. On a fresh build it applies both.
  Changing thresholds on an org that already has the overlay takes a separate one-off
  overlay, not a rerun; follow the design doc's Verification Checklist for where each change
  goes [Repo: `docs/features/composable-quote-approvals.md`].
- Run the headless test in [actions-and-objects.md](actions-and-objects.md) for these paths:
    - no-approval
    - each single dimension
    - multi-dimension
    - rejection
    - recall and resubmit
    - cancel

  Each must end with the expected work-item statuses and quote status.
- After dataset changes:
    - `python scripts/ai/check_plan_readme_consistency.py --strict datasets/sfdmu/qb/en-US/qb-approvals`
    - `python scripts/validate_sfdmu_v5_datasets.py`
- After skill edits, run `python scripts/ai/analyze_agent_tooling.py check`.
