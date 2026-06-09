---
page_id: connect_requests_adjustment_details_input.htm
title: Adjustment Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_adjustment_details_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_requests.htm
fetched_at: 2026-06-09
---

# Adjustment Details Input

Input representation of the adjustment details.

JSON example
:   ```
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

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `adjustments` | Map<String, Object>[] | Details of the pricing element. | Optional | 60.0 |
    | `description` | String | Description of the pricing element. | Optional | 60.0 |
    | `elementType` | String | Type of the pricing element. | Optional | 60.0 |
    | `name` | String | Name of the pricing element. | Optional | 60.0 |
