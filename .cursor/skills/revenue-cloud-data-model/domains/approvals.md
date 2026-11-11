# Approvals Domain

3 objects in the ERD: one core record for approval workflow submissions, plus the two
supporting records the `qb-approvals` data plan loads against. Four more Advanced Approvals
objects, marked "live, not in ERD" below, were confirmed by `describe` on a live 264
QuantumBit build (2026-11-10) and aren't in the offline ERD yet. Behaviour and modeling:
`advanced-approvals` skill.

## Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `ApprovalSubmission` | One approval request for a record | RelatedRecordId (polymorphic: Quote, Order, Contract, ...), RelatedRecordObjectName, Status, SubmittedById, FlowOrchestrationInstanceId, IsEligibleForSmartApproval, IsSmartApprovalRun, SmartApprvlBasisSubmissionId |
| `ApprovalWorkItem` (live, not in ERD) | One approval step assigned to a user, group or queue | ApprovalSubmissionId, RelatedRecordId, AssignedToId, Status, ApprovalChainName, ApprovalConditionName, ReviewedById, ReviewedDate, ParentWorkItemId, IsEligibleForSmartApproval, IsEligibleForAutoApproval, IsAutoReviewed, SmartApprovalBasisWorkItemId, FlowOrchestrationWorkItemId |
| `ApprovalSubmissionDetail` (live, not in ERD) | Audit trail of actions on a submission or work item | ApprovalSubmissionId, ApprovalWorkItemId, ActionName, ActionPerformedById, ActionPerformerRole, ActionChannelName, Comments |
| `ApprovalWorkItemCriteria` (live, not in ERD) | Entry/exit logic evaluated for a step | ApprovalWorkItemId, ApprovalStepApiName, CriteriaType, RequirementLogic |
| `ApprovalWorkItemCondition` (live, not in ERD) | One evaluated condition of that logic | ApprovalWorkItemCriteriaId, ConditionSequencePosition, LeftValue, OperatorType, RightValue, HasEvaluationSucceeded, IsConditionExcluded |

`ApprovalDelegation` is documented as new in 264 but was **not** present on that build
(`describe` returned NOT_FOUND); it likely depends on the Use Advanced Approval Delegation
setting. The Help says standard fields on approval objects can't be written through the
sObject APIs; change them through the approval invocable actions
[Help: `ind.approvals_design_build_activation`]. The dev guide, though, lists `update()` on
`ApprovalWorkItem` for `ApprovalChainName` and the Smart Approval fields
[Dev guide: `adv_approvals_capture_fields_on_approvalworkitem`]; unmeasured. Configuration records such as
`ApprovalAlertContentDef` load normally (the `qb-approvals` plan upserts them).

## Supporting Objects (from data plans)

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `ApprovalAlertContentDef` | Maps an email template to an approval flow, step and notification reason | Name, ApprovalFlowApiName, ApprovalStepApiName, NotificationReason, EmailTemplateId |
| `EmailTemplate` | Lightning email template used for approval alerts | Name (read-only reference) |

## Notes

- `ApprovalSubmission.RelatedRecordId` is polymorphic over the approved record's object; it
  is not a link between submissions. `SmartApprvlBasisSubmissionId` names the earlier
  submission that a Smart Approvals evaluation used as its basis (ERD: lookup to
  ApprovalSubmission); not observed on a live resubmission yet.
- Approval alerts use Lightning `EmailTemplate` records. Their builder page is an
  `EmailTemplatePage` FlexiPage, which can't be deployed through Metadata API, so
  `create_approval_email_templates` creates the templates over REST.
- The `qb-approvals` data plan loads ApprovalAlertContentDef records linking to pre-existing EmailTemplate records

## SFDMU Data Plan: `qb-approvals`

2 objects across 2 objectSets. EmailTemplate is ReadOnly; ApprovalAlertContentDef uses Upsert on Name.
