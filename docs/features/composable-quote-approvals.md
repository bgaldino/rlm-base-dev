# Composable Quote Approvals

Revenue Cloud Base Foundations uses one Advanced Approvals workflow for
QuantumBit quote approval. The workflow keeps all approval dimensions in one
submission and composes them with approval chains inside a single stage.

Implemented in:

- `unpackaged/post_approvals/flows/RLM_Quote_Smart_Approval.flow-meta.xml`
- `unpackaged/post_approvals/flows/RLM_Quote_Approval_Data.flow-meta.xml`
- `unpackaged/post_approvals/flows/RLM_Quote_Approval_Comments.flow-meta.xml`
- `unpackaged/post_approvals/flows/RLM_AA_Reset_Quote_Status.flow-meta.xml`
- `unpackaged/post_approvals/classes/RLM_AA_Submit_Approval.cls`
- `tasks/rlm_create_approval_email_templates.py`
- `datasets/sfdmu/qb/en-US/qb-approvals/`

## Responsibility Boundary

The platform owns the approval lifecycle. The project should not reimplement
recall, resubmission, work item audit, Smart Approval comparison, or approver
work item management.

- Submission lifecycle: platform `ApprovalSubmission` and Flow Orchestration;
  the project starts the orchestration for the quote.
- Recall and cancellation: platform Advanced Approvals invocable actions; the
  project exposes UI/actions when needed, and resets the quote's own approval
  status (`RLM_AA_Reset_Quote_Status`, below).
- Resubmission: platform new submission after rejection or recall; the project
  keeps the submit action re-runnable.
- Smart Approval: platform Smart Approval inputs on approval steps; the project
  avoids disqualifying flow patterns.
- Audit trail: platform `ApprovalSubmission` and `ApprovalWorkItem` records; the
  project queries or reports on them.
- Chain execution: platform `ActionInput__ApprovalChainName`; the project
  assigns stable chain names per approval area.
- Notifications: platform alert content records linked to email templates; the
  project seeds the alert records and templates.

## Current Topology

The current quote approval entry point is:

```text
Quote quick action
  -> RLM_Quote_Approval_Comments
  -> RLM_AA_Submit_Approval
  -> RLM_Quote_Smart_Approval
```

`RLM_Quote_Smart_Approval` has a background stage that calls
`RLM_Quote_Approval_Data`, then one approval stage with four conditional
approval steps:

| Step                | Chain    | Entry condition                                      | Assignee group |
| ------------------- | -------- | ---------------------------------------------------- | -------------- |
| `Manager_Approver`  | Discount | `DiscountApprovalLevel > 0`                          | `Manager`      |
| `Director_Approver` | Discount | `DiscountApprovalLevel >= 2` and manager approved    | `Director`     |
| `VP_Approver`       | Discount | `DiscountApprovalLevel >= 3` and director approved   | `VP`           |
| `Payment_Terms`     | Finance  | `PaymentTerms != "Net 30"`                           | `Manager`      |

The Discount chain is sequential because Director waits on Manager and VP waits
on Director. The Finance chain can run in parallel with Discount because it uses
a different `ApprovalChainName`.

`DiscountApprovalLevel` is the Quote roll-up of the line levels the pricing
procedure stores on each reprice. There is no staleness guard: a discount changed
without a reprice keeps its old level until the quote is repriced.

If no approval is required (`DiscountApprovalLevel = 0` AND `PaymentTerms = "Net 30"`),
the flow takes the `Requires_Approval` decision's default connector directly to
`Update_Quote_Status_to_Approved`, bypassing the approval stage entirely.

### Quote approval status

`Quote.RLM_Approval_Status__c` (global value set `RLM_Approval_Status`, shown on the
`RLM_Quote_Approval` path) is the project's own field. The platform keeps the real
state on `ApprovalSubmission` and `ApprovalWorkItem`; this field mirrors it for reps.

