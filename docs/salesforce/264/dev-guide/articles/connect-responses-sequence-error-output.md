---
page_id: connect-responses-sequence-error-output
title: Sequence Error
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-sequence-error-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_sequence_error_output.htm
fetched_at: 2026-11-25
---

# Sequence Error

Output representation of the error response that’s associated with a request to create or update a sequence policy, or assign sequences.

## JSON Example

This example shows a sample error response.

```
{
  "error": {
    "errorCode": "INVALID_INPUT",
    "message": "Specify a valid selectionLogic."
  },
  "isSuccess": false,
  "sequencePolicyId": null
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code for the resultant error. | Big, 65.0 | 65.0 |
| `message` | String | Error message for the resultant error. | Big, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-sequence-error-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
