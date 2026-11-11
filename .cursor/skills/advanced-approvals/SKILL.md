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

Use this skill to turn a sign-off policy ("over 20% needs a Director; below 65% margin
needs a Director; over $5M needs the VP") into Revenue Cloud Advanced Approvals. It also
covers running and checking a submission, and extending the approval workflow this repo
already ships. Claims are tagged: `[Help: <article>]` and `[Dev guide: <article>]` from
`docs/salesforce/264/`, `[Repo: <path>]`, and `[Measured: <date>, 264]` for a live run on a
QuantumBit build.

## Quick Rules

1. **Advanced Approvals runs on Flow Orchestration**, so Flow Orchestration's limits apply
   [Help: `ind.approvals_advanced_approvals`]. An approval workflow is an orchestration flow
   of stages and steps: background steps run flows, and approval steps assign work items
   [Help: `ind.approvals_example_configure_an_approval_workflow`].
2. **Reduce every condition to a Number or Text value before the approval stage.**
   - Conditions can test a background step's outputs, another step's outputs (the shipped
     Director step reads `Manager_Approver.Outputs.approvalDecision`) and flow formulas. Line
     values aren't one of those, so aggregate them (a maximum level, a count of lines below
     floor) into quote-level numbers in a background step or a roll-up first.
   - Smart Approvals needs Number or Text conditions and no NOT operator
     [Help: `ind.approvals_smart_approval_limitations`].
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
    - Standard approval fields can't be written through the sObject APIs
      [Help: `ind.approvals_design_build_activation`].
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
- **DO NOT** expect to choose the submitter. `SubmittedById` was the running user on every
  route tried: the repo's Apex bridge, and starting the flow over REST with another user's ID
  in the `submitter` input [Measured: 2026-11-10, 264]. The shipped orchestration declares
  `submitter` but never reads it. (In an *autolaunched* flow started by a quick action,
  `$User` is the Automated Process User [Help: `ind.approvals_add_an_approval_button_for_sales_reps`];
  the repo's quick action launches a screen flow, which runs as the user.)
- **DO NOT** confuse "dynamic approvals" with dynamic routing. In the docs it means
  AI-written notification summaries [Help: `ind.approvals_turn_on_dynamic_approvals`].
- **DO NOT** confuse this feature with the legacy Salesforce CPQ "Advanced Approvals"
  managed package.

## Entry Conditions

| Situation | Use |
|---|---|
| Add an approval dimension to the shipped quote approval (margin, deal size, term) | This skill → [matrix-modeling.md](matrix-modeling.md), then `docs/features/composable-quote-approvals.md` |
| Map a customer's sign-off matrix onto approvals | This skill → [matrix-modeling.md](matrix-modeling.md) |
| Submit, approve, reject, recall or inspect a submission; test headlessly | This skill → [actions-and-objects.md](actions-and-objects.md) |
| Smart Approvals, preview, email, delegation limits; what's still unknown | This skill → [limitations.md](limitations.md) |
| Change how the line approval level is computed | `pricing-procedures` and `expression-sets` (the `approval_flags.json` overlay) |
| Map a field into the pricing context | `context-service` (`datasets/context_plans/Approvals`) |
| Load or change alert definitions | `sfdmu-data-plans` (`datasets/sfdmu/qb/en-US/qb-approvals`) |
| Approval objects and fields | `revenue-cloud-data-model` → `domains/approvals.md` |

## What the repo ships

With the `quantumbit` and `approvals` flags on, `prepare_rlm_org` builds a working quote
approval (the alert definitions also need `qb`; all three default to true) [Repo: `cumulusci.yml`, `docs/features/composable-quote-approvals.md`]:

| Piece | What it does |
|---|---|
| `unpackaged/post_approvals` (`deploy_post_approvals`) | Fields (`Quote.RLM_Approval_Level__c`, a MAX roll-up of `QuoteLineItem.RLM_Approval_Level_Calc__c`; `RLM_Approval__c` flag; `RLM_Approval_Status__c`; `RLM_Payment_Terms__c`), the flows, the `RLM_Submit_for_Approval` quick action, the Apex bridge, the `RLM_Approvals` permission set |
| `datasets/expression_set_overlays/approval_flags.json` (`apply_approval_flags_overlay`) | Sets each line's level from its discount on every reprice: 15% to under 25% → 1 Manager, 25% to under 35% → 2 Director, 35% to under 100% → 3 VP |
| `datasets/context_plans/Approvals` (`apply_context_approvals`) | Maps the two line fields into `RLM_SalesTransactionContext` so pricing can write them |
| `RLM_Quote_Smart_Approval` (orchestration) | Background data step → approval stage with a Discount chain (Manager → Director → VP, cumulative) and a Finance chain (payment terms other than Net 30) → Approved or Rejected stage. Level 0 with Net 30 skips approval |
| `datasets/sfdmu/qb/en-US/qb-approvals` + `create_approval_email_templates` | Lightning email templates and the alert definitions that link them to steps |

Measured end to end on a QuantumBit build [Measured: 2026-11-10, 264]:
- A 30% line discount priced to level 2 ("Director"), 20% to level 1, and 5% to level 0.
- Submitting a level-2 quote created one Discount work item (Manager). The Director item
  appeared only after the Manager approved. After the Director approved, the submission
  and the quote were both Approved.
- Rejecting the Discount item while a Finance item was open set the Finance item to
  Withdrawn, and the submission and the quote to Rejected.
- A level-0 quote with Net 30 was Approved at once.
- **Recall left the quote's status at Pending:** the shipped flow has no recall path.
  Resubmitting created a new submission.

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

**Add a margin dimension to the shipped approval.** The policy: blended margin below 70%
needs a Manager, below 65% a Director, below 60% the VP.
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
- Or give margin its own chain if its approvers differ, following Quick Rule 6.
- The design doc asks for threshold policy to be externalized before a third dimension is
  added [Repo: `docs/features/composable-quote-approvals.md`]. Folding margin into one level
  adds no step, but its thresholds are still hard-coded.
- Reprice before testing.
- [matrix-modeling.md](matrix-modeling.md) walks through the choices.

**Find out why a quote is stuck at Pending.** Query its `ApprovalSubmission` and work
items:
- An `InProgress` submission with no `Assigned` item, after allowing a few seconds for the
  asynchronous orchestration, usually means a stage exit condition is missing for a step
  that never started. Confirm with `ApprovalWorkItemCriteria` / `ApprovalWorkItemCondition`,
  and check Paused and Failed Interviews [Help: `ind.approvals_approval_process_execution`].
- A `Recalled` submission with the quote at Pending is the missing recall path above.

## Validation Checks

- `cci flow run prepare_approvals --org <cci_alias>` succeeds, and a rerun is idempotent
  [Repo: `docs/features/composable-quote-approvals.md` → Verification Checklist].
- The approval-flags overlay and the approvals context plan are applied by
  `prepare_approvals_pricing`, not `prepare_approvals`. On a fresh build it applies both.
  On an org that already has them, rerunning it applies only additions: a changed overlay
  step must go through `updateSteps` (`expression-sets`), and a changed context mapping needs
  the version deactivated first (`context-service`). Reprice before testing.
- Run the headless test in [actions-and-objects.md](actions-and-objects.md) for these paths:
    - no-approval
    - each single dimension
    - multi-dimension
    - rejection
    - recall and resubmit

  Each must end with the expected work-item statuses and quote status.
- After dataset changes:
    - `python scripts/ai/check_plan_readme_consistency.py --strict datasets/sfdmu/qb/en-US/qb-approvals`
    - `python scripts/validate_sfdmu_v5_datasets.py`
- After skill edits, run `python scripts/ai/analyze_agent_tooling.py check`.
