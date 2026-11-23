---
page_id: actions_obj_get_previous_rela_rec_details.htm
title: Get Previous Related Record Details Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_get_previous_rela_rec_details.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Advanced Approvals
parent_page: advanced_approvals_invocable_actions_parent.htm
fetched_at: 2026-11-23
---

# Get Previous Related Record Details Action

Get the related record details submitted for approval before the current approval submission. The details are required for approval steps that use custom logic for auto-approvals.

This Apex action is available in API version 66.0 and later.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/getPreviousRelaRecDetails`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer token`

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| flowOrchestrationInstanceId | string | Required. The ID of the flow orchestration instance associated with the approval submission. |
| stepApiNamesList | string | Required. The comma-delimited list of step API names to retrieve previous related record details for. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| previousRelatedRecordDetails | sObject. | The collection of previous related record details for approval steps that use custom logic for auto-approvals. |

## Usage

To use this Apex action in approval workflows, see [Define Rules and Conditions for Auto-Approval Resubmissions](https://help.salesforce.com/s/articleView?id=ind.approvals_define_custom_logic_auto_approvals.htm&language=en_US "HTML (New Window)").

## Example

**POST**

Here's a sample request for the Get Previous Related Record Details action.

```
{
  "flowOrchestrationInstanceId": "0jEDU0000001zeN",
  "stepApiNameList": [
    "ManagerApprovalStep",
    "FinancialApprovalStep"
  ]
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_get_previous_rela_rec_details.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
