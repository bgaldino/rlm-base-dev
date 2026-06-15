---
page_id: connect_responses_core_pricing_output.htm
title: Pricing Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_core_pricing_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Pricing Output

Output representation of a Salesforce pricing request.

JSON example
:   ```
    {
    "apiExecutionId": "612228038743152",
    "pricingExecutionId": "612229738898095",
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
    },
    "pricingResultErrors": [],
    "status": "Completed",
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `apiExecutionId` | String | Unique ID that's generated each time a pricing API is executed. | Small, 63.0 | 63.0 |
| `error` | [Pricing Error Response](./connect_responses_pricing_error_response.htm.md "Output representation of the pricing error response.") | Displays the error encountered when the request is processed. For example, a pricing procedure isn’t found. | Small, 60.0 | 60.0 |
| `pricingExecutionId` | String | Unique ID that's generated each time a pricing process is executed. | Small, 63.0 | 63.0 |
| `pricing​Result` | [Pricing Result](./connect_responses_core_pricing_result.htm.md "Output representation of the pricing result.") | Represents the outcomes associated with the output tags defined in the contextual definition for which the pricing engine establishes values. The initial attribute name is substituted for the output tag's designation. For instance, if the original attribute name specified in the Context Definition is "Subtotal," but during contextual setup, the output tag is denoted as "Total Price," the API output exhibits the initial attribute name "Subtotal" in the response. | Small, 60.0 | 60.0 |
| `pricing​Result​Errors` | [Pricing Result Error[]](./connect_responses_core_pricing_result_error.htm.md "Output representation of the pricing result error.") | Errors from the pricing request, if any. | Small, 60.0 | 60.0 |
| `status` | String | Status of the pricing request. Valid values are:  - `Completed` — Pricing is completed   for all the line items. - `Partially Completed` — Pricing is   completed for some line items. - `Failed` — Pricing isn’t completed   for the line items. | Small, 60.0 | 60.0 |
