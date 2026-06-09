---
page_id: connect_responses_core_pricing_result.htm
title: Pricing Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_core_pricing_result.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Pricing Result

Output representation of the pricing result.

JSON example
:   ```
    "pricingResult": {
    "subtotal": [
    {
    "dataPath": [
    "cart_1001",
    "lineItem_1002"
    ],
    "value": 300.0,
    "errors": [],
    "isSuccess": true
    },
    {
    "dataPath": [
    "cart_1001",
    "lineItem_1001"
    ],
    "value":400.0,
    "errors": [],
    "isSuccess": true
    }
    ],
    "netunitprice": [
    {
    "dataPath": [
    "cart_1001",
    "lineItem_1002"
    ],
    "value": xx,
    "errors": [],
    "isSuccess": true
    },
    {
    "dataPath": [
    "cart_1001",
    "lineItem_1001"
    ],
    "value": xx,
    "errors": [],
    "isSuccess": true
    }
    ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `dataPath` | String | Includes the entire data route for the specific element starting from the root node. The request must include the ID to construct the accurate data route.  For example, if a jsonDataString property comprises a Cart [Id = Cart1] and its associated Cart Item [Id = CartItem1], then the data route for CartItem appears as [Cart1, CartItem1]. | Small, 60.0 | 60.0 |
| `errors` | [Pricing Error Response[]](./connect_responses_pricing_error_response.htm.md "Output representation of the pricing error response.") | Displays processing errors related to the element as recognized by the data path. | Small, 60.0 | 60.0 |
| `isSuccess` | Boolean | Displays if processing of the element for the specified data path is successful or not. | Small, 60.0 | 60.0 |
| `value` | Object | Displays the value of the element into consideration. Element is uniquely identify by the data path. | Small, 60.0 | 60.0 |
