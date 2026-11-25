---
page_id: connect-responses-core-pricing-result-error
title: Pricing Result Error
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-core-pricing-result-error.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-responses
legacy_page_id: connect_responses_core_pricing_result_error.htm
fetched_at: 2026-11-25
---

# Pricing Result Error

Output representation of the pricing result error.

## JSON Example

```
"pricingResultErrors": {
"Aggregateprice": [
{
"dataPath": [
"cart_1001",
],

"errors": [
{ 
“errorCode”: “Dummy”
“message”:
	}
       ]
   }
 ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `dataPath` | String[] | Includes the entire data route for the specific element starting from the root node. The request must include the ID to construct the accurate data route. For example, if a `jsonDataString` property comprises a Cart [Id = Cart1] and its associated Cart Item [Id = CartItem1], then the data route for CartItem appears as [Cart1, CartItem1]. | Small, 60.0 | 60.0 |
| `errors` | [Pricing Error Response](./connect-responses-pricing-error-response.md) | Displays processing errors related to the element as recognized by the data path. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-core-pricing-result-error.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
