---
page_id: connect_resources_sequences_assignment.htm
title: Sequence Assignment (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_sequences_assignment.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Sequence Assignment (POST)

Assign sequence pattern values to objects based on the configured
      sequence policy.

    

## Special Access Rules

      
      

You need the Billing Admin permission set to use this API.

    

**Resource**

: 

```
/connect/sequences/actions/assign
```

**Resource example**

: 

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/sequences/actions/assign
```

**Available version**

: 65.0

**HTTP methods**

: POST

**Request body for POST**

: 

**JSON example**

: 

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

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `sequence​PolicyId` | String | ID of the sequence policy. | Optional | 65.0 |
| `shouldPublish​Platform​Event` | Boolean | Indicates whether to publish a platform event when a sequence is assigned to a target record (`true`) or not (`false`). | Optional | 65.0 |
| `target​ObjectIds` | String[] | List of records to which the sequence pattern values are assigned. | Required | 65.0 |

**Response body for POST**

: [Sequences Assignment](./connect_responses_sequences_assignment_output.htm.md)
