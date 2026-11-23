---
page_id: connect_responses_binding_object_rate_output.htm
title: Binding Object Rate
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_binding_object_rate_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Binding Object Rate

Output representation of the details of Binding Object Rates object or Asset Rates object.

## JSON Example

This example includes the details of a binding object rate.

```
{
  "bindingObjectRate": {
    "id": "1QNSB0000001JyH4AU,1QNSB0000001JyI4AU",
    "negotiatedRate": null,
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
    ],
    "rate": 100,
    "rateCardEntryId": "1CJSB000000207R4AQ,1CJSB000000207S4AQ",
    "rateUnitOfMeasureName": "USD"
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the `Binding Object Rate Card Entry` or `Asset Rate Card Entry` object. | Big, 65.0 | 65.0 |
| `negotiated​Rate` | Double | Negotiated rate available in the `Binding Object Rate Card Entry` or `Asset Rate Card Entry` object. | Big, 65.0 | 65.0 |
| `negotiatedRate​Adjustments` | [Binding Object Rate Adjustments](./connect_responses_binding_object_rate_adjustments_output.htm.md "Output representation of the details of binding target rate adjustments.")[] | List of rate adjustments available in the `Binding Object Rate Adjustment` or `Asset Rate Adjustment`. | Big, 65.0 | 65.0 |
| `rate` | Double | Rate of the rate card entry associated to the `Binding Object Rate Card Entry` or `Asset Rate Card Entry` object. | Big, 65.0 | 65.0 |
| `rateCard​EntryId` | String | ID of the rate card entry associated to the `Binding Object Rate Card Entry` or `Asset Rate Card Entry` object. | Big, 65.0 | 65.0 |
| `rateUnitOf​MeasureName` | String | Rate unit of measure of the rates. | Big, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_binding_object_rate_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
