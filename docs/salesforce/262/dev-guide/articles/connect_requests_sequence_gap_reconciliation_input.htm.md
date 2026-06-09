---
page_id: connect_requests_sequence_gap_reconciliation_input.htm
title: Sequence Gap Reconciliation Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_sequence_gap_reconciliation_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Sequence Gap Reconciliation Input

Input representation of the details that are used to identify and reconcile gaps in
sequence values based on the sequence policy or target object.

JSON example
:   This example shows a sample request that specifies the list of sequence policies for gap
    reconciliation.

    ```
    {
      "sequencePolicyIds": [
        "1vdxx0000000abc",
        "1vdxx0000000def"
      ]
    }
    ```
:   This example shows a sample request that specifies the target invoice object for gap
    reconciliation.

    ```
    {
      "targetObjects": [
        "Invoice"
      ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `sequence​PolicyIds` | String[] | List of IDs of the sequence policies. | Required if the `targetObjects` property isn't specified. You must not specify both properties. | 65.0 |
    | `target​Objects` | String[] | List of objects to which the policies are applied. Valid values are:   - `Invoice` - `CreditMemo`—Available in API   version 66.0 and later. | Required if the `sequencePolicyIds` property isn't specified. You must not specify both properties. | 65.0 |
