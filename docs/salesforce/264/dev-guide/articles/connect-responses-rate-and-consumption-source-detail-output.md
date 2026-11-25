---
page_id: connect-responses-rate-and-consumption-source-detail-output
title: Rate and Consumption Source Detail
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-rate-and-consumption-source-detail-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_rate_and_consumption_source_detail_output.htm
fetched_at: 2026-11-25
---

# Rate and Consumption Source Detail

Output representation of the details of a specific rate and its consumption source.

## JSON Example

```
{
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
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `consumptionSource​Details` | [Consumption Source Detail](./connect-responses-consumption-source-detail-output.md)[] | Details on the consumption source. | Big, 66.0 | 66.0 |
| `endDate` | String | End date for the specific rate period. | Big, 66.0 | 66.0 |
| `netUnit​Rate` | Double | Net unit rate. | Big, 66.0 | 66.0 |
| `overageAmt` | Double | Amount for the overage quantity. | Big, 66.0 | 66.0 |
| `overageQty` | Double | Quantity of consumption that was rated as overage. | Big, 66.0 | 66.0 |
| `ratable​SummaryId` | String | Unique ID for the summary used in rating. | Big, 66.0 | 66.0 |
| `ratable​SummaryStatus` | String | Status of ratable summary. | Big, 66.0 | 66.0 |
| `rateUomId` | String | Unit of measure for the rate. | Big, 66.0 | 66.0 |
| `rateUomName` | String | Name of the rate unit of measure | Big, 66.0 | 66.0 |
| `ratingExecution​Id` | String | Execution ID of the rating. | Big, 66.0 | 66.0 |
| `sourceUsage​ResourceId` | String | ID of the source usage resource. | Big, 66.0 | 66.0 |
| `sourceUsage​ResourceName` | String | Name of the source usage resource. | Big, 66.0 | 66.0 |
| `startDate` | String | Start date for the specific rate period. | Big, 66.0 | 66.0 |
| `total​Consumption` | Double | Total quantity consumed for this rate. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-rate-and-consumption-source-detail-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
