---
page_id: apex_class_placequote_PlaceQuoteRLMApexProcessor.htm
title: PlaceQuoteRLMApexProcessor Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_placequote_PlaceQuoteRLMApexProcessor.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_placequote.htm
fetched_at: 2026-06-09
---

# PlaceQuoteRLMApexProcessor Class

Contains methods to place a quote with details of the graph request, pricing preferences,
and configuration options.

## Namespace

[PlaceQuote](./apex_namespace_placequote.htm.md "The PlaceQuote namespace provides classes and methods to create or update quotes with pricing preferences and configuration options.")

- **[PlaceQuoteRLMApexProcessor Methods](./apex_class_placequote_PlaceQuoteRLMApexProcessor.htm.md#apex_placequote_PlaceQuoteRLMApexProcessor_methods)**  
  Learn more about the methods available with the `PlaceQuoteRLMApexProcessor` class.
- **[PlaceQuoteRLMApexProcessor Example Implementation](./apex_class_placequote_PlaceQuoteRLMApexProcessor.htm.md#apex_placequote_PlaceQuoteRLMApexProcessor_example_implementation)**  
  To place a quote from Apex, refer to the example implementation of the `PlaceQuoteRLMApexProcessor` class.

## PlaceQuoteRLMApexProcessor Methods

Learn more about the methods available with the `PlaceQuoteRLMApexProcessor` class.

The `PlaceQuoteRLMApexProcessor` class includes these
methods.

- **[execute(pricingPreferenceEnum, graphRequest, configurationInputEnum, configurationOptionsInput)](./apex_class_placequote_PlaceQuoteRLMApexProcessor.htm.md#apex_placequote_PlaceQuoteRLMApexProcessor_execute)**  
  Use the method in the `PlaceQuoteExecutor` class to execute the Place Quote Apex API request by assigning the properties for graph request, pricing references, and configuration options.
- **[execute(pricingPreferenceEnum, catalogRatesPreference, graphRequest, configurationInputEnum, configurationOptionsInput)](./apex_class_placequote_PlaceQuoteRLMApexProcessor.htm.md#apex_placequote_PlaceQuoteRLMApexProcessor_execute_2)**  
  Use the method in the `PlaceQuoteExecutor` class to execute the Place Quote Apex API request by assigning the properties for graph request, pricing references, and configuration options. This method also includes the property to define fetching of rate card entries.

### execute(pricingPreferenceEnum, graphRequest, configurationInputEnum, configurationOptionsInput)

Use the method in the `PlaceQuoteExecutor` class to
execute the Place Quote Apex API request by assigning the properties for graph request, pricing
references, and configuration options.

#### Signature

`public static placequote.PlaceQuoteResponse execute(placequote.PricingPreferenceEnum pricingPreferenceEnum, placequote.GraphRequest graphRequest, placequote.ConfigurationInputEnum configurationInputEnum, placequote.ConfigurationOptionsInput configurationOptionsInput)`

#### Parameters

pricingPreferenceEnum
:   Type: [placequote.PricingPreferenceEnum](./apex_enum_placequote_PricingPreferenceEnum.htm.md "Specifies the pricing preference during the create quote process.")
:   Pricing preference during the quote process.

graphRequest
:   Type: [placequote.GraphRequest](./apex_class_placequote_GraphRequest.htm.md#apex_class_placequote_GraphRequest "Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains the field values of an order.")
:   The sObject graph values of the quote payload to be ingested.

configurationInputEnum
:   Type: [placequote.ConfigurationInputEnum](./apex_enum_placequote_ConfigurationInputEnum.htm.md "Specifies the configuration input for the request to place a quote.")
:   Configuration input for the quote process.

configurationOptionsInput
:   Type: [placequote.ConfigurationOptionsInput](./apex_class_placequote_ConfigurationOptionsInput.htm.md#apex_class_placequote_ConfigurationOptionsInput "Contains methods and properties to set the configuration options for the input to the product configurator.")
:   Configuration options during the ingestion process.

#### Return Value

Type: [placequote.PlaceQuoteResponse](./apex_class_placequote_PlaceQuoteResponse.htm.md#apex_class_placequote_PlaceQuoteResponse "Contains properties to hold the response to the place quote request.")

### execute(pricingPreferenceEnum, catalogRatesPreference, graphRequest, configurationInputEnum, configurationOptionsInput)

Use the method in the `PlaceQuoteExecutor` class to
execute the Place Quote Apex API request by assigning the properties for graph request, pricing
references, and configuration options. This method also includes the property to define fetching
of rate card entries.

#### Signature

`public static placequote.PlaceQuoteResponse
execute(placequote.PricingPreferenceEnum pricingPreferenceEnum,
placequote.CatalogRatesPreferenceEnum catalogRatesPreference, placequote.GraphRequest
graphRequest, placequote.ConfigurationInputEnum configurationInputEnum,
placequote.ConfigurationOptionsInput configurationOptionsInput)`

#### Parameters

pricingPreferenceEnum
:   Type: [placequote.PricingPreferenceEnum](./apex_enum_placequote_PricingPreferenceEnum.htm.md "Specifies the pricing preference during the create quote process.")
:   Pricing preference during the quote process.

catalogRatesPreference
:   Type: [placequote.CatalogRatesPreferenceEnum](./apex_enum_placequote_CatalogRatesPreferenceEnum.htm.md "Specifies the rate card entries defined in the catalog that must be fetched for quote line items, with usage-based selling during the quote creation process.")
:   The rate card entries defined in the catalog that must be fetched for quote line
    items, with usage-based pricing during the quote creation process. The `CatalogRatesPreferenceEnum` enum is available when the
    Usage-Based Selling feature is enabled.

graphRequest
:   Type: [placequote.GraphRequest](./apex_class_placequote_GraphRequest.htm.md#apex_class_placequote_GraphRequest "Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains the field values of an order.")
:   The sObject graph values of the quote payload to be ingested.

configurationInputEnum
:   Type: [placequote.ConfigurationInputEnum](./apex_enum_placequote_ConfigurationInputEnum.htm.md "Specifies the configuration input for the request to place a quote.")
:   Configuration input for the quote process.

configurationOptionsInput
:   Type: [placequote.ConfigurationOptionsInput](./apex_class_placequote_ConfigurationOptionsInput.htm.md#apex_class_placequote_ConfigurationOptionsInput "Contains methods and properties to set the configuration options for the input to the product configurator.")
:   Configuration options during the ingestion process.

#### Return Value

Type: [placequote.PlaceQuoteResponse](./apex_class_placequote_PlaceQuoteResponse.htm.md#apex_class_placequote_PlaceQuoteResponse "Contains properties to hold the response to the place quote request.")

## PlaceQuoteRLMApexProcessor Example Implementation

To place a quote from Apex, refer to the example implementation of the `PlaceQuoteRLMApexProcessor` class.

### Namespace

[PlaceQuote](./apex_namespace_placequote.htm.md "The PlaceQuote namespace provides classes and methods to create or update quotes with pricing preferences and configuration options.")

### Usage

Customize this example to suit your requirements. Create the list of records to be
ingested by using these steps. Replace the respective IDs with the values that are
present in your org. For example, replace the value of `${Pricebook2Id}` field with the price book ID that’s present in the
org.

### Example

- Set up a quote and quote line item. To associate the Record object with a
  reference identifier, create an instance of the `RecordWithReferenceRequest`
  class.

  ```
           //Quote Setup 
      PlaceQuote.RecordResource quoteRecord = new PlaceQuote.RecordResource(Quote.getSobjectType(),'POST');
      Map<String,Object> quoteFieldValues = new Map<String,Object>();
      quoteFieldValues.put('Name','q-ap12');
      quoteFieldValues.put('OpportunityId','006xx000001aBFcAAM');
      quoteFieldValues.put('Pricebook2Id','01sxx0000005pvRAAQ');
      quoteRecord.fieldValues = quoteFieldValues;
      
             //Quote Line Item Setup
      PlaceQuote.RecordResource quoteLineItemRecord1 = new PlaceQuote.RecordResource(QuoteLineItem.getSobjectType(),'POST');
      Map<String,Object> quoteLineItemFieldValues = new Map<String,Object>();
      quoteLineItemFieldValues.put('Product2Id','01txx0000006ibwAAA');
      quoteLineItemFieldValues.put('PricebookEntryId','01uxx0000008zPqAAI');
      quoteLineItemFieldValues.put('Quantity','2.0');
      quoteLineItemFieldValues.put('UnitPrice','5.0');
      quoteLineItemFieldValues.put('StartDate','2023-03-15');
      quoteLineItemFieldValues.put('QuoteId','@{refQuote.id}');
      quoteLineItemRecord1.fieldValues = quoteLineItemFieldValues;
      PlaceQuote.RecordWithReferenceRequest quoteItemRecords = new PlaceQuote.RecordWithReferenceRequest('refQuote',quoteRecord);
      PlaceQuote.RecordWithReferenceRequest quoteLineItemRecords1 = new PlaceQuote.RecordWithReferenceRequest('refQuoteItem1',quoteLineItemRecord1);
  ```
- To create a quote line relationship, create an instance of the `RecordResource`
  class.

  ```
  PlaceQuote.RecordResource quoteLineRelationship1 = new PlaceQuote.RecordResource(QuoteLineRelationship.getSobjectType(),'POST');
      Map<String,Object> quoteLineRelationshipValues = new Map<String,Object>();
      quoteLineRelationshipValues.put('ProductRelationshipTypeId','0yoxx00000000JNAAY');
      quoteLineRelationshipValues.put('MainQuoteLineId','@{refQuoteItem2.id}');
      quoteLineRelationshipValues.put('AssociatedQuoteLineId','@{refQuoteItem1.id}');
      quoteLineRelationshipValues.put('AssociatedQuoteLinePricing','IncludedInBundlePrice');
      quoteLineRelationship1.fieldValues = quoteLineRelationshipValues;
  ```
- Create the list of records to be
  ingested.

  ```
      PlaceQuote.RecordWithReferenceRequest quoteLineRelationship = new PlaceQuote.RecordWithReferenceRequest('QuoteLineRelationship',quoteLineRelationship1);
      List<PlaceQuote.RecordWithReferenceRequest> listOfRecords = new List<PlaceQuote.RecordWithReferenceRequest>();
      listOfRecords.add(quoteItemRecords);
      listOfRecords.add(quoteLineItemRecords1);
      listOfRecords.add(quoteLineItemRecords2);
      listOfRecords.add(quoteLineRelationship);
  ```
- To contain all record objects, create an instance of the `GraphRequest` class.

  ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

  #### Note

  The `CatalogRatesPreferenceEnum` enum is available
  when the Usage-Based Selling feature is
  enabled.

  ```
      PlaceQuote.GraphRequest graph = new PlaceQuote.GraphRequest('test',listOfRecords);
      PlaceQuote.ConfigurationOptionsInput cInput = new PlaceQuote.ConfigurationOptionsInput();
      PlaceQuote.CatalogRatesPreferenceEnum catalogRatesPreference = PlaceQuote.CatalogRatesPreferenceEnum.Fetch;
  ....PlaceQuote.ConfigurationInputEnum configurationPreference = PlaceQuote.ConfigurationInputEnum.RunAndAllowErrors;
      PlaceQuote.PricingPreferenceEnum pricingPreference = PlaceQuote.PricingPreferenceEnum.System;
      //System.debug(graph);
        
      //Place Quote Call
      PlaceQuote.PlaceQuoteResponse resp = PlaceQuote.PlaceQuoteRLMApexProcessor.execute(pricingPreference, catalogRatesPreference, graph, configurationPreference, cInput);
      System.debug(resp);
  ```
