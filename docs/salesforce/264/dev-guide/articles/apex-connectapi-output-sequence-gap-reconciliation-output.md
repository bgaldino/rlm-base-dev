---
page_id: apex-connectapi-output-sequence-gap-reconciliation-output
title: ConnectApi.SequenceGapReconciliationOutputRepresentation
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-output-sequence-gap-reconciliation-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-output-classes
legacy_page_id: apex_connectapi_output_sequence_gap_reconciliation_output.htm
fetched_at: 2026-11-25
---

# ConnectApi.SequenceGapReconciliationOutputRepresentation

Output representation of the details of the sequence gap reconciliation.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `error` | [`ConnectApi.SequenceGapReconciliationErrorOutputRepresentation`](./apex-connectapi-output-sequence-gap-reconciliation-error-output.md) | List of errors encountered during the processing of the API request. | 65.0 |
| `jobId` | String | Unique identifier assigned to sequence gap reconciliation asynchronous process. | 65.0 |
| `sequencePolicyIds` | List<`String`> | List of IDs of the sequence policies. | 65.0 |
| `status` | `StatusEnum` | The status of sequence reconciliation API request. Valid values are `Submitted` or `NotSubmitted`. | 65.0 |
| `submittedAt` | String | Date and time when the reconciliation request was submitted to the async job. | 65.0 |
| `targetObjects` | List<`String`> | List of objects to which the policies are applied. | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-output-sequence-gap-reconciliation-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
