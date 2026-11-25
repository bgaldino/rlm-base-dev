---
page_id: connect-responses-tax-engine-log-output
title: Tax Engine Log
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-tax-engine-log-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_tax_engine_log_output.htm
fetched_at: 2026-11-25
---

# Tax Engine Log

Output representation of the logs that the tax engine generates.

## JSON Example

```
{
  "taxEngineLogs": [
    {
      "createdDate": "2022-03-09T10:55:38.000Z",
      "id": "3l1xx00000000PpAAI",
      "resultCode": "Success"
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `createdDate` | String | Date when the tax engine creates the log. | Big, 62.0 | 62.0 |
| `id` | String | ID of the tax engine log record. | Big, 62.0 | 62.0 |
| `resultCode` | String | Result code associated with the created log. | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-tax-engine-log-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
