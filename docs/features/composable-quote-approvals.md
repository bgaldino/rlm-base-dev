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
`RLM_Quote_Approval_Data`, then one approval stage with seven conditional
approval steps:

| Step                | Chain    | Entry condition                                      | Assignee group |
| ------------------- | -------- | ---------------------------------------------------- | -------------- |
| `Manager_Approver`  | Discount | `DiscountApprovalLevel > 0`                          | `Manager`      |
| `Director_Approver` | Discount | `DiscountApprovalLevel >= 2` and manager approved    | `Director`     |
| `VP_Approver`       | Discount | `DiscountApprovalLevel >= 3` and director approved   | `VP`           |
| `Margin_Manager`    | Margin   | `MarginApprovalLevel > 0`                            | `Manager`      |
| `Margin_Director`   | Margin   | `MarginApprovalLevel >= 2` and manager approved      | `Director`     |
| `Margin_VP`         | Margin   | `MarginApprovalLevel >= 3` and director approved     | `VP`           |
| `Payment_Terms`     | Finance  | `PaymentTerms != "Net 30"`                           | `Manager`      |

The Discount chain is sequential because Director waits on Manager and VP waits
on Director. The Margin chain mirrors the same sequential shape on its own
`ActionInput__ApprovalChainName` (`Margin`), reusing the `Manager`/`Director`/`VP`
groups — no new approver groups. The Finance chain can run in parallel with
Discount and Margin because it uses a different `ApprovalChainName`.

Margin routes on **worst-line margin**: a per-line calc field takes the
`MAX` rollup across the quote's lines, so the thinnest-margin line drives the
quote's tier even if the blended/weighted deal margin is healthy — this
intentionally mirrors the Discount chain's worst-line policy.

If no approval is required (`DiscountApprovalLevel = 0` AND `MarginApprovalLevel = 0`
AND `PaymentTerms = "Net 30"`), the flow takes the `Requires_Approval` decision's
default connector directly to `Update_Quote_Status_to_Approved`, bypassing the
approval stage entirely.

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
((1 OR 2) AND (3 OR 4) AND (5 OR 6) AND (7 OR 8) AND (11 OR 12) AND (13 OR 14) AND (15 OR 16) AND 9) OR 10
```

Where:
- Conditions 1,3,5,7: `Step.Status = Completed` for Manager_Approver, Director_Approver,
  VP_Approver, Payment_Terms (Discount + Finance)
- Conditions 2,4,6,8: Inverse trigger conditions (step not required)
- Condition 9: Background step `Set_Quote_Approval_Status_Pending.Status = Completed`
- Condition 10: `rejectedQuote = true` (rejection shortcut)
- Conditions 11,13,15: `Step.Status = Completed` for Margin_Manager, Margin_Director,
  Margin_VP (Margin chain)
- Conditions 12,14,16: Inverse trigger conditions for the Margin chain
  (`MarginApprovalLevel < 1/2/3`)

This requires two numbered exit conditions for each approval step plus one for
each background step that gates exit, plus the rejection shortcut. The current
seven approval steps use 16 total conditions: `(7 steps × 2) + 1 background + 1 rejection`.
New chains' conditions are appended after the rejection shortcut (10) rather than
renumbered inline, so each dimension's condition block stays a contiguous, easy-to-audit
range — every chain's satisfaction clause is a required conjunct in
`exitConditionLogic`, never a top-level OR (a top-level OR would let that chain's
own completion state override every other chain, short-circuiting the exit gate).

This pattern has been validated in scratch orgs and proves:
- ✅ Grouped OR clauses inside an outer AND expression are supported
- ✅ Steps that never start resolve via their inverse trigger condition
- ✅ Resubmitted work items remain Smart Approval eligible

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
9. Grant FLS on any new fact-source fields across `RLM_Approvals`,
   `RLM_QuantumBit`, and `RLM_QuantumBit_Sales_Representative` (source lives in
   `unpackaged/post_personas/` and `unpackaged/post_tso/`). These deploy via
   `deploy_post_personas`/`deploy_post_tso`, **separate `Deploy` tasks from
   `deploy_post_approvals`** — a prepared org won't pick up the FLS edit until
   you rerun the matching task. An empty FLS query against correct source XML
   is the signature of a missed redeploy, not an authoring bug.
10. Optionally surface the new fields on the Quote record page via
    `templates/flexipages/patches/approvals/RLM_Quote_Record_Page.yml`
    (`add_display_field` / `add_facet_field`), then run
    `assemble_and_deploy_ux`.

What should not change for a normal new dimension:

- Submission quick action
- Submission comments flow
- Apex submission bridge
- Overall stage structure
- `RLM_AA_Evaluate_Approval_Request`
- `RLM_AA_Set_Quote_Status`
- Email-template task code

Threshold and terms policy is still hardcoded in the current formula/flow
conditions. The Margin dimension (a third approval dimension, added after
Discount and Finance) shipped with this deviation still open — thresholds are
hardcoded in `RLM_Margin_Level_Calc__c` rather than externalized. A routing-only
mode toggle (`RLM_Approval_Config__mdt`, gating which chains run) is scoped as a
deferred follow-up; full threshold externalization (cutoffs read from
`$CustomMetadata`) remains a further, still-deferred extension of that same
type.

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
- Preview Approvals shows the expected chains and steps, including the Margin chain.
- **No-approval path**: Quotes with `DiscountApprovalLevel = 0` AND
  `MarginApprovalLevel = 0` AND `PaymentTerms = "Net 30"` route directly to
  `Approved` status without entering the approval stage.
- **Single-dimension paths**: Discount-only, margin-only, and terms-only quotes
  complete correctly.
- **Multi-dimension path**: Quotes requiring discount, margin, and/or payment
  term approval in combination complete, with both Discount and Margin chains
  running in parallel when both trigger.
- **Rejection handling**: Rejecting any active work item (including a Margin
  step) routes the quote to `Rejected`.
- **Resubmission**: Resubmission after rejection or recall keeps expected work items Smart
  Approval eligible.
- `python scripts/ai/check_plan_readme_consistency.py datasets/sfdmu/qb/en-US/qb-approvals`
  reports zero errors after notification dataset changes.
- `python scripts/validate_sfdmu_v5_datasets.py` passes after dataset changes.
