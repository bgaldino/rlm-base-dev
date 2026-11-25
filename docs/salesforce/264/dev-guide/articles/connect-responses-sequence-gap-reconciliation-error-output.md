---
page_id: connect-responses-sequence-gap-reconciliation-error-output
title: Sequence Gap Reconciliation Error
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-sequence-gap-reconciliation-error-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_sequence_gap_reconciliation_error_output.htm
fetched_at: 2026-11-25
---

# Sequence Gap Reconciliation Error

Output representation of the errors encountered during the processing of the API request.

## JSON Example

This example shows a sample error response.

```
{
  "jobId": "",
  "sequencePolicyIds": [
    "1vdxx0000000abc",
    "1vdxx0000000def"
  ],
  "targetObjects": [
    "Invoice"
  ],
  "status": "NotSubmitted",
  "submittedAt": "",
  "error": {
    "errorCode": "INVALID_INPUT",
    "message": "Specify a value for either sequencePolicyIds or targetObjects."
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error​Code` | String | Code for the resultant error. | Big, 65.0 | 65.0 |
| `error​Message` | String | Error message for the resultant error. | Big, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-sequence-gap-reconciliation-error-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
