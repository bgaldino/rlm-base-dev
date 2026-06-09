---
page_id: connect_responses_asset_detail_output.htm
title: Asset Detail
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_asset_detail_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Asset Detail

Output representation of the details of a specific asset.

JSON example
:   ```
    {
      "assets": [
        {
          "assetId": "ASSET1",
          "usageEntitlementAccountId": "1EA000000000001",
          "grantBindingTargetId": "1GB000000000001",
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
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `assetId` | String | Unique identifier of the related asset. | Big, 66.0 | 66.0 |
| `billingPeriods` | [Billing Period](./connect_responses_billing_period_output.htm.md "Output representation of the details of a specific billing period.")[] | List of billing periods for the asset. | Big, 66.0 | 66.0 |
| `grantBinding​TargetId` | String | ID of the object the consumption is bound to. | Big, 66.0 | 66.0 |
| `usageEntitlement​AccountId` | String | ID of the account that holds the usage entitlement. | Big, 66.0 | 66.0 |
