---
page_id: connect-responses-sequence-gap-reconciliation-output
title: Sequence Gap Reconciliation
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-sequence-gap-reconciliation-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_sequence_gap_reconciliation_output.htm
fetched_at: 2026-11-25
---

# Sequence Gap Reconciliation

Output representation of the details of the sequence gap reconciliation.

## JSON Example

This example shows a sample successful response.

```
{
  "jobId": "0B1xx0000006P12",
  "sequencePolicyIds": [
    "1vdxx0000000uyr",
    "1vdxx0000000lrf"
  ],
  "targetObjects": [
    "Invoice"
  ],
  "status": "Submitted",
  "submittedAt": "2025-06-05T09:12:28Z",
  "error": {}
}
```

This example shows a sample error response for an invalid input.

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
    "message": "Missing required field in the request."
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Sequence Gap Reconciliation Error](./connect-responses-sequence-gap-reconciliation-error-output.md)[] | List of errors encountered during the processing of the API request. | Big, 65.0 | 65.0 |
| `jobId` | String | Unique identifier assigned to the sequence gap reconciliation asynchronous process. | Big, 65.0 | 65.0 |
| `sequence​PolicyIds` | String[] | List of IDs of the sequence policies. | Big, 65.0 | 65.0 |
| `status` | String | Status of the sequence gap reconciliation API request. Valid values are `Submitted` or `NotSubmitted`. | Big, 65.0 | 65.0 |
| `submitted​At` | String | Date and time when the reconciliation request was submitted to the async job. | Big, 65.0 | 65.0 |
| `target​Objects` | String[] | List of objects to which the policies are applied. | Big, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-sequence-gap-reconciliation-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
