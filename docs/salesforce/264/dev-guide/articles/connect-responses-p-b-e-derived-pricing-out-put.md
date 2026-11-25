---
page_id: connect-responses-p-b-e-derived-pricing-out-put
title: PBE Derived Pricing
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-p-b-e-derived-pricing-out-put.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-responses
legacy_page_id: connect_responses_p_b_e_derived_pricing_out_put.htm
fetched_at: 2026-11-25
---

# PBE Derived Pricing

Output representation of the response that includes the source product for the Price Book Entry (PBE) derived pricing.

## JSON Example

```
{
"productId":"01txx0000006i2SAAQ",
"pricebookEntryId":"01uxx0000008yYcAAI",
"effectiveFrom":"2020-01-01T22:53:20.000Z",
"effectiveTo":"2021-01-01T22:53:20.000Z"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Pricing Error Response](./connect-responses-pricing-error-response.md)[] | Displays the error while processing the request. | Small, 61.0 | 61.0 |
| `isSuccess` | Boolean | Indicates whether the request is successful (`true`) or not (`false`). | Small, 61.0 | 61.0 |
| `source​ProceductId` | String | ID of the source product. | Small, 61.0 | 61.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-p-b-e-derived-pricing-out-put.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
