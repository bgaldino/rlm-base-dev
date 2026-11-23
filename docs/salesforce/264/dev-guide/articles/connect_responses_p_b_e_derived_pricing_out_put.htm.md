---
page_id: connect_responses_p_b_e_derived_pricing_out_put.htm
title: PBE Derived Pricing
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_p_b_e_derived_pricing_out_put.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-11-23
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
| `error` | [Pricing Error Response](./connect_responses_pricing_error_response.htm.md "Output representation of the pricing error response.")[] | Displays the error while processing the request. | Small, 61.0 | 61.0 |
| `isSuccess` | Boolean | Indicates whether the request is successful (`true`) or not (`false`). | Small, 61.0 | 61.0 |
| `source​ProceductId` | String | ID of the source product. | Small, 61.0 | 61.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_p_b_e_derived_pricing_out_put.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
