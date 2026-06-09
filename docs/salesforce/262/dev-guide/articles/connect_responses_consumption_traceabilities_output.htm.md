---
page_id: connect_responses_consumption_traceabilities_output.htm
title: Consumption Traceabilities
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_consumption_traceabilities_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Consumption Traceabilities

Output representation of the overage and resource drawdown details.

JSON example
:   ```
    {
      "success": true,
      "data": {
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
        ],
        "error": null
      }
    }
    ```

| zProperty Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `data` | [Consumption Traceabilities Data](./connect_responses_consumption_traceabilities_data_output.htm.md "Output representation of the list of asset details.")[] | Payload that contains the traceability details. | Big, 66.0 | 66.0 |
| `error` | [Generic Error Details](./connect_responses_generic_error_output.htm.md "Output representation of the error details encountered during the API request.")[] | Error details if the request isn't successful. | Big, 66.0 | 66.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Big, 66.0 | 66.0 |
