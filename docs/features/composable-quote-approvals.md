# Composable Quote Approvals

Revenue Cloud Base Foundations uses one Advanced Approvals workflow for
QuantumBit quote approval. The workflow keeps all approval dimensions in one
submission and composes them with approval chains inside a single stage.

Implemented in:

- `unpackaged/post_approvals/flows/RLM_Quote_Smart_Approval.flow-meta.xml`
- `unpackaged/post_approvals/flows/RLM_Quote_Approval_Data.flow-meta.xml`
- `unpackaged/post_approvals/flows/RLM_Quote_Approval_Comments.flow-meta.xml`
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
  project exposes UI/actions when needed.
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

## Exit Condition Pattern

The approval stage currently enumerates completion scenarios in
`exitConditionLogic`. That works, but each new step can require rewriting the
whole expression.

The target pattern is one resolved clause per approval step:

```text
((Manager completed OR Manager did not trigger)
 AND (Director completed OR Director did not trigger)
 AND (VP completed OR VP did not trigger)
 AND (Payment Terms completed OR Payment Terms did not trigger))
 OR any step rejected
```

In metadata grammar this requires two numbered exit conditions for each
approval step: one for `Step.Status = Completed` and one inverse trigger
condition. For the current four approval steps, the expected count is
`2N + 1` approval-stage exit conditions: eight step-resolution conditions plus
the rejection shortcut. A background-step completion condition can be added if a
stage contains a background step whose completion must also gate exit.

Do not change the production flow to this pattern until it has been validated in
a scratch org. The validation must prove:

- `exitConditionLogic` accepts grouped OR clauses inside an outer AND expression.
- A step that never starts can be treated as resolved by its inverse trigger
  condition.
- Resubmitted work items remain Smart Approval eligible.

If grouped clauses are rejected by the platform, use formula-backed
step-resolved booleans or keep the current scenario-enumeration expression and
document the extension template.

## Adding A New Approval Dimension

Add dimensions as a recipe, not as a framework rewrite.

1. Add the approval fact to `RLM_Quote_Approval_Data` if the step needs a new
   quote-derived value.
2. Add one `stageSteps` approval step to `RLM_Quote_Smart_Approval`.
3. Give the step a unique `ActionInput__ApprovalChainName`.
4. Add explicit `entryConditions`; do not use a stage-start entry rule.
5. Add two stage exit conditions: `Step.Status = Completed` and the inverse of
   the trigger condition.
6. Add one grouped `(completed OR not triggered)` clause to the stage
   `exitConditionLogic`.
7. Add the step to the `rejectedQuote` formula so any rejection routes to the
   rejected-status stage.
8. Add one `ApprovalAlertContentDef.csv` row and one `EmailTemplate.csv` row in
   `datasets/sfdmu/qb/en-US/qb-approvals/`.

What should not change for a normal new dimension:

- Submission quick action
- Submission comments flow
- Apex submission bridge
- Overall stage structure
- `RLM_AA_Evaluate_Approval_Request`
- `RLM_AA_Set_Quote_Status`
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
- Preview Approvals shows the expected chains and steps.
- Discount-only, terms-only, and discount-plus-terms quotes all complete.
- Rejecting any active work item routes the quote to `Rejected`.
- Resubmission after rejection or recall keeps expected work items Smart
  Approval eligible.
- `python scripts/ai/check_plan_readme_consistency.py datasets/sfdmu/qb/en-US/qb-approvals`
  reports zero errors after notification dataset changes.
- `python scripts/validate_sfdmu_v5_datasets.py` passes after dataset changes.
