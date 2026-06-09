---
page_id: apex_namespace_placequote.htm
title: PlaceQuote Namespace
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_namespace_placequote.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_apex_reference.htm
fetched_at: 2026-06-09
---

# PlaceQuote Namespace

The `PlaceQuote` namespace provides classes and methods
to create or update quotes with pricing preferences and configuration options.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

This namespace has been deprecated as of API version 63.0. In API version 63.0 and
later, use the new [RevSalesTrxn](https://developer.salesforce.com/docs/./apex_namespace_RevSalesTrxn.htm.md "HTML (New Window)")
namespace.

The `PlaceQuote` namespace includes these classes.

- **[CatalogRatesPreferenceEnum Enum](./apex_enum_placequote_CatalogRatesPreferenceEnum.htm.md)**  
  Specifies the rate card entries defined in the catalog that must be fetched for quote line items, with usage-based selling during the quote creation process.
- **[ConfigurationInputEnum Enum](./apex_enum_placequote_ConfigurationInputEnum.htm.md)**  
  Specifies the configuration input for the request to place a quote.
- **[ConfigurationOptionsInput Class](./apex_class_placequote_ConfigurationOptionsInput.htm.md#apex_class_placequote_ConfigurationOptionsInput)**  
  Contains methods and properties to set the configuration options for the input to the product configurator.
- **[GraphRequest Class](./apex_class_placequote_GraphRequest.htm.md#apex_class_placequote_GraphRequest)**  
  Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains the field values of an order.
- **[PlaceQuoteException Class](./apex_class_placequote_PlaceQuoteException.htm.md#apex_class_placequote_PlaceQuoteException)**  
  Contains methods to hold the exception details for the place quote request.
- **[PlaceQuoteResponse Class](./apex_class_placequote_PlaceQuoteResponse.htm.md#apex_class_placequote_PlaceQuoteResponse)**  
  Contains properties to hold the response to the place quote request.
- **[PlaceQuoteRLMApexProcessor Class](./apex_class_placequote_PlaceQuoteRLMApexProcessor.htm.md#apex_class_placequote_PlaceQuoteRLMApexProcessor)**  
  Contains methods to place a quote with details of the graph request, pricing preferences, and configuration options.
- **[PricingPreferenceEnum Enum](./apex_enum_placequote_PricingPreferenceEnum.htm.md)**  
  Specifies the pricing preference during the create quote process.
- **[RecordResource Class](./apex_class_placequote_RecordResource.htm.md#apex_class_placequote_RecordResource)**  
  Contains constructors and properties to create a record object from the field values of a quote.
- **[RecordWithReferenceRequest Class](./apex_class_placequote_RecordWithReferenceRequest.htm.md#apex_class_placequote_RecordWithReferenceRequest)**  
  Contains constructors and properties to associate a record object with a reference identifier.
