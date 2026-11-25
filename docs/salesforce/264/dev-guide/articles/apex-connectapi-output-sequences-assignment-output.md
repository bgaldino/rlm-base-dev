---
page_id: apex-connectapi-output-sequences-assignment-output
title: ConnectApi.SequencesAssignmentOutputRepresentation
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-output-sequences-assignment-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-output-classes
legacy_page_id: apex_connectapi_output_sequences_assignment_output.htm
fetched_at: 2026-11-25
---

# ConnectApi.SequencesAssignmentOutputRepresentation

Output representation showing the status of the assigned sequence pattern values.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `errors` | List<[`ConnectApi.SequenceErrorOutputRepresentation`](./apex-connectapi-output-sequence-error-output.md)> | Error encountered during the processing of the API request. | 65.0 |
| `sequencesAssignment` | List<[`ConnectApi.SequencesAssignmentResultOutputRepresentation`](./apex-connectapi-output-sequences-assignment-result-output.md)> | Details of the sequence pattern values assignment. | 65.0 |
| `status` | `SequenceResponseStatusEnum` | Status of the sequence policy assignment. Valid values are `PartialSuccess`, `Success`, or `Failed`. | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-output-sequences-assignment-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
