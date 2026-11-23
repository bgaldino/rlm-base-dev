---
page_id: connect_responses_consumption_source_detail_output.htm
title: Consumption Source Detail
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_consumption_source_detail_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Consumption Source Detail

Output representation of the details of a specific consumption source.

## JSON Example

```
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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_consumption_source_detail_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
