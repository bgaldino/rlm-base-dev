---
page_id: connect_requests_pricing_versioning_revise_details_input.htm
title: Pricing Versioned Revision Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_pricing_versioning_revise_details_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_requests.htm
fetched_at: 2026-06-09
---

# Pricing Versioned Revision Details Input

Input representation of the versioned revision details.

JSON example
:   This example shows the input for versioned revision details for attribute-based
    adjustment.
:   ```
    {
            "entityName":"AttributeBasedAdjustment",
            "id":"entityId",
            "priceAdjustmentId":"priceAdjustmentScheduleId",
            "productId":"ProductId",
            "productSellingModelId":"PsmId",
            "adjustmentType":"AdjustmentType",
            "adjustmentValue":"AdjustmentValue(Numeric)"",
            "effectiveFrom":"EffectiveFrom date",
            "effectiveTo":"EffectiveTo Date",
            "additionalFieldsToValueMap":{
            "attributeBasedAdjRuleId":"AttributeBasedAdjRuleId"
    }
    }
    ```
:   This example shows the input for versioned revision details for bundle-based
    adjustment.
:   ```
     {
            "entityName": "BundleBasedAdjustment",
            "id": "entityId",
            "priceAdjustmentScheduleId": "priceAdjustmentScheduleId",
            "productId": "ProductId",
            "productSellingModelId": "PsmId",
            "adjustmentType": "AdjustmentType",
            "adjustmentValue": "AdjustmentValue(Numeric)",
            "effectiveFrom":"EffectiveFrom date",
            "effectiveTo":"EffectiveTo Date",
            "additionalFieldsToValueMap": {
              "rootBundleId": "RootBundleId",
              "parentProductId": "ParentProductId"
            }
     }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `additional​Fields​ToValue​Map` | Map<String, String> | Map containing the additional fields specific to the entity. | Optional | 60.0 |
    | `adjustment​Type` | String | Adjustment type such as, percentage, amount, or override. | Required | 60.0 |
    | `adjustment​Value` | String | Value for the adjustment. | Required | 60.0 |
    | `effective​From` | String | Date from when the adjustment is effective. | Required | 60.0 |
    | `effective​To` | String | Date until when the adjustment is effective. | Optional | 60.0 |
    | `entity​Name` | String | Name of the entity such as AttributeBasedAdjustment entity or BundleBasedAdjustment entity. | Required | 60.0 |
    | `id` | String | ID of the record. | Required | 60.0 |
    | `price​Adjustment​ScheduleId` | String | ID of the price adjustment schedule record. | Required | 60.0 |
    | `productId` | String | Product ID of the record. | Required | 60.0 |
    | `product​Selling​ModelId` | String | Product selling model ID associated to the record. | Optional | 60.0 |
