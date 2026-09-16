---
page_id: connect_requests_sequences_assignment_input.htm
title: Sequences Assignment Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_sequences_assignment_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Sequences Assignment Input

Input representation of the details of the target objects to which the sequence pattern
    values are assigned.

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