| Event | Who sets it | Value |
| ----- | ----------- | ----- |
| Approval stage starts | Orchestration background step `Set_Quote_Approval_Status_Pending` (`RLM_AA_Set_Quote_Status`) | `Pending` |
| All required steps approved, or no approval needed | Orchestration stage `Update_Quote_Status_to_Approved` | `Approved` |
| Any step rejected | Orchestration stage `Update_Quote_Status_to_Rejected` | `Rejected` |
| Submission recalled (`recallApprovalSubmission`) | `RLM_AA_Reset_Quote_Status` | `Recalled` |
| Submission canceled (`cancelApprovalSubmission`) | `RLM_AA_Reset_Quote_Status` | blank |

`RLM_Quote_Smart_Approval` has no recall path and nothing that runs on cancel, so it
doesn't set the field on either. `RLM_AA_Reset_Quote_Status` is a
record-triggered flow (after save, on update) on `ApprovalSubmission`. It runs when
`Status` changes to `Recalled` or `Canceled` and `RelatedRecordObjectName = 'Quote'`,
and updates the related quote.

It lives outside `RLM_Quote_Smart_Approval` on purpose. The Help docs offer two
patterns: a recall path inside the approval flow for recall, and a record-triggered
flow on Approval Submission for cancel
(`docs/salesforce/264/help/articles/ind.sf_contracts_aa_configure.htm.md`). One
record-triggered flow handles both, and leaves the orchestration, its active
version and its Smart Approvals eligibility unchanged.

## Exit Condition Pattern

The approval stage uses a composable exit condition pattern with one resolved
clause per approval step:

```text
((Manager completed OR Manager did not trigger)
 AND (Director completed OR Director did not trigger)
 AND (VP completed OR VP did not trigger)
 AND (Payment Terms completed OR Payment Terms did not trigger)
 AND background step completed)
 OR any step rejected
```

The current implementation uses this pattern with the logic expression:

```text
((1 OR 2) AND (3 OR 4) AND (5 OR 6) AND (7 OR 8) AND 9) OR 10
```

Where:
- Conditions 1,3,5,7: `Step.Status = Completed` for Manager, Director, VP, Payment_Terms
- Conditions 2,4,6,8: Inverse trigger conditions (step not required)
- Condition 9: Background step `Set_Quote_Approval_Status_Pending.Status = Completed`
- Condition 10: `rejectedQuote = true` (rejection shortcut)

This requires two numbered exit conditions for each approval step plus one for
each background step that gates exit, plus the rejection shortcut. The current
four approval steps use 10 total conditions: `(4 steps × 2) + 1 background + 1 rejection`.

This pattern has been validated in scratch orgs and proves:
- ✅ Grouped OR clauses inside an outer AND expression are supported
- ✅ Steps that never start resolve via their inverse trigger condition
- ✅ Resubmitted work items remain Smart Approval eligible

## Adding A New Approval Dimension

Add dimensions as a recipe, not as a framework rewrite.

1. Add the approval fact to `RLM_Quote_Approval_Data` if the step needs a new
   quote-derived value, and declare it as an output on the `QueryApprovalData` step
   (`outputConfigParams`) so conditions can read `QueryApprovalData.Outputs.<name>`.
2. Add the new step's trigger condition as an OR condition on the `Requires_Approval`
   decision. Without it, a quote that triggers only the new dimension takes the decision's
   default path straight to `Update_Quote_Status_to_Approved`.
3. Add one `stageSteps` approval step to `RLM_Quote_Smart_Approval`.
4. Give the step a unique `ActionInput__ApprovalChainName`.
5. Add explicit `entryConditions`; do not use a stage-start entry rule.
6. Add two stage exit conditions: `Step.Status = Completed` and the inverse of
   the trigger condition.
7. Add one grouped `(completed OR not triggered)` clause to the stage
   `exitConditionLogic`.
8. Add the step to the `rejectedQuote` formula so any rejection routes to the
   rejected-status stage.
