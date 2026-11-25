---
page_id: connect-responses-amend-output
title: Amendment
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-amend-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_amend_output.htm
fetched_at: 2026-11-25
---

# Amendment

Output representation of the details of an amendment record.

## JSON Example

```
{
  "amendmenRecordId": "0Q0xx0000004NsSCAU",
  "errors": [
    {
      "errorCode": "REQUIRED_FIELD_MISSING",
      "errorMessage": "Specify a value for quantityChange, and try again."
    }
  ],
  "requestId": "16Pxx0000004NIy",
  "success": true
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `amendment​RecordId` | String | ID of the amendment record that’s created for a quote or an order. | Small, 62.0 | 62.0 |
| `errors` | [ARC Base Error](./connect-responses-assets-arc-error.md)[] | Error responses if the creation of an amendment record fails. | Small, 62.0 | 62.0 |
| `request​Id` | String | Request ID that’s used to track an async request. | Small, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-amend-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
