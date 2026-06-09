---
page_id: connect_responses_resource_detail_output.htm
title: Resource Detail
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_resource_detail_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Resource Detail

Output representation of the details of a specific usage resource.

JSON example
:   ```
    {
      "resources": [
        {
          "liableSummaryId": "1HG000000000001",
          "usageResourceId": "1BX000000000004",
          "usageResourceName": "SF Credits",
          "usageResourceUomId": "1UM000000000001",
          "usageResourceUomUnitCode": "CREDIT",
          "resourceTotalOverageQuantity": 333.33,
          "resourceTotalOverageAmount": 333.33,
          "resourceTotalConsumption": 1500,
          "rateAndConsumptionSources": [
            {
              "startDate": "2025-01-01",
              "endDate": "2025-01-31",
              "rateUomId": "USD",
              "ratableSummaryId": "URS3",
              "ratingExecutionId": "1RE000000000001",
              "overageQuantity": 333.33,
              "overageAmount ": 333.33,
              "totalConsumption": 1500,
              "netUnitRate": 1,
              "consumptionSources": [
                {
                  "consumptionSourceId": "1AE000000000001",
                  "consumptionUnit": 500
                },
                {
                  "consumptionSourceId": "1CO000000000001",
                  "consumptionUnit": 375,
                  "commitRate": 1.5,
                  "targetRate": 2,
                  "cmtAssetRatableSummaryId": "URSCARID1"
                },
                {
                  "consumptionSourceId": "1CO000000000002",
                  "consumptionUnit": 125,
                  "commitRate": 0.75,
                  "targetRate": 1,
                  "cmtAssetRatableSummaryId": "URSCARID2"
                }
              ]
            }
          ]
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `liableSummaryId` | String | Unique identifier for the consumption summary. | Big, 66.0 | 66.0 |
| `liableSummary​Status` | String | Status of liable summary. | Big, 66.0 | 66.0 |
| `rateAnd​Consumption​Sources` | [Rate And Consumption Source Detail](./connect_responses_rate_and_consumption_source_detail_output.htm.md "Output representation of the details of a specific rate and its consumption source.")[] | Details on rates and consumption sources. | Big, 66.0 | 66.0 |
| `resourceTotal​Consumption` | Double | Total quantity of consumption for the resource. | Big, 66.0 | 66.0 |
| `resourceTotal​OverageAmount` | Double | Total amount for the overage. | Big, 66.0 | 66.0 |
| `resourceTotal​OverageQuantity` | Double | Total overage quantity. | Big, 66.0 | 66.0 |
| `usageResource​Id` | String | ID of the specific usage resource. | Big, 66.0 | 66.0 |
| `usageResource​Name` | String | Name of the usage resource. | Big, 66.0 | 66.0 |
| `usageResource​UomId` | String | Unit of measure ID for the usage resource. | Big, 66.0 | 66.0 |
| `usageResource​UomUnitCode` | String | Unit of measure code for the usage resource. | Big, 66.0 | 66.0 |
