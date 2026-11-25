---
page_id: qoc-business-apis-rest-references
title: Resources
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/qoc-business-apis-rest-references.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-business-apis
legacy_page_id: qoc_business_apis_rest_references.htm
fetched_at: 2026-11-25
---

# Resources

Learn more about the available Quote and Order Capture resources.

- 

**[Asset Amendment (POST)](./connect-resources-assets-amend.md)**

Initiate and execute the amendment of a quote or an order.

- 

**[Asset Cancellation (POST)](./connect-resources-assets-cancel.md)**

Initiate and execute the cancellation of an asset.

- 

**[Asset Renewal (POST)](./connect-resources-assets-renew.md)**

Initiate and execute the renewal of an asset.

- 

**[Clone Sales Transaction (POST)](./connect-resources-clone-sales-transaction.md)**

Create a clone of a sales transaction, such as a quote or an order. You can also clone a quote line item or an order item record with its related records and configurations.

- 

**[Create Promotions (GET, POST, PUT)](./connect-resources-create-promotions.md)**

Get rewards based on a product selling model template.

- 

**[Get Eligible Promotions (POST)](./connect-resources-get-eligible-promotions.md)**

Get eligible promotions for line items within a quote or an order.

- 

**[Initiate Downgrade (POST)](./connect-resources-initiate-downgrade.md)**

Move to a lower-tier or lower-value product. The change is tracked as a downgrade request with linked asset actions and quote or order line linkage for reporting and auditing. This API creates an amendment quote and order with downgrade-specific order actions and quote action subtypes.

- 

**[Initiate Swap (POST)](./connect-resources-initiate-swap.md)**

Exchange one product for another of equivalent or different value. The change is tracked as a swap request with linked asset actions and a net-zero order total where applicable. The API creates an amendment quote and order with order actions and quote action subtypes.

- 

**[Initiate Upgrade (POST)](./connect-resources-initiate-upgrade.md)**

Move a lower-tier product to a higher-tier product. The change is tracked as an upgrade request with linked asset actions and quote or order line linkage for reporting and auditing. This API creates an amendment quote and order with order actions and quote action subtypes.

- 

**[Instant Pricing (POST)](./connect-resources-cpq-instant-pricing.md)**

Fetch instant pricing data on the quote or order line data grid and associated summary component. This API offers capabilities to either create a context or update the existing one based on the provided context ID.

- 

**[Place Order (POST)](./connect-resources-place-order.md)**

Place orders with integrated pricing, configuration, and validation, and manage them throughout their entire lifecycle. Additionally, update an order or insert order items.

- 

**[Place Quote (POST)](./connect-resources-place-quote.md)**

Create a quote to discover and price products and services. Additionally, insert, update, or delete a quote line item.

- 

**[Place Sales Transaction (POST)](./connect-resources-place-sales-transaction.md)**

Create a sales transaction, such as an order or a quote, with integrated pricing and configuration. Also, update an order or a quote, and insert and delete order or quote line items to calculate the estimated tax.

- 

**[Place Supplemental Transaction (POST)](./connect-resources-place-supplemental-transaction.md)**

Create a supplemental order or change orders after they are submitted for processing, such as during the fulfillment process.

- 

**[Read Sales Transaction (POST)](./connect-resources-read-sales-transaction.md)**

Retrieve sales transaction data efficiently from an initialized or a hydrated context.

- 

**[Retrieve Sales Transaction API Errors (GET)](./connect-resources-retrieve-place-sales-transaction-error.md)**

Retrieve any asynchronous error details associated with a sales transaction request.

- 

**[Unlock Transaction (POST)](./connect-resources-unlock-transaction.md)**

Unlock a quote or order whose calculation is stuck in a non-terminal status so that you can retry the transaction.

- 

**[Create Ramp Deal (POST)](./connect-resources-create-ramp-deal.md)**

Create a ramp deal for a customer on a product. Sales reps can use ramp deals to provide yearly deals to a customer, resulting in long-term revenue and customer relationship. A customer can create, update, or view multiple segments of periods for their subscription term with different attributes for each segment.

- 

**[Delete Ramp Deal (POST)](./connect-resources-delete-ramp-deal.md)**

Delete a ramp deal to convert a ramped product to include a single quote line item or order item.

- 

**[Update Ramp Deal (POST)](./connect-resources-update-ramp-deal.md)**

Modify a ramp deal in scenarios where a segment has updates such as quantity, discount, or date change.

- 

**[View Ramp Deal (GET)](./connect-resources-view-ramp-deal.md)**

View a ramp deal related to a quote line item or an order item.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/qoc-business-apis-rest-references.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
