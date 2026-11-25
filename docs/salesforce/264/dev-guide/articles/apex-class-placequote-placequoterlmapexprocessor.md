---
page_id: apex-class-placequote-placequoterlmapexprocessor
title: PlaceQuoteRLMApexProcessor Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-placequote-placequoterlmapexprocessor.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-placequote
legacy_page_id: apex_class_placequote_PlaceQuoteRLMApexProcessor.htm
fetched_at: 2026-11-25
---

# PlaceQuoteRLMApexProcessor Class

Contains methods to place a quote with details of the graph request, pricing preferences, and configuration options.

## Namespace

[PlaceQuote](./apex-namespace-placequote.md)

- 

**[PlaceQuoteRLMApexProcessor Methods](#placequoterlmapexprocessor-methods)**

Learn more about the methods available with the `PlaceQuoteRLMApexProcessor` class.

- 

**[PlaceQuoteRLMApexProcessor Example Implementation](#placequoterlmapexprocessor-example-implementation)**

To place a quote from Apex, refer to the example implementation of the `PlaceQuoteRLMApexProcessor` class.

## PlaceQuoteRLMApexProcessor Methods

Learn more about the methods available with the `PlaceQuoteRLMApexProcessor` class.

The `PlaceQuoteRLMApexProcessor` class includes these methods.

- 

**[execute(pricingPreferenceEnum, graphRequest, configurationInputEnum, configurationOptionsInput)](#executepricingpreferenceenum-graphrequest-configurationinputenum-configurationoptionsinput)**

Use the method in the `PlaceQuoteExecutor` class to execute the Place Quote Apex API request by assigning the properties for graph request, pricing references, and configuration options.

- 

**[execute(pricingPreferenceEnum, catalogRatesPreference, graphRequest, configurationInputEnum, configurationOptionsInput)](#executepricingpreferenceenum-catalogratespreference-graphrequest-configurationinputenum-configurationoptionsinput)**

Use the method in the `PlaceQuoteExecutor` class to execute the Place Quote Apex API request by assigning the properties for graph request, pricing references, and configuration options. This method also includes the property to define fetching of rate card entries.

### execute(pricingPreferenceEnum, graphRequest, configurationInputEnum, configurationOptionsInput)

Use the method in the `PlaceQuoteExecutor` class to execute the Place Quote Apex API request by assigning the properties for graph request, pricing references, and configuration options.

#### Signature

`public static placequote.PlaceQuoteResponse execute(placequote.PricingPreferenceEnum pricingPreferenceEnum, placequote.GraphRequest graphRequest, placequote.ConfigurationInputEnum configurationInputEnum, placequote.ConfigurationOptionsInput configurationOptionsInput)`

#### Parameters

***pricingPreferenceEnum***

Type: [placequote.PricingPreferenceEnum](./apex-enum-placequote-pricingpreferenceenum.md)

Pricing preference during the quote process.

***graphRequest***

Type: [placequote.GraphRequest](./apex-class-placequote-graphrequest.md#graphrequest-class)

The sObject graph values of the quote payload to be ingested.

***configurationInputEnum***

Type: [placequote.ConfigurationInputEnum](./apex-enum-placequote-configurationinputenum.md)

Configuration input for the quote process.

***configurationOptionsInput***

Type: [placequote.ConfigurationOptionsInput](./apex-class-placequote-configurationoptionsinput.md#configurationoptionsinput-class)

Configuration options during the ingestion process.

#### Return Value

Type: [placequote.PlaceQuoteResponse](./apex-class-placequote-placequoteresponse.md#placequoteresponse-class)

### execute(pricingPreferenceEnum, catalogRatesPreference, graphRequest, configurationInputEnum, configurationOptionsInput)

Use the method in the `PlaceQuoteExecutor` class to execute the Place Quote Apex API request by assigning the properties for graph request, pricing references, and configuration options. This method also includes the property to define fetching of rate card entries.

#### Signature

`public static placequote.PlaceQuoteResponse execute(placequote.PricingPreferenceEnum pricingPreferenceEnum, placequote.CatalogRatesPreferenceEnum catalogRatesPreference, placequote.GraphRequest graphRequest, placequote.ConfigurationInputEnum configurationInputEnum, placequote.ConfigurationOptionsInput configurationOptionsInput)`

#### Parameters

***pricingPreferenceEnum***

Type: [placequote.PricingPreferenceEnum](./apex-enum-placequote-pricingpreferenceenum.md)

Pricing preference during the quote process.

***catalogRatesPreference***

Type: [placequote.CatalogRatesPreferenceEnum](./apex-enum-placequote-catalogratespreferenceenum.md)

The rate card entries defined in the catalog that must be fetched for quote line items, with usage-based pricing during the quote creation process. The `CatalogRatesPreferenceEnum` enum is available when the Usage-Based Selling feature is enabled.

***graphRequest***

Type: [placequote.GraphRequest](./apex-class-placequote-graphrequest.md#graphrequest-class)

The sObject graph values of the quote payload to be ingested.

***configurationInputEnum***

Type: [placequote.ConfigurationInputEnum](./apex-enum-placequote-configurationinputenum.md)

Configuration input for the quote process.

***configurationOptionsInput***

Type: [placequote.ConfigurationOptionsInput](./apex-class-placequote-configurationoptionsinput.md#configurationoptionsinput-class)

Configuration options during the ingestion process.

#### Return Value

Type: [placequote.PlaceQuoteResponse](./apex-class-placequote-placequoteresponse.md#placequoteresponse-class)

## PlaceQuoteRLMApexProcessor Example Implementation

To place a quote from Apex, refer to the example implementation of the `PlaceQuoteRLMApexProcessor` class.

### Namespace

[PlaceQuote](./apex-namespace-placequote.md)

### Usage

Customize this example to suit your requirements. Create the list of records to be ingested by using these steps. Replace the respective IDs with the values that are present in your org. For example, replace the value of `${Pricebook2Id}` field with the price book ID that’s present in the org.

### Example

- 

Set up a quote and quote line item. To associate the Record object with a reference identifier, create an instance of the `RecordWithReferenceRequest` class.

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

- 

To create a quote line relationship, create an instance of the `RecordResource` class.

```
PlaceQuote.RecordResource quoteLineRelationship1 = new PlaceQuote.RecordResource(QuoteLineRelationship.getSobjectType(),'POST');
    Map<String,Object> quoteLineRelationshipValues = new Map<String,Object>();
    quoteLineRelationshipValues.put('ProductRelationshipTypeId','0yoxx00000000JNAAY');
    quoteLineRelationshipValues.put('MainQuoteLineId','@{refQuoteItem2.id}');
    quoteLineRelationshipValues.put('AssociatedQuoteLineId','@{refQuoteItem1.id}');
    quoteLineRelationshipValues.put('AssociatedQuoteLinePricing','IncludedInBundlePrice');
    quoteLineRelationship1.fieldValues = quoteLineRelationshipValues;
```

- 

Create the list of records to be ingested.

```
    PlaceQuote.RecordWithReferenceRequest quoteLineRelationship = new PlaceQuote.RecordWithReferenceRequest('QuoteLineRelationship',quoteLineRelationship1);
    List<PlaceQuote.RecordWithReferenceRequest> listOfRecords = new List<PlaceQuote.RecordWithReferenceRequest>();
    listOfRecords.add(quoteItemRecords);
    listOfRecords.add(quoteLineItemRecords1);
    listOfRecords.add(quoteLineItemRecords2);
    listOfRecords.add(quoteLineRelationship);
```

- 

To contain all record objects, create an instance of the `GraphRequest` class.

**Note:**

The `CatalogRatesPreferenceEnum` enum is available when the Usage-Based Selling feature is enabled.

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-placequote-placequoterlmapexprocessor.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
