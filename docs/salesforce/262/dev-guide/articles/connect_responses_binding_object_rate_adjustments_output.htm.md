---
page_id: connect_responses_binding_object_rate_adjustments_output.htm
title: Binding Object Rate Adjustments
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_binding_object_rate_adjustments_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Binding Object Rate Adjustments

Output representation of the details of binding target rate adjustments.

JSON example
:   This example includes the details of binding target rate
    adjustments.

    ```
    {
      "negotiatedRateAdjustments": [
        {
          "lowerBound": 101,
          "name": null,
          "rateAdjustmentId": "1DMSB000001N3C74AK",
          "rateAdjustmentType": "Amount",
          "rateAdjustmentValue": 10,
          "tierUnitOfMeasure": "USD",
          "upperBound": null
        },
        {
          "lowerBound": 1,
          "name": null,
          "rateAdjustmentId": "1DMSB000001N3C64AK",
          "rateAdjustmentType": "Percentage",
          "rateAdjustmentValue": 30,
          "tierUnitOfMeasure": "USD",
          "upperBound": 100
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `lowerBound` | Double | Minimum quantity for the adjustment to be applicable. | Small, 65.0 | 65.0 |
| `name` | String | Name of the tier or binding object rate adjustment. | Small, 65.0 | 65.0 |
| `rateAdjustmentId` | String | ID of the binding object rate adjustment. | Small, 65.0 | 65.0 |
| `rateAdjustmentType` | String | Type of the binding object rate adjustment. | Small, 65.0 | 65.0 |
| `rateAdjustmentValue` | Double | Value of the binding object rate adjustment. | Small, 65.0 | 65.0 |
| `tierUnitOfMeasure` | String | Unit of measure that represents the tier or binding object rate adjustment. | Small, 65.0 | 65.0 |
| `upperBound` | Double | Maximum quantity for the adjustment to be applicable. | Small, 65.0 | 65.0 |
