---
page_id: connect_requests_delete_ramp_deal_input.htm
title: Delete Ramp Deal Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_delete_ramp_deal_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Delete Ramp Deal Input

Input representation of the request to delete a ramp deal.

**JSON example**

: 

```
{
  "rampDealIds": [
    "0Q0xx0000004CDxCAM",
    "0QLxx0000004CSOGA2"
  ]
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `rampDeal​Ids` | String[] | Ramp identifier on the quote line item or order item. | Required | 62.0 |
