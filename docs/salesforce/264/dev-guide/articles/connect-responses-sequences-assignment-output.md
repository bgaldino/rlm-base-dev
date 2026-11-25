---
page_id: connect-responses-sequences-assignment-output
title: Sequences Assignment
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-sequences-assignment-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_sequences_assignment_output.htm
fetched_at: 2026-11-25
---

# Sequences Assignment

Output representation with the status of the assigned sequence pattern values.

## JSON Example

This example shows a sample successful response.

```
{
  "errors": null,
  "sequencesAssignment": [
    {
      "errors": null,
      "isSuccess": true,
      "sequencePatternValue": "INV-1234-2025-04-12-001",
      "targetObjectId": "3ttxx000000085dAAA"
    }
  ],
  "status": "Success"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Sequence Error](./connect-responses-sequence-error-output.md)[] | Error encountered during the processing of the API request. | Big, 65.0 | 65.0 |
| `sequencesAssignment` | [Sequences Assignment Result](./connect-responses-sequences-assignment-result-output.md)[] | Details of the sequence pattern values assignment. | Big, 65.0 | 65.0 |
| `status` | String | Status of the sequence policy assignment. Valid values are `PartialSuccess`, `Success`, or `Failed`. | Big, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-sequences-assignment-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
