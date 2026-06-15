---
page_id: connect_responses_billing_period_output.htm
title: Billing Period
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_billing_period_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Billing Period

Output representation of the details of a specific billing period.

JSON example
:   ```
    {
      "billingPeriods": [
        {
          "startDate": "2025-01-01",
          "endDate": "2025-01-31",
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
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `endDate` | String | End date of the billing period. | Big, 66.0 | 66.0 |
| `resources` | [Resource Detail](./connect_responses_resource_detail_output.htm.md "Output representation of the details of a specific usage resource.")[] | List of usage resources within the billing period. | Big, 66.0 | 66.0 |
| `startDate` | String | Start date of the billing period. | Big, 66.0 | 66.0 |
