---
page_id: qoc-business-apis
title: Transaction Management Business APIs
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/qoc-business-apis.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-overview
legacy_page_id: qoc_business_apis.htm
fetched_at: 2026-11-25
---

# Transaction Management Business APIs

Use the Transaction Management Business APIs to fetch instant pricing data on a quote or an order, to create a quote, or to create an order.

This table lists the available Transaction Management resources.

| Resource | Description |
| --- | --- |
| [`/connect/revenue-management/assets/actions/amend`](./connect-resources-assets-amend.md) (POST) | Initiate and execute the amendment of a quote or an order. |
| [`/connect/revenue-management/assets/actions/cancel`](./connect-resources-assets-cancel.md) (POST) | Initiate and execute the cancellation of an asset. |
| [`/connect/revenue-management/assets/actions/renew`](./connect-resources-assets-renew.md) (POST) | Initiate and execute the renewal of an asset. |
| [`/industries/cpq/quotes/actions/get-instant-price`](./connect-resources-cpq-instant-pricing.md) (POST) | Fetch instant pricing data on the quote or order line data grid and associated summary component. This API offers capabilities to either create a context or update the existing one based on the provided context ID. |
| [`/commerce/sales-orders/actions/place`](./connect-resources-place-order.md) (POST) | Place orders with integrated pricing, configuration, and validation, and manage them throughout their entire lifecycle. Additionally, update an order or insert order items. |
| [`/commerce/quotes/actions/place`](./connect-resources-place-quote.md) (POST) | Create a quote to discover and price products and services. Additionally, insert, update, or delete a quote line item. |
| [`/connect/revenue-management/sales-transaction-contexts/{resourceId}/actions/ramp-deal-create`](./connect-resources-create-ramp-deal.md) (POST) | Create a ramp deal for a customer on a product. Sales reps can use ramp deals to provide yearly deals to a customer, resulting in long-term revenue and customer relationship. A customer can create, update, or view multiple segments of periods for their subscription term with different attributes for each segment. |
| [`/connect/revenue-management/sales-transaction-contexts/{resourceId}/actions/ramp-deal-update`](./connect-resources-update-ramp-deal.md) (POST) | Modify a ramp deal in scenarios where a segment has updates such as quantity, discount, or date change. |
| [`/connect/revenue-management/sales-transaction-contexts/{resourceId}/actions/ramp-deal-view`](./connect-resources-view-ramp-deal.md) (GET) | View a ramp deal related to a quote line item or an order item. |
| [`/connect/revenue-management/sales-transaction-contexts/{resourceId}/actions/ramp-deal-delete`](./connect-resources-delete-ramp-deal.md) (POST) | Delete a ramp deal to convert a ramped product to include a single quote line item or order item. |
| [`/connect/rev/sales-transaction/actions/place`](./connect-resources-place-sales-transaction.md) (POST) | Create a sales transaction, such as an order or a quote, with integrated pricing and configuration. Also, update an order or a quote, and insert and delete order or quote line items to calculate the estimated tax. |
| [`/connect/rev/sales-transaction/actions/clone`](./connect-resources-clone-sales-transaction.md) (POST) | Create a clone of a sales transaction, such as a quote or an order. You can also clone a quote line item or an order item record with its related records and configurations. |
| [`/connect/rev/sales-transaction/actions/place-supplemental-transaction`](./connect-resources-place-supplemental-transaction.md) (POST) | Create a supplemental order or change orders after they are submitted for processing, such as during the fulfillment process. |
| [`/connect/revenue/transaction-management/sales-transactions/actions/read`](./connect-resources-read-sales-transaction.md) (POST) | Retrieve sales transaction data efficiently from an initialized or a hydrated context. |
| [`/global-promotions-management/promotions`](./connect-resources-create-promotions.md) (GET, POST, PUT) | Get rewards based on a product selling model template. |
| [`/revenue/transaction-management/sales-transactions/actions/get-eligible-promotions`](./connect-resources-get-eligible-promotions.md) (POST) | Get eligible promotions for line items within a quote or an order. |
| [`/revenue/transaction-management/assets/actions/swap`](./connect-resources-initiate-swap.md) (POST) | Exchange one product for another of equivalent or different value. The change is tracked as a swap request with linked asset actions and a net-zero order total where applicable. The API creates an amendment quote and order with order actions and quote action subtypes. |
| [`/revenue/transaction-management/assets/actions/upgrade`](./connect-resources-initiate-upgrade.md) (POST) | Move a lower-tier product to a higher-tier product. The change is tracked as an upgrade request with linked asset actions and quote or order line linkage for reporting and auditing. This API creates an amendment quote and order with order actions and quote action subtypes. |
| [`/revenue/transaction-management/assets/actions/downgrade`](./connect-resources-initiate-downgrade.md) (POST) | Move to a lower-tier or lower-value product. The change is tracked as a downgrade request with linked asset actions and quote or order line linkage for reporting and auditing. This API creates an amendment quote and order with downgrade-specific order actions and quote action subtypes. |

- 

**[Resources](./qoc-business-apis-rest-references.md)**

Learn more about the available Quote and Order Capture resources.

- 

**[Request Bodies](./qoc-api-requests.md)**

Learn more about the available API request bodies.

- 

**[Response Bodies](./qoc-api-responses.md)**

Learn more about the available response bodies.

**See Also**

- [*Connect REST API Developer Guide*: Introduction](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/intro_what_is_chatter_connect.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/qoc-business-apis.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
