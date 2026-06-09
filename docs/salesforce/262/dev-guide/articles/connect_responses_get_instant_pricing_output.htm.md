---
page_id: connect_responses_get_instant_pricing_output.htm
title: Instant Pricing
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_get_instant_pricing_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Instant Pricing

Output representation containing the results of the instant pricing request.

Sample Response
:   ```
    {
      "contextId": "0000000p18dq18g0025177552281982954d1f35410374495bc923a2319a1247c",
      "correlationId": "7847127122596",
      "records": [
        {
          "error": {},
          "record": {
            "NetUnitPrice": 900.8972677417262,
            "Discount": null,
            "EndQuantity": 5,
            "NetTotalPrice": 3603.5890709669047,
            "AggregatedQuantity": 4,
            "TotalLineAmount": 3603.5890709669047,
            "Quantity": 4,
            "attributes": {
              "type": "QuoteLineItem"
            },
            "ListPrice": 900.8972677417262
          },
          "referenceId": "0QLLT0000018DY14AM"
        },
        {
          "error": {},
          "record": {
            "NetUnitPrice": 720.3738964743471,
            "Discount": null,
            "EndQuantity": 5,
            "NetTotalPrice": 2881.4955858973885,
            "AggregatedQuantity": 4,
            "TotalLineAmount": 2881.4955858973885,
            "Quantity": 4,
            "attributes": {
              "type": "QuoteLineItem"
            },
            "ListPrice": 720.3738964743471
          },
          "referenceId": "0QLLT0000018DYr4AM"
        },
        {
          "error": {},
          "record": {
            "NetUnitPrice": 218.36199390885784,
            "Discount": null,
            "EndQuantity": 5,
            "NetTotalPrice": 873.4479756354314,
            "AggregatedQuantity": 4,
            "TotalLineAmount": 873.4479756354314,
            "Quantity": 4,
            "attributes": {
              "type": "QuoteLineItem"
            },
            "ListPrice": 218.36199390885784
          },
          "referenceId": "0QLLT0000018DYG4A2"
        },
        {
          "error": {},
          "record": {
            "AccountId": "001LT000011SA6bYAG",
            "TotalPrice": 406014.84549259685,
            "attributes": {
              "type": "Quote"
            },
            "Discount": 0,
            "psmSummaryFields": {
              "evergreen##months##1": {
                "aggregatedTotal": 140349.76846114534,
                "pricingTerm": 1,
                "pricingTermUnit": "Months",
                "sellingModelType": "Evergreen"
              },
              "onetime": {
                "aggregatedTotal": 128927.94222255558,
                "sellingModelType": "OneTime"
              },
              "termdefined##annual##1": {
                "aggregatedTotal": 136737.13480889596,
                "pricingTerm": 1,
                "pricingTermUnit": "Annual",
                "sellingModelType": "TermDefined"
              }
            },
            "Subtotal": 406014.84549259685
          },
          "referenceId": "0Q0LT000000Q1LR0A0"
        }
      ],
      "success": true
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | Context ID returned by the context service. | Small, 59.0 | 59.0 |
| `correlationId` | String | Client-generated ID for tracking multiple related API calls. | Small, 59.0 | 59.0 |
| `records` | [Object Reference](./connect_responses_object_with_reference_response.htm.md "Output representation of an sObject with a reference ID along with any potential error.")[] | List of records related to pricing results. | Small, 59.0 | 59.0 |
| `success` | Boolean | Indicates whether the fetching of instant pricing is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |
