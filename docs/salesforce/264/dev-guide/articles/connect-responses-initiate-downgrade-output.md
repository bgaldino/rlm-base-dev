---
page_id: connect-responses-initiate-downgrade-output
title: Initiate Downgrade Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-initiate-downgrade-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_initiate_downgrade_output.htm
fetched_at: 2026-11-25
---

# Initiate Downgrade Response

Output representation of the request to initiate a downgrade action.

## JSON Example

```
{
  "salesTransactionId": "0Q09Q000005IkEPSA0"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `salesTransactionId` | String | ID of the sales transaction that’s created by the downgrade action. | Small, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-initiate-downgrade-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
