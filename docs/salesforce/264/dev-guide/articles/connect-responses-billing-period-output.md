---
page_id: connect-responses-billing-period-output
title: Billing Period
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-billing-period-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_billing_period_output.htm
fetched_at: 2026-11-25
---

# Billing Period

Output representation of the details of a specific billing period.

## JSON Example

```
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
| `resources` | [Resource Detail](./connect-responses-resource-detail-output.md)[] | List of usage resources within the billing period. | Big, 66.0 | 66.0 |
| `startDate` | String | Start date of the billing period. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-billing-period-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
