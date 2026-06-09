---
page_id: actions_obj_reassign_approval_work_item.htm
title: Reassign Approval Work Item Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_reassign_approval_work_item.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Advanced Approvals
parent_page: advanced_approvals_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Reassign Approval Work Item Action

Reassign an approval work item that hasn't been completed. You can
also add comments about why the approval admin reassigned the approval work
item.

This action also validates if a user has required permissions to reassign an approval work item
and update the assignee. Keep these considerations in mind when you use this
invocable action.

- The user must have the Approval Admin user permission.
- The status of the approval work item must be in `Assigned` status.

This action is available in API version 62.0 and later.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/reassignApprovalWorkItem`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization:
    Bearertoken`

## Inputs

| Input | Details |
| --- | --- |
| approvalWorkItemId | Type  string  Description  Required.  ID of the approval work item to be reassigned. |
| assigneeId | Type  string  Description  Required.  ID of the user, group, or queue to reassign the approval work item to. |
| comments | Type  string  Description  Comments entered by the approval admin about why they reassigned the approval work item. |

## Outputs

None.

## Example

POST
:   Here's a sample request for the Reassign Approval Work Item action.

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
:   Here's a sample response for the Reassign Approval Work Item action.

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
