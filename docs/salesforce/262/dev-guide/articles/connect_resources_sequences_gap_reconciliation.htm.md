---
page_id: connect_resources_sequences_gap_reconciliation.htm
title: Sequence Gap Reconciliation (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_sequences_gap_reconciliation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Sequence Gap Reconciliation (POST)

Restore a missing sequence value identified by using this API in
gapless-enabled sequences. This sequence value can be used later in the subsequent sequence
policy numbering, ensuring there are no gaps.

## Special Access Rules

You need the Billing Admin permission set to use this API.

Resource
:   ```
    /connect/sequences/gap-reconciliation
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/sequences/gap-reconciliation
    ```

Available version
:   65.0

HTTP methods
:   POST

Request body for POST
:   JSON example
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

Response body for POST
:   [Sequence Gap Reconciliation](./connect_responses_sequence_gap_reconciliation_output.htm.md "Output representation of the details of the sequence gap reconciliation.")
