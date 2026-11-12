# Actions, Objects and a Headless Test

Read this when submitting, acting on or inspecting approvals, or testing them without
the UI. Parent: [advanced-approvals](SKILL.md). The object fields are in
`revenue-cloud-data-model` → `domains/approvals.md`.

## Objects

| Object | Holds |
|---|---|
| `ApprovalSubmission` | The request: `RelatedRecordId`, `Status` (Approved, Canceled, Errored, InProgress, Recalled, Rejected, Suspended), `SubmittedById`, `FlowOrchestrationInstanceId`. Query only: no create or update [Dev guide: `sforce_api_objects_approvalsubmission`] |
| `ApprovalWorkItem` | One assigned step: `Status` (Assigned, Approved, Rejected, Recalled, Canceled, Withdrawn, ...), `AssignedToId` (user, group or queue), `ApprovalChainName`, `ApprovalConditionName`, `ReviewedById`, Smart Approval fields |
| `ApprovalSubmissionDetail` | Audit trail of every action |
| `ApprovalWorkItemCriteria`, `ApprovalWorkItemCondition` | The entry and exit logic evaluated for a work item, condition by condition: criteria keyed by `ApprovalWorkItemId`, conditions by `ApprovalWorkItemCriteriaId`. Read these to see why a started step's logic evaluated as it did; whether a row exists for a step that never started is unverified. The Help names approval admins as having access to them [Help: `ind.approvals_personas`] |

The Withdrawn, Recalled and Canceled work-item statuses and the field lists were measured on a live
org [Measured: 2026-11-10, 264]. `ApprovalDelegation` wasn't present there.

## Actions

| Operation | How | Who, precondition |
|---|---|---|
| Submit | Start the approval flow. Repo: `POST /services/data/v68.0/actions/custom/apex/RLM_AA_Submit_Approval` with `{"inputs":[{"flowName":"RLM_Quote_Smart_Approval","recordId":"<quote>","comments":"..."}]}`. Starting the flow directly (`/actions/custom/flow/<flow>`) also works. The Apex bridge passes the running user as `submitter`. In one REST run that started the flow with another user's ID in `submitter`, `SubmittedById` was still the running user [Measured: 2026-11-10, 264] | Run Flows; for the Apex route, access to the `RLM_AA_Submit_Approval` class (granted by `RLM_Approvals`) |
| Approve or reject | `POST /actions/standard/reviewApprovalWorkItem` with `approvalWorkItemId`, `approvalDecision` (`Approve`/`Reject`), `comments` [Dev guide: `actions_obj_review_approval_work_item`] | The assignee, a group or queue member, a delegate, or a user above in the role hierarchy [Dev guide], or an approval administrator, who can review any work item [Help: `ind.approvals_personas`]; the item must be `Assigned`. An admin holding Approval Admin (through its profile and `RLM_CLM`) reviewed an empty group's item [Measured: 2026-11-10, 264] |
| Override | `overrideApprovalWorkItem`, same inputs [Dev guide: `actions_obj_override_approval_work_item`] | Approval Admin; item `Assigned` |
| Reassign | `reassignApprovalWorkItem` with `approvalWorkItemId`, `assigneeId`, `comments` | Approval Admin; item `Assigned`. Makes a later resubmission ineligible for Smart Approvals |
| Recall | `recallApprovalSubmission` with `approvalSubmissionId`, `comments` [Dev guide: `actions_obj_recall_approval_submission`] | Submission InProgress or Suspended. The dev guide says Approval Admin and submitter [Dev guide: `actions_obj_recall_approval_submission`]; the Help personas table gives submitters recall with Run Flows plus Read [Help: `ind.approvals_personas`]. The measured run was an admin who was also the submitter |
| Cancel | `cancelApprovalSubmission` with `approvalSubmissionId`, `comments` [Dev guide: `actions_obj_cancel_approval_submission`] | Approval Admin; submission InProgress or Suspended |
| Preview | `POST /connect/advanced-approvals/approval-submission/preview` with `flowApiName`, `objectApiName`, `recordId`, `inputParameters` [Dev guide: `connect_resources_preview_approvals`]; v65+, `inputParameters` v67+ | Creates nothing |
| Prior submission data | `getPreviousRelaRecDetails` (v66+) | For rule-based auto-approval |
| Read the approval data | Run the approval data flow on its own: `POST /services/data/v68.0/actions/custom/flow/<data flow API name>` with `{"inputs":[{"QuoteId":"<quote>"}]}` (the shipped `RLM_Quote_Approval_Data` takes `QuoteId`). The response's `outputValues` holds every output the background step would pass, so each dimension's level can be read without submitting. Measured on a modified copy of the shipped data flow that returns one level per dimension [Measured: 2026-11-12, 264] | Run Flows; a data flow that only reads records submits nothing |

## Headless test

For each path, create a quote, reprice it, submit, act, and read state after every step.
Before submitting, read each dimension's level from the data flow (Actions → Read the
approval data), so a wrong result can be traced to the level or to the routing.

```sql
SELECT Id, Status, SubmittedBy.Name FROM ApprovalSubmission WHERE RelatedRecordId = '<quote>' ORDER BY CreatedDate
SELECT Id, Status, ApprovalChainName, AssignedToId, IsEligibleForSmartApproval
  FROM ApprovalWorkItem WHERE RelatedRecordId = '<quote>' ORDER BY CreatedDate
SELECT RLM_Approval_Level__c, RLM_Approval_Status__c FROM Quote WHERE Id = '<quote>'
```

Wait a few seconds between an action and the read: the orchestration runs
asynchronously. Expected results on the shipped flow [Measured: 2026-11-10, 264]:

| Path | Setup | Expected |
|---|---|---|
| No approval | level 0, Net 30 | Submission Approved immediately; quote Approved |
| Cumulative chain | level 2, Net 30 | Manager item; after approval, a Director item; after approval, submission and quote Approved |
| Parallel chains, rejection | level 2, Net 60 | Discount and Finance items; rejecting Discount sets Finance to Withdrawn, submission and quote to Rejected |
| Recall and resubmit | level 1 | Recall sets the submission and item to Recalled, and the quote to Recalled (`RLM_AA_Reset_Quote_Status`); resubmit creates a new InProgress submission and sets the quote back to Pending; approving it sets both to Approved |
| Cancel | level 1, submitted | Cancel sets the submission and item to Canceled, and clears the quote's status |

Test with a sales user as well as an admin before relying on permissions: the measured
runs used an admin.
