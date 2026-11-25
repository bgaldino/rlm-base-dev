---
page_id: actions-obj-review-approval-work-item
title: Review Approval Work Item Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-review-approval-work-item.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Advanced Approvals
parent_page: advanced-approvals-invocable-actions-parent
legacy_page_id: actions_obj_review_approval_work_item.htm
fetched_at: 2026-11-25
---

# Review Approval Work Item Action

Update an approval work item status with the assignee or reviewer’s decision and any comments that the assignee or reviewer added.

Keep these considerations in mind when you use this invocable action.

- The user must be an assignee of the approval work item or be a member of a group or queue if the approval work item is assigned to the group or queue. Additionally, a user has access to Approval Submissions if they’re a delegate of the assignee or has a role higher than the assignee.

- The status of the approval work item must be in `Assigned` status.

- The user can also use this action if inherited access to group or queue membership, nested group membership, roles hierarchy, or delegates is available. See [Public Group Considerations](https://help.salesforce.com/s/articleView?id=platform.user_groups_considerations.htm).

This action is available in API version 62.0 and later.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/reviewApprovalWorkItem`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `approvalDecision` | string | Required. Action that the assigned approver made for the approval work item. Valid values are `approve` or `reject`. |
| `approvalWorkItemId` | string | Required. ID of the approval work item to be reviewed by the assigned approver. |
| `channelType` | picklist | Type of channel where the request to review the approval work item originated. Valid values are `InvocableAction`, `Slack`, or `ApprovalRecord`. The default value is `InvocableAction`. Available in API version 65.0 and later. |
| `comments` | string | Approval comments for the decision. |

## Outputs

None.

## Example

**POST**

Here’s a sample request for the Review Approval Work Item action.

```
{
  "inputs": [
    {
      "approvalWorkItemId": "9jRxx00000001lhEAA",
      "approvalDecision": "Approve",
      "channelType": "InvocableAction",
      "comments": "Looks good."
    }
  ]
}
```

Here’s a sample response for the Review Approval Work Item action.

```
{
  "actionName": "reviewApprovalWorkItem",
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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-review-approval-work-item.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
