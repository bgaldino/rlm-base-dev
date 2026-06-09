---
page_id: connect_requests_place_supplemental_transaction_input.htm
title: Supplemental Transaction Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_place_supplemental_transaction_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Supplemental Transaction Input

Input representation of the details of the request to create a supplemental
order.

JSON example
:   This sample creates a supplemental order, which is a clone of the original
    order. The supplemental order is related to the original
    order.

    ```
    {
      "relatedSalesTransactionId": "801S70000001VKgIAM"
    }
    ```
:   This sample overrides a field value of an order line item to supplement the order item with ID
    value as `802SG000003vZ15YAE`.

    ```
    {
        "relatedSalesTransactionId": "801S70000001VKgIAM",
        "pricingPref": "System",
        "supplementalGraph": {
            "graphId": "1",
            "records": [
                {
                    "referenceId": "refOrder",
                    "record": {
                        "attributes": {
                            "type": "Order",
                            "method": "PATCH",
                            "id": "801S70000001VKgIAM"
                        },
                        "EffectiveDate": "2025-03-01",
                        "QuoteId": "0Q0xx0000004DQ4CAM"
                    }
                },
                {
                    "referenceId": "refOrderItem",
                    "record": {
                        "attributes": {
                            "type": "OrderItem",
                            "method": "PATCH",
                            "id": "802SG000003vZ15YAE"
                        },
                        "QuoteLineItemId": "0Q0xx0000004E2mYLK"
                    }
                }
            ]
        }
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `pricingPref` | String | Pricing preference for this supplemental transaction or order ingestion process. Valid values are:   - `Force`—Enforces pricing   during the creation of sales transactions. - `Skip`—Skips pricing during   the creation of sales transactions. - `System`—Determines whether a   pricing calculation is required.   If `pricingPref` value is defined as either `Force` or `System`, the supplemental order can have a different pricing from the original order. | Optional | 64.0 |
    | `relatedSales​TransactionId` | String | Related or the original sales transaction upon which a supplemental transaction is created. | Required | 64.0 |
    | `supplemental​Graph` | [Object Graph Input](./connect_requests_object_graph_input.htm.md "Input representation of an sObject with a graph ID.") | The sObject graph that represents a payload with the additional changes to be ingested.  The attribute's HTTP method must be PATCH. The attribute ID must be the ID of the original order or order item that you want to supplement. | Optional | 64.0 |
