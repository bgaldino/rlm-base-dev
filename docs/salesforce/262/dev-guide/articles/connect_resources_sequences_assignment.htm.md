---
page_id: connect_resources_sequences_assignment.htm
title: Sequence Assignment (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_sequences_assignment.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Sequence Assignment (POST)

Assign sequence pattern values to objects based on the configured
sequence policy.

## Special Access Rules

You need the Billing Admin permission set to use this API.

Resource
:   ```
    /connect/sequences/actions/assign
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/sequences/actions/assign
    ```

Available version
:   65.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "targetObjectIds": [
            "3ttxx00000005nhAAA",
            "3ttxx00000006bhAAA"
          ],
          "sequencePolicyId": "1Vdxx0000004CFU"
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `sequence​PolicyId` | String | ID of the sequence policy. | Optional | 65.0 |
        | `shouldPublish​Platform​Event` | Boolean | Indicates whether to publish a platform event when a sequence is assigned to a target record (`true`) or not (`false`). | Optional | 65.0 |
        | `target​ObjectIds` | String[] | List of records to which the sequence pattern values are assigned. | Required | 65.0 |

Response body for POST
:   [Sequences Assignment](./connect_responses_sequences_assignment_output.htm.md "Output representation with the status of the assigned sequence pattern values.")
