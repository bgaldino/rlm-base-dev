---
page_id: apex-connectapi-input-sequences-assignment
title: ConnectApi.SequencesAssignmentInputRepresentation
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-sequences-assignment.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-input-classes
legacy_page_id: apex_connectapi_input_sequences_assignment.htm
fetched_at: 2026-11-25
---

# ConnectApi.SequencesAssignmentInputRepresentation

The details of the target objects to which the sequence pattern values are assigned.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `sequencePolicyId` | String | ID of the sequence policy. | Optional | 65.0 |
| `shouldPublishPlatformEvent` | Boolean | Indicates whether to publish a platform event when a sequence is assigned to a target record (`true`) or not (`false`). | Optional | 65.0 |
| `targetObjectIds` | List<`String`> | List of records to which the sequence pattern values are assigned. | Required | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-sequences-assignment.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
