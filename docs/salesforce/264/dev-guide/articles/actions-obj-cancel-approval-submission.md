---
page_id: actions-obj-cancel-approval-submission
title: Cancel Approval Submission Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-cancel-approval-submission.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Advanced Approvals
parent_page: advanced-approvals-invocable-actions-parent
legacy_page_id: actions_obj_cancel_approval_submission.htm
fetched_at: 2026-11-25
---

# Cancel Approval Submission Action

Cancels an approval submission and all child approval work items that haven’t been completed. You can also add comments about why the approval admin made the cancellation.

This action also validates if a user has required permissions to cancel an approval submission. Keep these considerations in mind when you use this invocable action.

- The user must have the Approval Admin user permission.

- The status of the approval submission must be in `In progress` or `Suspended` status.

This action is available in API version 62.0 and later.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/cancelApprovalSubmission`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `approvalSubmissionId` | string | Required. ID of the Approval Submission to be canceled. |
| `comments` | string | Comments entered by the approval admin about why they canceled the Approval Submission. |

## Outputs

None.

## Example

**POST**

Here’s a sample request for the Cancel Approval Submission action.

```
{
  "inputs": [
    {
      "approvalSubmissionId": "9iPxx00000001lhEBA",
      "comments": "Cancellation comments."
    }
  ]
}
```

Here’s a sample response for the Cancel Approval Submission action.

```
{
  "actionName": "cancelApprovalSubmission",
  "errors": null,
  "invocationId": null,
  "isSuccess": true,
  "outcome": null,
  "outputValues": null,
  "sortOrder": -1,
  "version": 1
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-cancel-approval-submission.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
