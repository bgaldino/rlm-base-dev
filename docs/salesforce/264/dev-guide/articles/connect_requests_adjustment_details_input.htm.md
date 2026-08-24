---
page_id: connect_requests_adjustment_details_input.htm
title: Adjustment Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_adjustment_details_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Adjustment Details Input

Input representation of the adjustment details.

**JSON example**

          
: 
            

```

   "pricingElement": {
     "adjustments": [{
     "AdjustmentValue": "15.00",
     "AdjustmentType": "Percentage"
  }],
   "description": null,
   "elementType": "VolumeDiscount",
   "name": "Volume Discount"
 }
```

          

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `adjustments` | Map<String, Object>[] | Details of the pricing element. | Optional | 60.0 |
| `description` | String | Description of the pricing element. | Optional | 60.0 |
| `elementType` | String | Type of the pricing element. | Optional | 60.0 |
| `name` | String | Name of the pricing element. | Optional | 60.0 |
