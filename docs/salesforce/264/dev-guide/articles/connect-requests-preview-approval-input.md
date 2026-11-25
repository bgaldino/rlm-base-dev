---
page_id: connect-requests-preview-approval-input
title: Preview Approval Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-preview-approval-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Advanced Approvals
parent_page: advanced-approvals-api-requests
legacy_page_id: connect_requests_preview_approval_input.htm
fetched_at: 2026-11-25
---

# Preview Approval Input

Input representation of the details of the request to preview an approval.

## JSON Example

```
{
  "flowApiName": "QuoteApprovals",
  "objectApiName": "Quote",
  "recordId": "0Q0DU0000005HZC0A2",
  "inputParameters": {
    "approverComments": "Submitted for approval",
    "requestType": "Standard"
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `flowApiName` | String | API name of the auto-launched flow. | Required | 65.0 |
| `objectApiName` | String | API name of the object to preview the approvals for. | Required | 65.0 |
| `recordId` | String | ID of the record to preview the approvals for. | Required | 65.0 |
| `inputParameters` | Map<String, Object> | List of input parameters to preview. | Optional | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-preview-approval-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
