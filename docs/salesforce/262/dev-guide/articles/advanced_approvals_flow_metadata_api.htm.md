---
page_id: advanced_approvals_flow_metadata_api.htm
title: Flow for Advanced Approvals
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/advanced_approvals_flow_metadata_api.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Advanced Approvals
parent_page: advanced_approvals_metadata_api_parent.htm
fetched_at: 2026-06-09
---

# Flow for Advanced Approvals

The flow for Advanced Approvals represents the metadata associated with a flow. With
Flow, you can create an application that takes users through a series of pages to query and
update the records in the database. You can also run logic and provide branching capability
based on user input to build dynamic applications.

## FlowActionCall

Advanced Approvals exposes additional actionType values
for the FlowActionCall metadata type.

| Field Name | Field Type | Description |
| --- | --- | --- |
| actionType | InvocableActionType (enumeration of type string) | Required.  The action type. Additional valid values for Advanced Approvals are:   - `cancelApprovalSubmission`—Cancels an approval submission and all child approval work items   that haven't been completed. You can also add comments about why the approval admin made   the cancellation. Added in API version 62.0 and later. - `overrideApprovalWorkItem`—Update an approval work item status with the approval admin decision   and any comments that the approval admin added. Added in API version 62.0 and later. - `reassignApprovalWorkItem`—Reassign an approval work item that hasn't been completed. You can   also add comments about why the approval admin reassigned the approval work   item. Added in API version 62.0 and later. - `recallApprovalSubmission`—Recall an approval submission that isn't completed. You can also add   comments that the submitter or approval admin made the recall. Added in API version 62.0 and later. - `reviewApprovalWorkItem`—Update an approval work item status with the assignee or reviewer's   decision and any comments that the assignee or reviewer added. Added in API version 62.0 and later. - `getPreviousRelaRecDetails`—Get the related record details submitted for approval before the   current approval submission. The details are required for approval steps that use custom   logic for auto-approvals. Added in API version 66.0 and later. |

/
