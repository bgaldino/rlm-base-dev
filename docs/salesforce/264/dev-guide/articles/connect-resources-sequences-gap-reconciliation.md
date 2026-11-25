---
page_id: connect-resources-sequences-gap-reconciliation
title: Sequence Gap Reconciliation (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-sequences-gap-reconciliation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_sequences_gap_reconciliation.htm
fetched_at: 2026-11-25
---

# Sequence Gap Reconciliation (POST)

Restore a missing sequence value identified by using this API in gapless-enabled sequences. This sequence value can be used later in the subsequent sequence policy numbering, ensuring there are no gaps.

## Special Access Rules

You need the Billing Admin permission set to use this API.

## Resource

```
/connect/sequences/gap-reconciliation
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/sequences/gap-reconciliation
```

## Available Version

65.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

This example shows a sample request that specifies the list of sequence policies for gap reconciliation.

```
{
  "sequencePolicyIds": [
    "1vdxx0000000abc",
    "1vdxx0000000def"
  ]
}
```

This example shows a sample request that specifies the target invoice object for gap reconciliation.

```
{
  "targetObjects": [
    "Invoice"
  ]
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `sequence​PolicyIds` | String[] | List of IDs of the sequence policies. | Required if the `targetObjects` property isn’t specified. You must not specify both properties. | 65.0 |
| `target​Objects` | String[] | List of objects to which the policies are applied. Valid values are `Invoice`; or `CreditMemo`—Available in API version 66.0 and later. | Required if the `sequencePolicyIds` property isn’t specified. You must not specify both properties. | 65.0 |

## Response Body for POST

[Sequence Gap Reconciliation](./connect-responses-sequence-gap-reconciliation-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-sequences-gap-reconciliation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
