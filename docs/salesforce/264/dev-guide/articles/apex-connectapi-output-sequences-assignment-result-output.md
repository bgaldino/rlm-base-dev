---
page_id: apex-connectapi-output-sequences-assignment-result-output
title: ConnectApi.SequencesAssignmentResultOutputRepresentation
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-output-sequences-assignment-result-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-output-classes
legacy_page_id: apex_connectapi_output_sequences_assignment_result_output.htm
fetched_at: 2026-11-25
---

# ConnectApi.SequencesAssignmentResultOutputRepresentation

Output representation of the details of the assigned sequence values to target objects.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `errors` | List<`ConnectApi.SequenceErrorOutputRepresentation`> | Error encountered during the processing of the API request. | 65.0 |
| `isSuccess` | Boolean | Indicates whether the sequence pattern value was assigned (`true`) or not (`false`). | 65.0 |
| `sequencePatternValue` | String | Sequence pattern value assigned to the target object. | 65.0 |
| `sequencePolicyId` | String | ID of the sequence policy assigned to the target object. | 65.0 |
| `targetObjectId` | String | Record to which the sequence pattern value is assigned. | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-output-sequences-assignment-result-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
