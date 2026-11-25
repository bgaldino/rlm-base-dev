---
page_id: connect-requests-sequences-assignment-input
title: Sequences Assignment Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-sequences-assignment-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_sequences_assignment_input.htm
fetched_at: 2026-11-25
---

# Sequences Assignment Input

Input representation of the details of the target objects to which the sequence pattern values are assigned.

## JSON Example

```
{
  "targetObjectIds": [
    "3ttxx00000005nhAAA",
    "3ttxx00000006bhAAA"
  ],
  "sequencePolicyId": "1Vdxx0000004CFU"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `sequence​PolicyId` | String | ID of the sequence policy. | Optional | 65.0 |
| `shouldPublish​Platform​Event` | Boolean | Indicates whether to publish a platform event when a sequence is assigned to a target record (`true`) or not (`false`). | Optional | 65.0 |
| `target​ObjectIds` | String[] | List of records to which the sequence pattern values are assigned. | Required | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-sequences-assignment-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
