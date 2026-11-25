---
page_id: advanced-approvals-flow-metadata-api
title: Flow for Advanced Approvals
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/advanced-approvals-flow-metadata-api.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Advanced Approvals
parent_page: advanced-approvals-metadata-api-parent
legacy_page_id: advanced_approvals_flow_metadata_api.htm
fetched_at: 2026-11-25
---

# Flow for Advanced Approvals

The flow for Advanced Approvals represents the metadata associated with a flow. With Flow, you can create an application that takes users through a series of pages to query and update the records in the database. You can also run logic and provide branching capability based on user input to build dynamic applications.

## FlowActionCall

Advanced Approvals exposes additional actionType values for the FlowActionCall metadata type.

| Field Name | Field Type | Description |
| --- | --- | --- |
| `actionType` | InvocableActionType (enumeration of type string) | Required. The action type. Additional valid values for Advanced Approvals are `cancelApprovalSubmission`—Cancels an approval submission and all child approval work items that haven’t been completed. You can also add comments about why the approval admin made the cancellation. Added in API version 62.0 and later; `overrideApprovalWorkItem`—Update an approval work item status with the approval admin decision and any comments that the approval admin added. Added in API version 62.0 and later; `reassignApprovalWorkItem`—Reassign an approval work item that hasn’t been completed. You can also add comments about why the approval admin reassigned the approval work item. Added in API version 62.0 and later; `recallApprovalSubmission`—Recall an approval submission that isn’t completed. You can also add comments that the submitter or approval admin made the recall. Added in API version 62.0 and later; `reviewApprovalWorkItem`—Update an approval work item status with the assignee or reviewer’s decision and any comments that the assignee or reviewer added. Added in API version 62.0 and later; or `getPreviousRelaRecDetails`—Get the related record details submitted for approval before the current approval submission. The details are required for approval steps that use custom logic for auto-approvals. Added in API version 66.0 and later. |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/advanced-approvals-flow-metadata-api.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
