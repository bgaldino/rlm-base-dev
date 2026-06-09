---
page_id: actions_obj_override_approval_work_item.htm
title: Override Approval Work Item Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_override_approval_work_item.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Advanced Approvals
parent_page: advanced_approvals_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Override Approval Work Item Action

Update an approval work item status with the approval admin decision
and any comments that the approval admin added.

This action also validates if a user has required permissions to override an approval work item
and update its status. Keep these considerations in mind when you use this invocable
action.

- The user must have the Approval Admin user permission.
- This action enables approval admins to interject the approval decision for any
  assignee.
- The status of the approval work item must be in `Assigned` status.

This action is available in API version 62.0 and later.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/overrideApprovalWorkItem`

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
| approvalDecision | Type  string  Description  Required.  Action that the overriding approval admin made for the unreviewed approval work item. Valid values are:   - `approve` - `reject` |
| approvalWorkItemId | Type  string  Description  Required.  ID of the unreviewed approval work item to be reviewed by an approval admin. |
| channelType | Type  picklist  Description  Type of channel where the request to review the approval work item originated. Valid values are:   - `InvocableAction` - `Slack` - `ApprovalRecord`   The default value is `InvocableAction`. Available in API version 65.0 and later. |
| comments | Type  string  Description  Comments entered by the approval admin about their decision to approve or reject an unreviewed approval work item. |

## Outputs

None.

## Example

POST
:   Here's a sample request for the Override Approval Work Item action.

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
:   Here's a sample response for the Override Approval Work Item action.

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
