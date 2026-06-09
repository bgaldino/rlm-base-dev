---
page_id: connect_responses_consumption_source_detail_output.htm
title: Consumption Source Detail
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_consumption_source_detail_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Consumption Source Detail

Output representation of the details of a specific consumption source.

JSON example
:   ```
    {
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
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `cmtAssetRatable​SummaryId` | String | ID for querying rating waterfall. | Big, 66.0 | 66.0 |
| `commitRate` | Double | Net unit rate at which drawdown is done for commitment products. | Big, 66.0 | 66.0 |
| `consumption​SourceId` | String | Object on which the consumption was recorded. | Big, 66.0 | 66.0 |
| `consumption​Unit` | Double | Recorded quantity of consumption. | Big, 66.0 | 66.0 |
| `targetRate` | Double | Input unit rate which is used for commitment products. | Big, 66.0 | 66.0 |
