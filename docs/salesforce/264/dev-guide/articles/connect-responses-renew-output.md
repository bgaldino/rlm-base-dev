---
page_id: connect-responses-renew-output
title: Renewal
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-renew-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_renew_output.htm
fetched_at: 2026-11-25
---

# Renewal

Output representation of the details of a renewal record.

## JSON Example

```
{
  "renewalRecordId": "0Q0xx0000004NsSCAU",
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
| `errors` | [ARC Base Error](./connect-responses-assets-arc-error.md)[] | Error responses if the creation of a renewal record fails. | Small, 62.0 | 62.0 |
| `renewal​RecordId` | String | ID of the renewal record that’s created for the Quote or Order record. | Small, 62.0 | 62.0 |
| `requestId` | String | Request ID that’s used to track the async request. | Small, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-renew-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
