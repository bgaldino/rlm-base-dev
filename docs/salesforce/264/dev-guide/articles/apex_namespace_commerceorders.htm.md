---
page_id: apex_namespace_commerceorders.htm
title: CommerceOrders Namespace
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_namespace_commerceorders.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_apex_reference.htm
fetched_at: 2026-11-23
---

# CommerceOrders Namespace

The `CommerceOrders` namespace provides classes and
methods to place orders with integrated pricing, configuration, and validation.

![Note](/docs/resources/img/en-us/264.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

This namespace has been deprecated as of API version 63.0. In API version 63.0 and
later, use the new [RevSalesTrxn](./apex_namespace_RevSalesTrxn.htm.md "HTML (New Window)")
namespace.

The `CommerceOrders` namespace includes these classes.

- **[CatalogRatesPreferenceEnum Enum](./apex_enum_commerceorders_CatalogRatesPreferenceEnum.htm.md)**  
  Specifies the rate card entries defined in the catalog that must be fetched for order items, with usage-based selling during the order creation process.
- **[ConfigurationInputEnum Enum](./apex_enum_commerceorders_ConfigurationInputEnum.htm.md)**  
  Specifies the configuration input for the request to place an order.
- **[ConfigurationOptionsInput Class](./apex_class_commerceorders_ConfigurationOptionsInput.htm.md#apex_class_commerceorders_ConfigurationOptionsInput)**  
  Contains methods and properties to set the configuration options for the input to the product configurator.
- **[GraphRequest Class](./apex_class_commerceorders_GraphRequest.htm.md#apex_class_commerceorders_GraphRequest)**  
  Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains the field values of an order.
- **[PlaceOrderExecutor Class](./apex_class_commerceorders_PlaceOrderExecutor.htm.md#apex_class_commerceorders_PlaceOrderExecutor)**  
  Contains methods to place an order with details of the graph request, pricing preferences, and configuration options.
- **[PlaceOrderResult Class](./apex_class_commerceorders_PlaceOrderResult.htm.md#apex_class_commerceorders_PlaceOrderResult)**  
  Contains properties to hold the response to the place order request.
- **[PricingPreferenceEnum Enum](./apex_enum_commerceorders_PricingPreferenceEnum.htm.md)**  
  Specifies the pricing preference during the create order process.
- **[RecordResource Class](./apex_class_commerceorders_RecordResource.htm.md#apex_class_commerceorders_RecordResource)**  
  Contains constructors and properties to create a record object from field values of an order.
- **[RecordWithReferenceRequest Class](./apex_class_commerceorders_RecordWithReferenceRequest.htm.md#apex_class_commerceorders_RecordWithReferenceRequest)**  
  Contains constructors and properties to associate a record object with a reference identifier.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_namespace_commerceorders.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