9. Add one `ApprovalAlertContentDef.csv` row and one `EmailTemplate.csv` row in
   `datasets/sfdmu/qb/en-US/qb-approvals/`.

What should not change for a normal new dimension:

- Submission quick action
- Submission comments flow
- Apex submission bridge
- Overall stage structure
- `RLM_AA_Evaluate_Approval_Request`
- `RLM_AA_Set_Quote_Status`
- `RLM_AA_Reset_Quote_Status`
- Email-template task code

Threshold and terms policy is still hardcoded in the current formula/flow
conditions. Externalize threshold policy before adding a third approval
dimension beyond Discount and Finance.

## Notification Scaling

`tasks/rlm_create_approval_email_templates.py` is CSV-driven. It reads every row
from `EmailTemplate.csv`, creates missing Lightning email templates, then links
the matching `ApprovalAlertContentDef` records by the `EmailTemplate.Name`
column. Adding a new approval step family should require only one template row
and one alert row.

## Verification Checklist

Run these checks before treating an approval-flow change as ready:

- `cci flow run prepare_approvals --org <cci_alias>` succeeds on a scratch org.
- Re-running `prepare_approvals` is idempotent.
- If the approval-flags overlay or the approvals context plan changed: on a fresh build,
  `cci flow run prepare_approvals_pricing --org <cci_alias>` applies both. The thresholds
  are step criteria in `approval_flags.json` `addSteps`; edit them there so fresh builds
  get them. On an org that already has the overlay, a rerun fails on a changed step and
  silently skips a changed existing variable. Change that org with a separate, uncommitted
  overlay that keeps `expressionSetApiName` and `versionApiName` from `approval_flags.json`
  and holds only the change: `updateSteps` for a changed step; for a changed variable, its
  name in `removeVariables` and its new definition in `addVariables` (the task removes
  before it adds, `tasks/rlm_expression_set_connect.py`). Apply it with
  `cci task run apply_approval_flags_overlay -o overlay_file <one-off.json> --org <cci_alias>`.
  Never add `updateSteps` for the overlay's own steps to the shipped file: on a fresh org
  those steps don't exist yet, so the task fails. Deactivate the context version before changing a
  mapping (`.cursor/skills/context-service/`). Reprice before testing.
- Preview Approvals doesn't show steps whose entry conditions depend on the
  `QueryApprovalData` background step's subflow. The Help workaround, mock output values set
  in Flow Builder, edits the flow: do it only in a throwaway version that is never committed
  or left active, since a new active version also ends Smart Approvals eligibility for
  resubmissions (Help: `ind.approvals_smart_approval_limitations`). A real submission (below) is the deciding check.
- **No-approval path**: Quotes with `DiscountApprovalLevel = 0` AND `PaymentTerms = "Net 30"` 
  route directly to `Approved` status without entering the approval stage.
- **Single-dimension paths**: Discount-only and terms-only quotes complete correctly.
- **Multi-dimension path**: Quotes requiring both discount and payment term approval complete.
- **Rejection handling**: Rejecting any active work item routes the quote to `Rejected`.
- **Recall**: Recalling an in-progress submission sets the submission and its open
  work items to `Recalled`, and the quote's `RLM_Approval_Status__c` to `Recalled`.
- **Cancel**: Canceling an in-progress submission sets the submission and its open
  work items to `Canceled`, and clears the quote's `RLM_Approval_Status__c`.
- **Resubmission**: Resubmission after rejection or recall keeps expected work items Smart
  Approval eligible.
- `python scripts/ai/check_plan_readme_consistency.py --strict datasets/sfdmu/qb/en-US/qb-approvals`
  reports zero errors, zero warnings after notification dataset changes.
- `python scripts/validate_sfdmu_v5_datasets.py` reports no findings against the composable-approvals
  plans after dataset changes (the run as a whole should PASS clean — 0 Critical, 0 High).
