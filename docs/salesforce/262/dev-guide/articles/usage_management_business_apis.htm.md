---
page_id: usage_management_business_apis.htm
title: Usage Management Business APIs
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/usage_management_business_apis.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_overview.htm
fetched_at: 2026-06-09
---

# Usage Management Business APIs

Use the Usage Management Business APIs to get details of a usage-based product that’s
associated with an asset, an order item, or a quote line item.

This table lists the available Usage Management resources.

| Resource | Description |
| --- | --- |
| [`/asset-management/assets/assetId/usage-details`](./connect_resources_asset_usage_details.htm.md "Get details of a usage-based product associated with an asset. This covers details of grants, resources, and configured rates for the product, including negotiated rates in case of a rate override.") (GET) | Get details of a usage-based product associated with an asset. This covers details of grants, resources, and configured rates for the product, including negotiated rates in case of a rate override. |
| [`/commerce/sales-orders/line-items/orderItemId/usage-details`](./connect_resources_order_usage_details.htm.md "Get details of a usage-based product associated with an order item.") (GET) | Get details of a usage-based product associated with an order item. |
| [`/commerce/quotes/line-items/quoteLineItemId/usage-details`](./connect_resources_quote_usage_details.htm.md "Get details of a usage-based product associated with a quote line item.") (GET) | Get details of a usage-based product associated with a quote line item. |
| [`/revenue/usage-management/binding-objects/bindingObjectId/actions/usage-details`](./connect_resources_retrieve_binding_object_details.htm.md "Get details of grants, resources, rates, and any configured policies for a specified binding object.") (GET) | Get details of grants, resources, rates, and any configured policies for a specified binding object. |
| [`/revenue/usage-management/consumption/actions/trace`](./connect_resources_consumption_traceabilities.htm.md "Get a comprehensive breakdown of overage charges and resource drawdown, enabling you to view information that's applicable to specific invoice lines.") (POST) | Get a comprehensive breakdown of overage charges and resource drawdown, enabling you to view information that's applicable to specific invoice lines. |
| [`/revenue/usage-management/usage-products/actions/validate`](./connect_resources_usage_product_validation.htm.md "Validate cross-object relationships and business rules for usage-based products.") (POST) | Validate cross-object relationships and business rules for usage-based products. |

- **[Resources](./usage_management_business_apis_resources.htm.md)**  
  Learn more about the available Usage Management API resources.
- **[Request Bodies](./usage_management_business_apis_requests.htm.md)**  
  Learn more about the available request bodies of Usage Management APIs.
- **[Response Bodies](./usage_management_business_apis_responses.htm.md)**  
  Learn more about the available response bodies of Usage Management APIs.

#### See Also

- [*Connect REST API Developer Guide*: Introduction](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/intro_what_is_chatter_connect.htm "Connect REST API Developer Guide: Introduction - HTML (New Window)")
