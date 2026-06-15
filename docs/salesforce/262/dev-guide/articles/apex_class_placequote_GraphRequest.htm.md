---
page_id: apex_class_placequote_GraphRequest.htm
title: GraphRequest Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_placequote_GraphRequest.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_placequote.htm
fetched_at: 2026-06-09
---

# GraphRequest Class

Contains constructors and properties to set the graph ID and a list of records to be
ingested. The list of records is specified in a key-value map format that contains the field
values of an order.

## Namespace

[PlaceQuote](./apex_namespace_placequote.htm.md "The PlaceQuote namespace provides classes and methods to create or update quotes with pricing preferences and configuration options.")

## Example

Invoke the Place Quote Apex API by using these steps.

- Set up a quote and quote line item. To associate the Record object with a reference
  identifier, create an instance of the `RecordWithReferenceRequest` class.

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
- Create the list of records to be ingested.

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

  The `CatalogRatesPreferenceEnum` enum is available when the Usage-Based Selling
  feature is enabled.

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

- **[GraphRequest Constructors](./apex_class_placequote_GraphRequest.htm.md#apex_placequote_GraphRequest_constructors)**  
  Learn more about the available constructors with the `GraphRequest` class.
- **[GraphRequest Properties](./apex_class_placequote_GraphRequest.htm.md#apex_placequote_GraphRequest_properties)**

## GraphRequest Constructors

Learn more about the available constructors with the `GraphRequest` class.

The `GraphRequest` class includes these constructors.

- **[GraphRequest(graphId, records)](./apex_class_placequote_GraphRequest.htm.md#apex_placequote_GraphRequest_ctor)**  
  Creates an instance of the `GraphRequest` class to assign the graph ID and a list of records to be ingested.

### GraphRequest(graphId, records)

Creates an instance of the `GraphRequest` class
to assign the graph ID and a list of records to be ingested.

#### Signature

`public GraphRequest(String graphId, List<placequote.RecordWithReferenceRequest> records)`

#### Parameters

graphId
:   Type: String
:   ID of the graph.

records
:   Type: List<[placequote.RecordWithReferenceRequest](./apex_class_placequote_RecordWithReferenceRequest.htm.md#apex_class_placequote_RecordWithReferenceRequest "Contains constructors and properties to associate a record object with a reference identifier.")>
:   List of records to be ingested.

## GraphRequest Properties

The following are properties for `GraphRequest`.

- **[graphId](./apex_class_placequote_GraphRequest.htm.md#apex_placequote_GraphRequest_graphId)**  
  Set the `graphId` property to assign the ID value of the graph.

### graphId

Set the `graphId` property to assign the ID value of
the graph.

#### Signature

`public String graphId {get; set;}`

#### Property Value

Type: String
