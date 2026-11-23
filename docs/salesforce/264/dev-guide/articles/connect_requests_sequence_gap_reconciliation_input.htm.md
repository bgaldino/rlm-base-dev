---
page_id: connect_requests_sequence_gap_reconciliation_input.htm
title: Sequence Gap Reconciliation Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_sequence_gap_reconciliation_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-11-23
---

# Sequence Gap Reconciliation Input

Input representation of the details that are used to identify and reconcile gaps in sequence values based on the sequence policy or target object.

## JSON Example

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

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `sequence​PolicyIds` | String[] | List of IDs of the sequence policies. | Required if the `targetObjects` property isn't specified. You must not specify both properties. | 65.0 |
| `target​Objects` | String[] | List of objects to which the policies are applied. Valid values are `Invoice`; or `CreditMemo`—Available in API version 66.0 and later. | Required if the `sequencePolicyIds` property isn't specified. You must not specify both properties. | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_sequence_gap_reconciliation_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
