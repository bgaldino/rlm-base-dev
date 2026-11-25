---
page_id: connect-responses-rate-adjustments-output
title: Rate Adjustments
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-rate-adjustments-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_rate_adjustments_output.htm
fetched_at: 2026-11-25
---

# Rate Adjustments

Output representation of the details of a rate adjustment.

## JSON Example

```
      "rateAdjustments": [
        {
           "fields": {},
           "lowerBound": 0.0,
           "name": null,
           "negotiatedRateAdjustmentId": null,
           "rateAdjustmentId": "1ENxx0000004C9BGAU",
           "rateAdjustmentType": "Percentage",
           "rateAdjustmentValue": 10.0,
           "tierUnitOfMeasure": "USD",
           "upperBound": 50.0
        }
    ]
```

If the `negotiable` property value that’s associated with a rate card entry is blank, then the data is derived from Product Catalog Management. If it isn’t blank, then the data is derived from Rate Management.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `fields` | Map<String, [Fields Response](./connect-responses-fields-output.md)> | List of optional fields and their values that belong to the rate adjustment object. | Big, 63.0 | 63.0 |
| `lowerBound` | Double | Minimum quantity for the adjustment to be applicable. | Small, 63.0 | 63.0 |
| `name` | String | Name of the tier. | Small, 63.0 | 63.0 |
| `negotiatedRate​Adjustment​Id` | String | ID of the negotiated rate adjustment. | Small, 63.0 | 63.0 |
| `rateAdjustment​Id` | String | ID of the rate adjustment. | Small, 63.0 | 63.0 |
| `rateAdjustment​Type` | String | Type of the rate adjustment. | Small, 63.0 | 63.0 |
| `rateAdjustment​Value` | Double | Value of the rate adjustment. | Small, 63.0 | 63.0 |
| `tierUnitOf​Measure` | String | Unit of measure representing the tier. | Small, 63.0 | 63.0 |
| `upperBound` | Double | Maximum quantity for the adjustment to be applicable. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-rate-adjustments-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
