---
page_id: connect-responses-batch-metadata-output
title: Batch Metadata
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-batch-metadata-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_batch_metadata_output.htm
fetched_at: 2026-11-25
---

# Batch Metadata

Output representation of the metadata that describes the available batches for a context.

## JSON Example

This example response shows the metadata that describes the available batches for a context.

```
{
  "parentContextId": "008d27d7-e004-4906-a949-ee7d7c323c77",
  "totalBatches": 3,
  "batchId": "b1f2c3d4-5678-90ab-cdef-1234567890ab"
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `batchId` | String | ID of the batch for the context. | Small, 68.0 | 68.0 |
| `parentContextId` | String | ID of the parent context that the batches belong to. | Small, 68.0 | 68.0 |
| `totalBatches` | Integer | Total number of batches available for the context. | Small, 68.0 | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-batch-metadata-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
