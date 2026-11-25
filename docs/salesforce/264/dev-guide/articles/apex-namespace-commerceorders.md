---
page_id: apex-namespace-commerceorders
title: CommerceOrders Namespace
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-namespace-commerceorders.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-apex-reference
legacy_page_id: apex_namespace_commerceorders.htm
fetched_at: 2026-11-25
---

# CommerceOrders Namespace

The `CommerceOrders` namespace provides classes and methods to place orders with integrated pricing, configuration, and validation.

**Note:**

This namespace has been deprecated as of API version 63.0. In API version 63.0 and later, use the new [RevSalesTrxn](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_namespace_RevSalesTrxn.htm) namespace.

The `CommerceOrders` namespace includes these classes.

- 

**[CatalogRatesPreferenceEnum Enum](./apex-enum-commerceorders-catalogratespreferenceenum.md)**

Specifies the rate card entries defined in the catalog that must be fetched for order items, with usage-based selling during the order creation process.

- 

**[ConfigurationInputEnum Enum](./apex-enum-commerceorders-configurationinputenum.md)**

Specifies the configuration input for the request to place an order.

- 

**[ConfigurationOptionsInput Class](./apex-class-commerceorders-configurationoptionsinput.md#configurationoptionsinput-class)**

Contains methods and properties to set the configuration options for the input to the product configurator.

- 

**[GraphRequest Class](./apex-class-commerceorders-graphrequest.md#graphrequest-class)**

Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains the field values of an order.

- 

**[PlaceOrderExecutor Class](./apex-class-commerceorders-placeorderexecutor.md#placeorderexecutor-class)**

Contains methods to place an order with details of the graph request, pricing preferences, and configuration options.

- 

**[PlaceOrderResult Class](./apex-class-commerceorders-placeorderresult.md#placeorderresult-class)**

Contains properties to hold the response to the place order request.

- 

**[PricingPreferenceEnum Enum](./apex-enum-commerceorders-pricingpreferenceenum.md)**

Specifies the pricing preference during the create order process.

- 

**[RecordResource Class](./apex-class-commerceorders-recordresource.md#recordresource-class)**

Contains constructors and properties to create a record object from field values of an order.

- 

**[RecordWithReferenceRequest Class](./apex-class-commerceorders-recordwithreferencerequest.md#recordwithreferencerequest-class)**

Contains constructors and properties to associate a record object with a reference identifier.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-namespace-commerceorders.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
