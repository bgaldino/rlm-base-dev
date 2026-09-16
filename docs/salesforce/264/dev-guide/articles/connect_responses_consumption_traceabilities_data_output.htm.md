---
page_id: connect_responses_consumption_traceabilities_data_output.htm
title: Consumption Traceabilities Data
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_consumption_traceabilities_data_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Consumption Traceabilities Data

Output representation of the list of asset details.

      
        
          

**JSON example**

          
: 
            

```
{
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
    ]
  }
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `assets` | [Asset Detail](./connect_responses_asset_detail_output.htm.md)[] | List of assets for the specified liable summaries. | Big, 66.0 | 66.0 |
