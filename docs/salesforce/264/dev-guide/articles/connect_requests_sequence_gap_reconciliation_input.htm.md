---
page_id: connect_requests_sequence_gap_reconciliation_input.htm
title: Sequence Gap Reconciliation Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_sequence_gap_reconciliation_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Sequence Gap Reconciliation Input

Input representation of the details that are used to identify and reconcile gaps in
    sequence values based on the sequence policy or target object.

**JSON example**

: This example shows a sample request that specifies the list of sequence policies for gap
            reconciliation.

```
{
  "sequencePolicyIds": [
    "1vdxx0000000abc",
    "1vdxx0000000def"
  ]
}
```

          
: This example shows a sample request that specifies the target invoice object for gap
            reconciliation.

```
{
  "targetObjects": [
    "Invoice"
  ]
}
```

**Properties**

: 

- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `sequence​PolicyIds` | String[] | List of IDs of the sequence policies. | Required if the `targetObjects` property isn't specified. You must not specify both properties. | 65.0 |
| `target​Objects` | String[] | List of objects to which the policies are applied. Valid values are: `Invoice` `CreditMemo`—Available in API version 66.0 and later. | Required if the `sequencePolicyIds` property isn't specified. You must not specify both properties. | 65.0 |
