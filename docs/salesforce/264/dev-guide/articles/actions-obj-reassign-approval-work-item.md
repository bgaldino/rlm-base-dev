---
page_id: actions-obj-reassign-approval-work-item
title: Reassign Approval Work Item Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-reassign-approval-work-item.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Advanced Approvals
parent_page: advanced-approvals-invocable-actions-parent
legacy_page_id: actions_obj_reassign_approval_work_item.htm
fetched_at: 2026-11-25
---

# Reassign Approval Work Item Action

Reassign an approval work item that hasn’t been completed. You can also add comments about why the approval admin reassigned the approval work item.

This action also validates if a user has required permissions to reassign an approval work item and update the assignee. Keep these considerations in mind when you use this invocable action.

- The user must have the Approval Admin user permission.

- The status of the approval work item must be in `Assigned` status.

This action is available in API version 62.0 and later.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/reassignApprovalWorkItem`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `approvalWorkItemId` | string | Required. ID of the approval work item to be reassigned. |
| `assigneeId` | string | Required. ID of the user, group, or queue to reassign the approval work item to. |
| `comments` | string | Comments entered by the approval admin about why they reassigned the approval work item. |

## Outputs

None.

## Example

**POST**

Here’s a sample request for the Reassign Approval Work Item action.

```
{
  "inputs": [
    {
      "approvalWorkItemId": "9jRDU00000015C22AI",
      "assigneeId": "005DU000000I3zHYAS",
      "comments": "Needs to be reviewed."
    }
  ]
}
```

Here’s a sample response for the Reassign Approval Work Item action.

```
{
  "actionName": "reassignApprovalWorkItem",
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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-reassign-approval-work-item.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
