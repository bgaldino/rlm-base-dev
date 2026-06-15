---
page_id: connect_requests_sequences_assignment_input.htm
title: Sequences Assignment Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_sequences_assignment_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Sequences Assignment Input

Input representation of the details of the target objects to which the sequence pattern
values are assigned.

JSON example
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
