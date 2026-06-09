---
page_id: connect_responses_core_pricing_result_error.htm
title: Pricing Result Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_core_pricing_result_error.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Pricing Result Error

Output representation of the pricing result error.

JSON example
:   ```
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
| `dataPath` | String[] | Includes the entire data route for the specific element starting from the root node. The request must include the ID to construct the accurate data route.  For example, if a jsonDataString property comprises a Cart [Id = Cart1] and its associated Cart Item [Id = CartItem1], then the data route for CartItem appears as [Cart1, CartItem1]. | Small, 60.0 | 60.0 |
| `errors` | [Pricing Error Response](./connect_responses_pricing_error_response.htm.md "Output representation of the pricing error response.") | Displays processing errors related to the element as recognized by the data path. | Small, 60.0 | 60.0 |
