---
page_id: apex-namespace-placequote
title: PlaceQuote Namespace
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-namespace-placequote.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-apex-reference
legacy_page_id: apex_namespace_placequote.htm
fetched_at: 2026-11-25
---

# PlaceQuote Namespace

The `PlaceQuote` namespace provides classes and methods to create or update quotes with pricing preferences and configuration options.

**Note:**

This namespace has been deprecated as of API version 63.0. In API version 63.0 and later, use the new [RevSalesTrxn](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_namespace_RevSalesTrxn.htm) namespace.

The `PlaceQuote` namespace includes these classes.

- 

**[CatalogRatesPreferenceEnum Enum](./apex-enum-placequote-catalogratespreferenceenum.md)**

Specifies the rate card entries defined in the catalog that must be fetched for quote line items, with usage-based selling during the quote creation process.

- 

**[ConfigurationInputEnum Enum](./apex-enum-placequote-configurationinputenum.md)**

Specifies the configuration input for the request to place a quote.

- 

**[ConfigurationOptionsInput Class](./apex-class-placequote-configurationoptionsinput.md#configurationoptionsinput-class)**

Contains methods and properties to set the configuration options for the input to the product configurator.

- 

**[GraphRequest Class](./apex-class-placequote-graphrequest.md#graphrequest-class)**

Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains the field values of an order.

- 

**[PlaceQuoteException Class](./apex-class-placequote-placequoteexception.md#placequoteexception-class)**

Contains methods to hold the exception details for the place quote request.

- 

**[PlaceQuoteResponse Class](./apex-class-placequote-placequoteresponse.md#placequoteresponse-class)**

Contains properties to hold the response to the place quote request.

- 

**[PlaceQuoteRLMApexProcessor Class](./apex-class-placequote-placequoterlmapexprocessor.md#placequoterlmapexprocessor-class)**

Contains methods to place a quote with details of the graph request, pricing preferences, and configuration options.

- 

**[PricingPreferenceEnum Enum](./apex-enum-placequote-pricingpreferenceenum.md)**

Specifies the pricing preference during the create quote process.

- 

**[RecordResource Class](./apex-class-placequote-recordresource.md#recordresource-class)**

Contains constructors and properties to create a record object from the field values of a quote.

- 

**[RecordWithReferenceRequest Class](./apex-class-placequote-recordwithreferencerequest.md#recordwithreferencerequest-class)**

Contains constructors and properties to associate a record object with a reference identifier.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-namespace-placequote.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
