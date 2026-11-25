---
page_id: apex-connectapi-input-sequence-gap-reconciliation
title: ConnectApi.SequenceGapReconciliationInputRepresentation
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-sequence-gap-reconciliation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-input-classes
legacy_page_id: apex_connectapi_input_sequence_gap_reconciliation.htm
fetched_at: 2026-11-25
---

# ConnectApi.SequenceGapReconciliationInputRepresentation

The details of the input used to identify and reconcile gaps in sequence values based on the sequence policy or target object.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `sequencePolicyIds` | List<`String`> | List of IDs of the sequence policies. | Required if the `targetObjects` property isn’t specified. You must not specify both properties. | 65.0 |
| `targetObjects` | List<`String`> | List of objects to which the policies are applied. | Required if the `sequencePolicyIds` property isn’t specified. You must not specify both properties. | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-sequence-gap-reconciliation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
