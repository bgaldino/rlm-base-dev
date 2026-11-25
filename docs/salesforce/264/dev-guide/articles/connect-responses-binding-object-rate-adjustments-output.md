---
page_id: connect-responses-binding-object-rate-adjustments-output
title: Binding Object Rate Adjustments
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-binding-object-rate-adjustments-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_binding_object_rate_adjustments_output.htm
fetched_at: 2026-11-25
---

# Binding Object Rate Adjustments

Output representation of the details of binding target rate adjustments.

## JSON Example

This example includes the details of binding target rate adjustments.

```
{
  "negotiatedRateAdjustments": [
    {
      "lowerBound": 101,
      "name": null,
      "rateAdjustmentId": "1DMSB000001N3C74AK",
      "rateAdjustmentType": "Amount",
      "rateAdjustmentValue": 10,
      "tierUnitOfMeasure": "USD",
      "upperBound": null
    },
    {
      "lowerBound": 1,
      "name": null,
      "rateAdjustmentId": "1DMSB000001N3C64AK",
      "rateAdjustmentType": "Percentage",
      "rateAdjustmentValue": 30,
      "tierUnitOfMeasure": "USD",
      "upperBound": 100
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `lowerBound` | Double | Minimum quantity for the adjustment to be applicable. | Small, 65.0 | 65.0 |
| `name` | String | Name of the tier or binding object rate adjustment. | Small, 65.0 | 65.0 |
| `rateAdjustmentId` | String | ID of the binding object rate adjustment. | Small, 65.0 | 65.0 |
| `rateAdjustmentType` | String | Type of the binding object rate adjustment. | Small, 65.0 | 65.0 |
| `rateAdjustmentValue` | Double | Value of the binding object rate adjustment. | Small, 65.0 | 65.0 |
| `tierUnitOfMeasure` | String | Unit of measure that represents the tier or binding object rate adjustment. | Small, 65.0 | 65.0 |
| `upperBound` | Double | Maximum quantity for the adjustment to be applicable. | Small, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-binding-object-rate-adjustments-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
