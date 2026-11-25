---
page_id: usage-management-business-apis
title: Usage Management Business APIs
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/usage-management-business-apis.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-overview
legacy_page_id: usage_management_business_apis.htm
fetched_at: 2026-11-25
---

# Usage Management Business APIs

Use the Usage Management Business APIs to get details of a usage-based product that’s associated with an asset, an order item, or a quote line item.

This table lists the available Usage Management resources.

| Resource | Description |
| --- | --- |
| [`/asset-management/assets/{assetId}/usage-details`](./connect-resources-asset-usage-details.md) (GET) | Get details of a usage-based product associated with an asset. This covers details of grants, resources, and configured rates for the product, including negotiated rates in case of a rate override. |
| [`/commerce/sales-orders/line-items/{orderItemId}/usage-details`](./connect-resources-order-usage-details.md) (GET) | Get details of a usage-based product associated with an order item. |
| [`/commerce/quotes/line-items/{quoteLineItemId}/usage-details`](./connect-resources-quote-usage-details.md) (GET) | Get details of a usage-based product associated with a quote line item. |
| [`/revenue/usage-management/binding-objects/{bindingObjectId}/actions/usage-details`](./connect-resources-retrieve-binding-object-details.md) (GET) | Get details of grants, resources, rates, and any configured policies for a specified binding object. |
| [`/revenue/usage-management/consumption/actions/trace`](./connect-resources-consumption-traceabilities.md) (POST) | Get a comprehensive breakdown of overage charges and resource drawdown, enabling you to view information that’s applicable to specific invoice lines. |
| [`/revenue/usage-management/usage-products/actions/validate`](./connect-resources-usage-product-validation.md) (POST) | Validate cross-object relationships and business rules for usage-based products. |

- 

**[Resources](./usage-management-business-apis-resources.md)**

Learn more about the available Usage Management API resources.

- 

**[Request Bodies](./usage-management-business-apis-requests.md)**

Learn more about the available request bodies of Usage Management APIs.

- 

**[Response Bodies](./usage-management-business-apis-responses.md)**

Learn more about the available response bodies of Usage Management APIs.

**See Also**

- [*Connect REST API Developer Guide*: Introduction](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/intro_what_is_chatter_connect.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/usage-management-business-apis.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
