---
page_id: actions-obj-override-approval-work-item
title: Override Approval Work Item Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-override-approval-work-item.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Advanced Approvals
parent_page: advanced-approvals-invocable-actions-parent
legacy_page_id: actions_obj_override_approval_work_item.htm
fetched_at: 2026-11-25
---

# Override Approval Work Item Action

Update an approval work item status with the approval admin decision and any comments that the approval admin added.

This action also validates if a user has required permissions to override an approval work item and update its status. Keep these considerations in mind when you use this invocable action.

- The user must have the Approval Admin user permission.

- This action enables approval admins to interject the approval decision for any assignee.

- The status of the approval work item must be in `Assigned` status.

This action is available in API version 62.0 and later.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/overrideApprovalWorkItem`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `approvalDecision` | string | Required. Action that the overriding approval admin made for the unreviewed approval work item. Valid values are `approve` or `reject`. |
| `approvalWorkItemId` | string | Required. ID of the unreviewed approval work item to be reviewed by an approval admin. |
| `channelType` | picklist | Type of channel where the request to review the approval work item originated. Valid values are `InvocableAction`, `Slack`, or `ApprovalRecord`. The default value is `InvocableAction`. Available in API version 65.0 and later. |
| `comments` | string | Comments entered by the approval admin about their decision to approve or reject an unreviewed approval work item. |

## Outputs

None.

## Example

**POST**

Here’s a sample request for the Override Approval Work Item action.

```
{
  "inputs": [
    {
      "approvalWorkItemId": "9jRxx00000001lhEAA",
      "approvalDecision": "Reject",
      "channelType": "InvocableAction",
      "comments": "Needs to be reviewed."
    }
  ]
}
```

Here’s a sample response for the Override Approval Work Item action.

```
{
  "actionName": "overrideApprovalWorkItem",
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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-override-approval-work-item.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
