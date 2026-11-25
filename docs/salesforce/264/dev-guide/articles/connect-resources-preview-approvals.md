---
page_id: connect-resources-preview-approvals
title: Preview Approval (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-preview-approvals.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Advanced Approvals
parent_page: advanced-approvals-business-apis-rest-references
legacy_page_id: connect_resources_preview_approvals.htm
fetched_at: 2026-11-25
---

# Preview Approval (POST)

Preview the approval levels of a record and associated level details, approval chains, approvers, and conditions before you submit the record for an approval.

For example, a sales rep working on a quote can preview the approval levels for a quote before submitting the quote for approval.

## Resource

```
/connect/advanced-approvals/approval-submission/preview
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/advanced-approvals/approval-submission/preview
```

## Available Version

65.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

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

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `flowApiName` | String | API name of the auto-launched flow. | Required | 65.0 |
| `objectApiName` | String | API name of the object to preview the approvals for. | Required | 65.0 |
| `recordId` | String | ID of the record to preview the approvals for. | Required | 65.0 |
| `inputParameters` | Map<String, Object> | List of input parameters to preview. | Optional | 67.0 |

## Response Body for POST

[Preview Approval](./connect-responses-preview-approval-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-preview-approvals.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
