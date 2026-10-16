---
page_id: apex_namespace_placequote.htm
title: PlaceQuote Namespace
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_namespace_placequote.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_apex_reference.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# PlaceQuote Namespace

The `PlaceQuote` namespace provides classes and methods
    to create or update quotes with pricing preferences and configuration options.

      

#### Note

This namespace has been deprecated as of API version 63.0. In API version 63.0 and
        later, use the new [RevSalesTrxn](./apex_namespace_RevSalesTrxn.htm.md)
        namespace.

The `PlaceQuote` namespace includes these classes.

- 
**[CatalogRatesPreferenceEnum Enum](./apex_enum_placequote_CatalogRatesPreferenceEnum.htm.md)**  

Specifies the rate card entries defined in the catalog that must be fetched for quote     line items, with usage-based selling during the quote creation process.

- 
**[ConfigurationInputEnum Enum](./apex_enum_placequote_ConfigurationInputEnum.htm.md)**  

Specifies the configuration input for the request to place a quote.

- 
**[ConfigurationOptionsInput Class](./apex_class_placequote_ConfigurationOptionsInput.htm.md#apex_class_placequote_ConfigurationOptionsInput)**  

Contains methods and properties to set the configuration options for the input to the     product configurator.

- 
**[GraphRequest Class](./apex_class_placequote_GraphRequest.htm.md#apex_class_placequote_GraphRequest)**  

Contains constructors and properties to set the graph ID and a list of records to be     ingested. The list of records is specified in a key-value map format that contains the field     values of an order.

- 
**[PlaceQuoteException Class](./apex_class_placequote_PlaceQuoteException.htm.md#apex_class_placequote_PlaceQuoteException)**  

Contains methods to hold the exception details for the place quote request.

- 
**[PlaceQuoteResponse Class](./apex_class_placequote_PlaceQuoteResponse.htm.md#apex_class_placequote_PlaceQuoteResponse)**  

Contains properties to hold the response to the place quote request.

- 
**[PlaceQuoteRLMApexProcessor Class](./apex_class_placequote_PlaceQuoteRLMApexProcessor.htm.md#apex_class_placequote_PlaceQuoteRLMApexProcessor)**  

Contains methods to place a quote with details of the graph request, pricing preferences,     and configuration options.

- 
**[PricingPreferenceEnum Enum](./apex_enum_placequote_PricingPreferenceEnum.htm.md)**  

Specifies the pricing preference during the create quote process.

- 
**[RecordResource Class](./apex_class_placequote_RecordResource.htm.md#apex_class_placequote_RecordResource)**  

Contains constructors and properties to create a record object from the field values of a     quote.

- 
**[RecordWithReferenceRequest Class](./apex_class_placequote_RecordWithReferenceRequest.htm.md#apex_class_placequote_RecordWithReferenceRequest)**  

Contains constructors and properties to associate a record object with a reference     identifier.
