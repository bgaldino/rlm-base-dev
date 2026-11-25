---
page_id: connect-resources-sequences-assignment
title: Sequence Assignment (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-sequences-assignment.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_sequences_assignment.htm
fetched_at: 2026-11-25
---

# Sequence Assignment (POST)

Assign sequence pattern values to objects based on the configured sequence policy.

## Special Access Rules

You need the Billing Admin permission set to use this API.

## Resource

```
/connect/sequences/actions/assign
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/sequences/actions/assign
```

## Available Version

65.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
  "targetObjectIds": [
    "3ttxx00000005nhAAA",
    "3ttxx00000006bhAAA"
  ],
  "sequencePolicyId": "1Vdxx0000004CFU"
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `sequence​PolicyId` | String | ID of the sequence policy. | Optional | 65.0 |
| `shouldPublish​Platform​Event` | Boolean | Indicates whether to publish a platform event when a sequence is assigned to a target record (`true`) or not (`false`). | Optional | 65.0 |
| `target​ObjectIds` | String[] | List of records to which the sequence pattern values are assigned. | Required | 65.0 |

## Response Body for POST

[Sequences Assignment](./connect-responses-sequences-assignment-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-sequences-assignment.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
