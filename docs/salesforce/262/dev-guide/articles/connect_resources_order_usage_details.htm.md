---
page_id: connect_resources_order_usage_details.htm
title: Order Item Usage Details (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_order_usage_details.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Order Item Usage Details (GET)

Get details of a usage-based product associated with an order
item.

Here are the details that this API returns.

- Grants and resources for the product, if rates aren’t configured.
- Grants, resources, and any configured rates for the product. The rates are returned by
  the [Rate Plan (GET) API](./connect_resources_get_rate_plan.htm.md "HTML (New Window)").
- Resources that include grants, if applicable, and any negotiated rates for the product
  in case of a rate override request.

This API doesn't return binding target rates. Use the [Binding Object Usage Details
API](./connect_resources_retrieve_binding_object_details.htm.md "HTML (New Window)") to retrieve binding target rates.

Resource
:   ```
    /commerce/sales-orders/line-items/orderItemId/usage-details
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/sales-orders/line-items/802SG000003vZ15YAE/usage-details
    ```

    ```
    https://yourInstance.salesforce.com/services/data​/v67.0/commerce/sales-orders/line-items/802SG000003vZ15YAE/usage-details?optionalFields=OrderItemRateCardEntry.MyCustomDate__c,OrderItemRateCardEntry.MyCustomNumber__c,OrderItemRateAdjustment.myCustomString__c
    ```

Available version
:   63.0

HTTP methods
:   GET

Path parameter for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `orderItemId` | String | ID of the order item. | Required | 63.0 |

Query parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `effectiveDate` | String | Date that's used to search for the applicable rate card entries. | Optional | 63.0 |
    | `optionalFields` | String[] | Custom fields that you can use to query these objects.  - [OrderItemRateCardEntry](./sforce_api_objects_orderitemratecardentry.htm.md "HTML (New Window)") - [OrderItemRateAdjustment](./sforce_api_objects_orderitemrateadjustment.htm.md "HTML (New Window)") | Optional | 63.0 |

Response body for GET
:   [Usage
    Details](./connect_responses_usage_detail_output.htm.md "Output representation of the usage details of a quote, an order, or an asset.")
