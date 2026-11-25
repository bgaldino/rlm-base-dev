---
page_id: apex-class-placequote-graphrequest
title: GraphRequest Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-placequote-graphrequest.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-placequote
legacy_page_id: apex_class_placequote_GraphRequest.htm
fetched_at: 2026-11-25
---

# GraphRequest Class

Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains the field values of an order.

## Namespace

[PlaceQuote](./apex-namespace-placequote.md)

## Example

Invoke the Place Quote Apex API by using these steps.

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

- 

**[GraphRequest Constructors](#graphrequest-constructors)**

Learn more about the available constructors with the `GraphRequest` class.

- 

**[GraphRequest Properties](#graphrequest-properties)**

## GraphRequest Constructors

Learn more about the available constructors with the `GraphRequest` class.

The `GraphRequest` class includes these constructors.

- 

**[GraphRequest(graphId, records)](#graphrequestgraphid-records)**

Creates an instance of the `GraphRequest` class to assign the graph ID and a list of records to be ingested.

### GraphRequest(graphId, records)

Creates an instance of the `GraphRequest` class to assign the graph ID and a list of records to be ingested.

#### Signature

`public GraphRequest(String graphId, List<placequote.RecordWithReferenceRequest> records)`

#### Parameters

***graphId***

Type: String

ID of the graph.

***records***

Type: List<[placequote.RecordWithReferenceRequest](./apex-class-placequote-recordwithreferencerequest.md#recordwithreferencerequest-class)>

List of records to be ingested.

## GraphRequest Properties

The following are properties for `GraphRequest`.

- 

**[graphId](#graphid)**

Set the `graphId` property to assign the ID value of the graph.

### graphId

Set the `graphId` property to assign the ID value of the graph.

#### Signature

`public String graphId {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-placequote-graphrequest.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
