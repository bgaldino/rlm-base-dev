---
page_id: apex-class-revsalestrxn-placesalestransactionexecutor
title: PlaceSalesTransactionExecutor Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-revsalestrxn-placesalestransactionexecutor.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-revsalestrxn
legacy_page_id: apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor.htm
fetched_at: 2026-11-25
---

# PlaceSalesTransactionExecutor Class

Contains methods to place a sales transaction with details of the graph request, pricing preferences, and configuration options.

## Namespace

[RevSalesTrxn](./apex-namespace-revsalestrxn.md)

- 

**[PlaceSalesTransactionExecutor Methods](#placesalestransactionexecutor-methods)**

Learn more about the methods available with the `PlaceSalesTransactionExecutor` class.

- 

**[PlaceSalesTransactionExecutor Example Implementation](#placesalestransactionexecutor-example-implementation)**

To place a sales transaction from Apex, refer to the example implementation of the `PlaceSalesTransactionExecutor` class.

## PlaceSalesTransactionExecutor Methods

Learn more about the methods available with the `PlaceSalesTransactionExecutor` class.

The `PlaceSalesTransactionExecutor` class includes these methods.

- 

**[execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId)](#executegraphrequest-pricingpreferenceenum-configurationexecutionenum-configuratoroptions-contextid)**

Use the method in the `PlaceSalesTransactionExecutor` class to execute the Place Sales Transaction Apex API request by assigning the properties for graph request, pricing references, and configurator options.

- 

**[execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId, catalogRatesPreferenceEnum)](#executegraphrequest-pricingpreferenceenum-configurationexecutionenum-configuratoroptions-contextid-catalogratespreferenceenum)**

Use the method in the `PlaceSalesTransactionExecutor` class to execute the Place Sales Transaction Apex API request by assigning the properties for graph request, pricing references, configurator options, and catalog rates.

- 

**[execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId, catalogRatesPreferenceEnum, taxPreferenceEnum, persistPreferenceEnum)](#executegraphrequest-pricingpreferenceenum-configurationexecutionenum-configuratoroptions-contextid-catalogratespreferenceenum-taxpreferenceenum-persistpreferenceenum)**

Use the method in the `PlaceSalesTransactionExecutor` class to execute the Place Sales Transaction Apex API request by assigning the properties for graph request, pricing and tax preferences, configurator options, and catalog rates.

- 

**[execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId, taxPreferenceEnum, persistPreferenceEnum, groupRampActionEnum)](#executegraphrequest-pricingpreferenceenum-configurationexecutionenum-configuratoroptions-contextid-taxpreferenceenum-persistpreferenceenum-grouprampactionenum)**

Use the method in the `PlaceSalesTransactionExecutor` class to execute the Place Sales Transaction Apex API request by assigning the properties for graph request, pricing and tax preferences, configurator options, persist preference, and group ramp action.

- 

**[execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId, catalogRatesPreferenceEnum, taxPreferenceEnum, persistPreferenceEnum, groupRampActionEnum)](#executegraphrequest-pricingpreferenceenum-configurationexecutionenum-configuratoroptions-contextid-catalogratespreferenceenum-taxpreferenceenum-persistpreferenceenum-grouprampactionenum)**

Use the method in the `PlaceSalesTransactionExecutor` class to execute the Place Sales Transaction Apex API request by assigning the properties for graph request, pricing and tax preferences, configurator options, catalog rates, persist preference, and group ramp action.

### execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId)

Use the method in the `PlaceSalesTransactionExecutor` class to execute the Place Sales Transaction Apex API request by assigning the properties for graph request, pricing references, and configurator options.

#### Signature

`public static revsalestrxn.PlaceSalesTransactionResponse execute(revsalestrxn.GraphRequest graphRequest, revsalestrxn.PricingPreferenceEnum pricingPreferenceEnum, revsalestrxn.ConfigurationExecutionEnum configurationExecutionEnum, revsalestrxn.ConfiguratorOptions configuratorOptions, revsalestrxn.ContextId contextId)`

#### Parameters

***graphRequest***

Type: [revsalestrxn.GraphRequest](./apex-class-revsalestrxn-graphrequest.md#graphrequest-class)

The sObject graph values of the order payload to be ingested.

***pricingPreferenceEnum***

Type: [revsalestrxn.PricingPreferenceEnum](./apex-enum-revsalestrxn-pricingpreferenceenum.md)

Pricing preference during the sales transaction process.

***configurationExecutionEnum***

Type: [revsalestrxn.ConfigurationExecutionEnum](./apex-enum-revsalestrxn-configurationexecutionenum.md)

Configuration method for the sales transaction request.

***configuratorOptions***

Type: [revsalestrxn.ConfigurationOptionsInput](./apex-class-revsalestrxn-configurationoptionsinput.md#configurationoptionsinput-class)

Configuration options during the creation of the sales transaction.

***contextId***

Type: String

Context ID to assign to the sales transaction.

#### Return Value

Type: [revsalestrxn.PlaceSalesTransactionResponse](./apex-class-revsalestrxn-placesalestransactionresponse.md#placesalestransactionresponse-class)

### execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId, catalogRatesPreferenceEnum)

Use the method in the `PlaceSalesTransactionExecutor` class to execute the Place Sales Transaction Apex API request by assigning the properties for graph request, pricing references, configurator options, and catalog rates.

#### Signature

[Usage Selling](https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_usage_sellling.htm) must be enabled to use this signature.

`public static revsalestrxn.PlaceSalesTransactionResponse execute(revsalestrxn.GraphRequest graphRequest, revsalestrxn.PricingPreferenceEnum pricingPreferenceEnum, revsalestrxn.ConfigurationExecutionEnum configurationExecutionEnum, revsalestrxn.ConfiguratorOptions configuratorOptions, revsalestrxn.ContextId contextId, revsalestrxn.CatalogRatesPreferenceEnum catalogRatesPreferenceEnum)`

#### Parameters

***graphRequest***

Type: [revsalestrxn.GraphRequest](./apex-class-revsalestrxn-graphrequest.md#graphrequest-class)

The sObject graph values of the order payload to be ingested.

***pricingPreferenceEnum***

Type: [revsalestrxn.PricingPreferenceEnum](./apex-enum-revsalestrxn-pricingpreferenceenum.md)

Pricing preference during the sales transaction process.

***configurationExecutionEnum***

Type: [revsalestrxn.ConfigurationExecutionEnum](./apex-enum-revsalestrxn-configurationexecutionenum.md)

Configuration method for the sales transaction request.

***configuratorOptions***

Type: [revsalestrxn.ConfigurationOptionsInput](./apex-class-revsalestrxn-configurationoptionsinput.md#configurationoptionsinput-class)

Configuration options during the creation of the sales transaction.

***contextId***

Type: String

Context ID to assign to the sales transaction.

***catalogRatesPreferenceEnum***

Type: [revsalestrxn.CatalogRatesPreferenceEnum](./apex-enum-revsalestrxn-catalogratespreferenceenum.md)

Rate card entries defined in the catalog that must be fetched for quote line items, with usage-based selling during the place sales transaction process.

#### Return Value

Type: [revsalestrxn.PlaceSalesTransactionResponse](./apex-class-revsalestrxn-placesalestransactionresponse.md#placesalestransactionresponse-class)

### execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId, catalogRatesPreferenceEnum, taxPreferenceEnum, persistPreferenceEnum)

Use the method in the `PlaceSalesTransactionExecutor` class to execute the Place Sales Transaction Apex API request by assigning the properties for graph request, pricing and tax preferences, configurator options, and catalog rates.

#### Signature

[Usage Selling](https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_usage_sellling.htm) must be enabled to use this signature.

`public static revsalestrxn.PlaceSalesTransactionResponse execute(revsalestrxn.GraphRequest graphRequest, revsalestrxn.PricingPreferenceEnum pricingPreferenceEnum, revsalestrxn.ConfigurationExecutionEnum configurationExecutionEnum, revsalestrxn.ConfiguratorOptions configuratorOptions, revsalestrxn.ContextId contextId, revsalestrxn.CatalogRatesPreferenceEnum catalogRatesPreferenceEnum, revsalestrxn.TaxPreferenceEnum taxPreferenceEnum, revsalestrxn.PersistPreferenceEnum persistPreferenceEnum)`

#### Parameters

***graphRequest***

Type: [revsalestrxn.GraphRequest](./apex-class-revsalestrxn-graphrequest.md#graphrequest-class)

The sObject graph values of the order payload to be ingested.

***pricingPreferenceEnum***

Type: [revsalestrxn.PricingPreferenceEnum](./apex-enum-revsalestrxn-pricingpreferenceenum.md)

Pricing preference during the sales transaction process.

***configurationExecutionEnum***

Type: [revsalestrxn.ConfigurationExecutionEnum](./apex-enum-revsalestrxn-configurationexecutionenum.md)

Configuration method for the sales transaction request.

***configuratorOptions***

Type: [revsalestrxn.ConfigurationOptionsInput](./apex-class-revsalestrxn-configurationoptionsinput.md#configurationoptionsinput-class)

Configuration options during the creation of the sales transaction.

***contextId***

Type: String

Context ID to assign to the sales transaction.

***catalogRatesPreferenceEnum***

Type: [revsalestrxn.CatalogRatesPreferenceEnum](./apex-enum-revsalestrxn-catalogratespreferenceenum.md)

Rate card entries defined in the catalog that must be fetched for quote line items, with usage-based selling during the place sales transaction process.

***taxPreferenceEnum***

Type: [revsalestrxn.taxPreferenceEnum](./apex-enum-revsalestrxn-taxpreferenceenum.md)

Tax preference during the sales transaction process. Available in API version 65.0 and later.

***persistPreferenceEnum***

Type: [revsalestrxn.persistPreferenceEnum](./apex-enum-revsalestrxn-persistpreferenceenum.md)

Persist preference during the sales transaction process. Available in API version 65.0 and later.

#### Return Value

Type: [revsalestrxn.PlaceSalesTransactionResponse](./apex-class-revsalestrxn-placesalestransactionresponse.md#placesalestransactionresponse-class)

### execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId, taxPreferenceEnum, persistPreferenceEnum, groupRampActionEnum)

Use the method in the `PlaceSalesTransactionExecutor` class to execute the Place Sales Transaction Apex API request by assigning the properties for graph request, pricing and tax preferences, configurator options, persist preference, and group ramp action.

#### Signature

`public static revsalestrxn.PlaceSalesTransactionResponse execute(revsalestrxn.GraphRequest graphRequest, revsalestrxn.PricingPreferenceEnum pricingPreferenceEnum, revsalestrxn.ConfigurationExecutionEnum configurationExecutionEnum, revsalestrxn.ConfiguratorOptions configuratorOptions, revsalestrxn.ContextId contextId, revsalestrxn.TaxPreferenceEnum taxPreferenceEnum, revsalestrxn.PersistPreferenceEnum persistPreferenceEnum, revsalestrxn.GroupRampActionEnum groupRampActionEnum)`

#### Parameters

***graphRequest***

Type: [revsalestrxn.GraphRequest](./apex-class-revsalestrxn-graphrequest.md#graphrequest-class)

The sObject graph values of the order payload to be ingested.

***pricingPreferenceEnum***

Type: [revsalestrxn.PricingPreferenceEnum](./apex-enum-revsalestrxn-pricingpreferenceenum.md)

Pricing preference during the sales transaction process.

***configurationExecutionEnum***

Type: [revsalestrxn.ConfigurationExecutionEnum](./apex-enum-revsalestrxn-configurationexecutionenum.md)

Configuration method for the sales transaction request.

***configuratorOptions***

Type: [revsalestrxn.ConfigurationOptionsInput](./apex-class-revsalestrxn-configurationoptionsinput.md#configurationoptionsinput-class)

Configuration options during the creation of the sales transaction.

***contextId***

Type: String

Context ID to assign to the sales transaction.

***taxPreferenceEnum***

Type: [revsalestrxn.taxPreferenceEnum](./apex-enum-revsalestrxn-taxpreferenceenum.md)

Tax preference during the sales transaction process. Available in API version 65.0 and later.

***persistPreferenceEnum***

Type: [revsalestrxn.persistPreferenceEnum](./apex-enum-revsalestrxn-persistpreferenceenum.md)

Persist preference during the sales transaction process. Available in API version 65.0 and later.

***groupRampActionEnum***

Type: [revsalestrxn.GroupRampActionEnum](./apex-enum-revsalestrxn-grouprampactionenum.md)

Specifies the action that you want to perform on group ramp segments.

#### Return Value

Type: [revsalestrxn.PlaceSalesTransactionResponse](./apex-class-revsalestrxn-placesalestransactionresponse.md#placesalestransactionresponse-class)

### execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId, catalogRatesPreferenceEnum, taxPreferenceEnum, persistPreferenceEnum, groupRampActionEnum)

Use the method in the `PlaceSalesTransactionExecutor` class to execute the Place Sales Transaction Apex API request by assigning the properties for graph request, pricing and tax preferences, configurator options, catalog rates, persist preference, and group ramp action.

#### Signature

[Usage Selling](https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_usage_sellling.htm) must be enabled to use this signature.

`public static revsalestrxn.PlaceSalesTransactionResponse execute(revsalestrxn.GraphRequest graphRequest, revsalestrxn.PricingPreferenceEnum pricingPreferenceEnum, revsalestrxn.ConfigurationExecutionEnum configurationExecutionEnum, revsalestrxn.ConfiguratorOptions configuratorOptions, revsalestrxn.ContextId contextId, revsalestrxn.CatalogRatesPreferenceEnum catalogRatesPreferenceEnum, revsalestrxn.TaxPreferenceEnum taxPreferenceEnum, revsalestrxn.PersistPreferenceEnum persistPreferenceEnum, revsalestrxn.GroupRampActionEnum groupRampActionEnum)`

#### Parameters

***graphRequest***

Type: [revsalestrxn.GraphRequest](./apex-class-revsalestrxn-graphrequest.md#graphrequest-class)

The sObject graph values of the order payload to be ingested.

***pricingPreferenceEnum***

Type: [revsalestrxn.PricingPreferenceEnum](./apex-enum-revsalestrxn-pricingpreferenceenum.md)

Pricing preference during the sales transaction process.

***configurationExecutionEnum***

Type: [revsalestrxn.ConfigurationExecutionEnum](./apex-enum-revsalestrxn-configurationexecutionenum.md)

Configuration method for the sales transaction request.

***configuratorOptions***

Type: [revsalestrxn.ConfigurationOptionsInput](./apex-class-revsalestrxn-configurationoptionsinput.md#configurationoptionsinput-class)

Configuration options during the creation of the sales transaction.

***contextId***

Type: String

Context ID to assign to the sales transaction.

***catalogRatesPreferenceEnum***

Type: [revsalestrxn.CatalogRatesPreferenceEnum](./apex-enum-revsalestrxn-catalogratespreferenceenum.md)

Rate card entries defined in the catalog that must be fetched for quote line items, with usage-based selling during the place sales transaction process.

***taxPreferenceEnum***

Type: [revsalestrxn.taxPreferenceEnum](./apex-enum-revsalestrxn-taxpreferenceenum.md)

Tax preference during the sales transaction process. Available in API version 65.0 and later.

***persistPreferenceEnum***

Type: [revsalestrxn.persistPreferenceEnum](./apex-enum-revsalestrxn-persistpreferenceenum.md)

Persist preference during the sales transaction process. Available in API version 65.0 and later.

***groupRampActionEnum***

Type: [revsalestrxn.GroupRampActionEnum](./apex-enum-revsalestrxn-grouprampactionenum.md)

Specifies the action that you want to perform on group ramp segments.

#### Return Value

Type: [revsalestrxn.PlaceSalesTransactionResponse](./apex-class-revsalestrxn-placesalestransactionresponse.md#placesalestransactionresponse-class)

## PlaceSalesTransactionExecutor Example Implementation

To place a sales transaction from Apex, refer to the example implementation of the `PlaceSalesTransactionExecutor` class.

### Namespace

[RevSalesTrxn](./apex-namespace-revsalestrxn.md)

### Usage

Customize this example to suit your requirements. Create the list of records to be ingested by using these steps. Replace the respective IDs with the values that are present in your org. For example, replace the value of `${Pricebook2Id}` field with the price book ID that’s present in the org.

### Example

This example shows a sample request to create a sales transaction, update a quote with a quote line item, delete a quote line item, or skip or persist pricing changes. It includes these steps.

- Set up a quote and quote line item.

- To create a quote line relationship, create an instance of the `RecordResource` class. To create an object with its fields, specify the object that you want to create by using POST method. Create a map of the fields and its values by using put(key, value) operation. Assign this field map to the record object.

- To update an object’s specific fields, specify the object you want to update by using the PATCH method along with the ID of the object. Create a map of the fields and its values by using put(key, value) operation. Only certain fields on an object can be updated. Add the fields that you want to update to the map. Assign this field map to the record object.

- To associate the Record object with a reference identifier, create an instance of the `RecordWithReferenceRequest` class.

- To contain all record objects, create an instance of the `GraphRequest` class.

```
public class PlaceSalesTransactionTest {
    public static void callPSTAPI_Post() {
        RevSalesTrxn.PricingPreferenceEnum pricingPrefEnum = RevSalesTrxn.PricingPreferenceEnum.SYSTEM;
        RevSalesTrxn.ConfigurationExecutionEnum configurationExecutionEnum = RevSalesTrxn.ConfigurationExecutionEnum.SYSTEM;
        
        //Quote setup
        RevSalesTrxn.RecordResource quoteRecord = new RevSalesTrxn.RecordResource(Quote.getSobjectType(),'POST');
        Map<String,Object> quoteFieldValues = new Map<String,Object>();
        quoteFieldValues.put('Name','q-ap12');
        quoteFieldValues.put('OpportunityId','006xx000001a3e8AAA');
        quoteFieldValues.put('Pricebook2Id','01sDU000000JRX8YAO');
        quoteRecord.fieldValues = quoteFieldValues;
        
        //Quote line item setup
        
        //1st quote line item
        RevSalesTrxn.RecordResource quoteLineItemRecord1 = new RevSalesTrxn.RecordResource(QuoteLineItem.getSobjectType(),'POST');
        Map<String,Object> quoteLineItemFieldValues = new Map<String,Object>();
        quoteLineItemFieldValues.put('Product2Id','01txx0000006i7JAAQ');
        quoteLineItemFieldValues.put('PricebookEntryId','01uxx0000008yc6AAA');
        quoteLineItemFieldValues.put('Quantity','2.0');
        quoteLineItemFieldValues.put('UnitPrice','1000');
        quoteLineItemFieldValues.put('StartDate','2025-03-15');
        quoteLineItemFieldValues.put('QuoteId','@{refQuote.id}');
        quoteLineItemRecord1.fieldValues = quoteLineItemFieldValues;
        RevSalesTrxn.RecordWithReferenceRequest quoteItemRecords = new RevSalesTrxn.RecordWithReferenceRequest('refQuote',quoteRecord);
        RevSalesTrxn.RecordWithReferenceRequest quoteLineItemRecords1 = new RevSalesTrxn.RecordWithReferenceRequest('refQuoteItem1',quoteLineItemRecord1);
        
        //2nd quote line item
        RevSalesTrxn.RecordResource quoteLineItemRecord2 = new RevSalesTrxn.RecordResource(QuoteLineItem.getSobjectType(),'POST');
        Map<String,Object> quoteLineItemFieldValues2 = new Map<String,Object>();
        quoteLineItemFieldValues2.put('Product2Id','01txx0000006i7RAAQ');
        quoteLineItemFieldValues2.put('PricebookEntryId','01uxx0000008ybvAAA');
        quoteLineItemFieldValues2.put('Quantity','2.0');
        quoteLineItemFieldValues2.put('UnitPrice','7.0');
        quoteLineItemFieldValues2.put('StartDate','2025-03-15');
        quoteLineItemFieldValues2.put('QuoteId','@{refQuote.id}');
        quoteLineItemRecord2.fieldValues = quoteLineItemFieldValues2;
        RevSalesTrxn.RecordWithReferenceRequest quoteLineItemRecords2 = new RevSalesTrxn.RecordWithReferenceRequest('refQuoteItem2',quoteLineItemRecord2);
        
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords = new List<RevSalesTrxn.RecordWithReferenceRequest>();
        listOfRecords.add(quoteItemRecords);
        listOfRecords.add(quoteLineItemRecords1);
        listOfRecords.add(quoteLineItemRecords2);
        
        
        RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('test',listOfRecords);
        System.debug(graph);
        
        //Place sales transaction API call - There are different executor signatures detailed in the documentation
        RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(graph, pricingPrefEnum, configurationExecutionEnum, new RevSalesTrxn.ConfigurationOptionsInput(), null, null, null, null);
        //If you do not have Usage Based Selling Feature, you can use the signatures without catalog rates enum
        //RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(graph, pricingPrefEnum, configurationExecutionEnum, new RevSalesTrxn.ConfigurationOptionsInput(), null);
        System.debug(resp);
    }
    
    public static void callPSTAPI_Post_Skip_Tax_Skip_Persist() {
        RevSalesTrxn.PricingPreferenceEnum pricingPrefEnum = RevSalesTrxn.PricingPreferenceEnum.SYSTEM;
        RevSalesTrxn.ConfigurationExecutionEnum configurationExecutionEnum = RevSalesTrxn.ConfigurationExecutionEnum.SYSTEM;
        RevSalesTrxn.TaxPreferenceEnum taxPrefEnum = RevSalesTrxn.TaxPreferenceEnum.SKIP;
        RevSalesTrxn.PersistPreferenceEnum persistPrefEnum = RevSalesTrxn.PersistPreferenceEnum.SKIP;
        
        //Quote setup
        RevSalesTrxn.RecordResource quoteRecord = new RevSalesTrxn.RecordResource(Quote.getSobjectType(),'POST');
        Map<String,Object> quoteFieldValues = new Map<String,Object>();
        quoteFieldValues.put('Name','q-ap12');
        quoteFieldValues.put('OpportunityId','006xx000001a3e8AAA');
        quoteFieldValues.put('Pricebook2Id','01sDU000000JRX8YAO');
        quoteRecord.fieldValues = quoteFieldValues;
        
        //Quote line item setup
        
        //1st quote line item
        RevSalesTrxn.RecordResource quoteLineItemRecord1 = new RevSalesTrxn.RecordResource(QuoteLineItem.getSobjectType(),'POST');
        Map<String,Object> quoteLineItemFieldValues = new Map<String,Object>();
        quoteLineItemFieldValues.put('Product2Id','01txx0000006i7JAAQ');
        quoteLineItemFieldValues.put('PricebookEntryId','01uxx0000008yc6AAA');
        quoteLineItemFieldValues.put('Quantity','2.0');
        quoteLineItemFieldValues.put('UnitPrice','1000');
        quoteLineItemFieldValues.put('StartDate','2025-03-15');
        quoteLineItemFieldValues.put('QuoteId','@{refQuote.id}');
        quoteLineItemRecord1.fieldValues = quoteLineItemFieldValues;
        RevSalesTrxn.RecordWithReferenceRequest quoteItemRecords = new RevSalesTrxn.RecordWithReferenceRequest('refQuote',quoteRecord);
        RevSalesTrxn.RecordWithReferenceRequest quoteLineItemRecords1 = new RevSalesTrxn.RecordWithReferenceRequest('refQuoteItem1',quoteLineItemRecord1);
        
        //2nd quote line item
        RevSalesTrxn.RecordResource quoteLineItemRecord2 = new RevSalesTrxn.RecordResource(QuoteLineItem.getSobjectType(),'POST');
        Map<String,Object> quoteLineItemFieldValues2 = new Map<String,Object>();
        quoteLineItemFieldValues2.put('Product2Id','01txx0000006i7RAAQ');
        quoteLineItemFieldValues2.put('PricebookEntryId','01uxx0000008ybvAAA');
        quoteLineItemFieldValues2.put('Quantity','2.0');
        quoteLineItemFieldValues2.put('UnitPrice','7.0');
        quoteLineItemFieldValues2.put('StartDate','2025-03-15');
        quoteLineItemFieldValues2.put('QuoteId','@{refQuote.id}');
        quoteLineItemRecord2.fieldValues = quoteLineItemFieldValues2;
        RevSalesTrxn.RecordWithReferenceRequest quoteLineItemRecords2 = new RevSalesTrxn.RecordWithReferenceRequest('refQuoteItem2',quoteLineItemRecord2);
        
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords = new List<RevSalesTrxn.RecordWithReferenceRequest>();
        listOfRecords.add(quoteItemRecords);
        listOfRecords.add(quoteLineItemRecords1);
        listOfRecords.add(quoteLineItemRecords2);
        
        
        RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('test',listOfRecords);
        System.debug(graph);
        
        //Place sales transaction API call
        RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(graph, pricingPrefEnum, configurationExecutionEnum, new RevSalesTrxn.ConfigurationOptionsInput(), null, null, taxPrefEnum, persistPrefEnum);
        System.debug(resp);
    }
    
    public static void callPSTAPI_Patch() {
        
        // Apex test to update a quote with a quote line item
        RevSalesTrxn.PricingPreferenceEnum pricingPrefEnum = RevSalesTrxn.PricingPreferenceEnum.SYSTEM;
        RevSalesTrxn.ConfigurationExecutionEnum configurationExecutionEnum = RevSalesTrxn.ConfigurationExecutionEnum.SYSTEM;
        
        //Quote setup
        RevSalesTrxn.RecordResource quoteRecord = new RevSalesTrxn.RecordResource(Quote.getSobjectType(),'PATCH','0Q0xx0000004CYsCAM');
        RevSalesTrxn.RecordWithReferenceRequest quoteItemRecords = new RevSalesTrxn.RecordWithReferenceRequest('refQuote',quoteRecord);
        
        //Quote line item setup
        //New quote line item
        RevSalesTrxn.RecordResource quoteLineItemRecord = new RevSalesTrxn.RecordResource(QuoteLineItem.getSobjectType(),'POST');
        Map<String,Object> quoteLineItemFieldValues = new Map<String,Object>();
        quoteLineItemFieldValues.put('Product2Id','01txx0000006i7KAAQ');
        quoteLineItemFieldValues.put('PricebookEntryId','01uxx0000008ycFAAQ');
        quoteLineItemFieldValues.put('Quantity','2.0');
        quoteLineItemFieldValues.put('UnitPrice','7.0');
        quoteLineItemFieldValues.put('StartDate','2025-03-15');
        quoteLineItemFieldValues.put('QuoteId','@{refQuote.id}');
        quoteLineItemRecord.fieldValues = quoteLineItemFieldValues;
        RevSalesTrxn.RecordWithReferenceRequest quoteLineItemRecords = new RevSalesTrxn.RecordWithReferenceRequest('refQuoteItem',quoteLineItemRecord);
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords = new List<RevSalesTrxn.RecordWithReferenceRequest>();
        listOfRecords.add(quoteItemRecords);
        listOfRecords.add(quoteLineItemRecords);
        RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('test', listOfRecords);
        
        //Place sales transaction API call
        RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(graph, pricingPrefEnum, configurationExecutionEnum, new RevSalesTrxn.ConfigurationOptionsInput(), null, null, null, null);
        System.debug(resp);
    }

    public static void callPSTAPI_Patch_Skip_Config_Skip_Pricing() {
        
        // Apex test to update a quote with a quote line item
        RevSalesTrxn.PricingPreferenceEnum pricingPrefEnum = RevSalesTrxn.PricingPreferenceEnum.SKIP;
        RevSalesTrxn.ConfigurationExecutionEnum configurationExecutionEnum = RevSalesTrxn.ConfigurationExecutionEnum.SKIP;
        
        //Quote setup
        RevSalesTrxn.RecordResource quoteRecord = new RevSalesTrxn.RecordResource(Quote.getSobjectType(),'PATCH','0Q0xx0000004CYsCAM');
        RevSalesTrxn.RecordWithReferenceRequest quoteItemRecords = new RevSalesTrxn.RecordWithReferenceRequest('refQuote',quoteRecord);
        
        //Quote line item setup
        //New quote line item
        RevSalesTrxn.RecordResource quoteLineItemRecord = new RevSalesTrxn.RecordResource(QuoteLineItem.getSobjectType(),'POST');
        Map<String,Object> quoteLineItemFieldValues = new Map<String,Object>();
        quoteLineItemFieldValues.put('Product2Id','01txx0000006i7KAAQ');
        quoteLineItemFieldValues.put('PricebookEntryId','01uxx0000008ycFAAQ');
        quoteLineItemFieldValues.put('Quantity','2.0');
        quoteLineItemFieldValues.put('UnitPrice','7.0');
        quoteLineItemFieldValues.put('StartDate','2025-03-15');
        quoteLineItemFieldValues.put('QuoteId','@{refQuote.id}');
        quoteLineItemRecord.fieldValues = quoteLineItemFieldValues;
        RevSalesTrxn.RecordWithReferenceRequest quoteLineItemRecords = new RevSalesTrxn.RecordWithReferenceRequest('refQuoteItem',quoteLineItemRecord);
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords = new List<RevSalesTrxn.RecordWithReferenceRequest>();
        listOfRecords.add(quoteItemRecords);
        listOfRecords.add(quoteLineItemRecords);
        RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('test', listOfRecords);
        
        //Place sales transaction API call
        RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(graph, pricingPrefEnum, configurationExecutionEnum, new RevSalesTrxn.ConfigurationOptionsInput(), null, null, null, null);
        System.debug(resp);
    }

    public static void callPSTAPI_Patch_With_ContextId() {
        
          // Apex test to update a quote with a quote line item
        RevSalesTrxn.PricingPreferenceEnum pricingPrefEnum = RevSalesTrxn.PricingPreferenceEnum.SYSTEM;
        RevSalesTrxn.ConfigurationExecutionEnum configurationExecutionEnum = RevSalesTrxn.ConfigurationExecutionEnum.SYSTEM;
        
        //Quote setup
       String contextId = 'MY_CONTEXT_ID';
        RevSalesTrxn.RecordResource quoteRecord = new RevSalesTrxn.RecordResource(Quote.getSobjectType(),'PATCH','0Q0xx0000004CYsCAM');
        RevSalesTrxn.RecordWithReferenceRequest quoteItemRecords = new RevSalesTrxn.RecordWithReferenceRequest('refQuote',quoteRecord);
        
        //Quote line item setup
        //New quote line item
        RevSalesTrxn.RecordResource quoteLineItemRecord = new RevSalesTrxn.RecordResource(QuoteLineItem.getSobjectType(),'POST');
        Map<String,Object> quoteLineItemFieldValues = new Map<String,Object>();
        quoteLineItemFieldValues.put('Product2Id','01txx0000006i7KAAQ');
        quoteLineItemFieldValues.put('PricebookEntryId','01uxx0000008ycFAAQ');
        quoteLineItemFieldValues.put('Quantity','2.0');
        quoteLineItemFieldValues.put('UnitPrice','7.0');
        quoteLineItemFieldValues.put('StartDate','2025-03-15');
        quoteLineItemFieldValues.put('QuoteId','@{refQuote.id}');
        quoteLineItemRecord.fieldValues = quoteLineItemFieldValues;
        RevSalesTrxn.RecordWithReferenceRequest quoteLineItemRecords = new RevSalesTrxn.RecordWithReferenceRequest('refQuoteItem',quoteLineItemRecord);
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords = new List<RevSalesTrxn.RecordWithReferenceRequest>();
        listOfRecords.add(quoteItemRecords);
        listOfRecords.add(quoteLineItemRecords);
        RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('test', listOfRecords);
        
        //Place sales transaction API call
        RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(graph, pricingPrefEnum, configurationExecutionEnum, new RevSalesTrxn.ConfigurationOptionsInput(), contextId, null, null, null);
        System.debug(resp);
    }

    public static void callPSTAPI_Delete() {
        
        // Apex test to update a quote with a quote line item
        RevSalesTrxn.PricingPreferenceEnum pricingPrefEnum = RevSalesTrxn.PricingPreferenceEnum.SYSTEM;
        RevSalesTrxn.ConfigurationExecutionEnum configurationExecutionEnum = RevSalesTrxn.ConfigurationExecutionEnum.SYSTEM;
        
        //Quote setup
        RevSalesTrxn.RecordResource quoteRecord = new RevSalesTrxn.RecordResource(Quote.getSobjectType(),'PATCH','0Q0xx0000004CYsCAM');
        RevSalesTrxn.RecordWithReferenceRequest quoteItemRecords = new RevSalesTrxn.RecordWithReferenceRequest('refQuote',quoteRecord);
        
        //Quote line item setup
        //Delete a quote line item
        RevSalesTrxn.RecordResource quoteLineItemRecord = new RevSalesTrxn.RecordResource(QuoteLineItem.getSobjectType(),'DELETE','0QLxx0000004CYsCAM');
        RevSalesTrxn.RecordWithReferenceRequest quoteLineItemRecords = new RevSalesTrxn.RecordWithReferenceRequest('refQuoteItem',quoteLineItemRecord);
        List<RevSalesTrxn.RecordWithReferenceRequest> listOfRecords = new List<RevSalesTrxn.RecordWithReferenceRequest>();
        listOfRecords.add(quoteItemRecords);
        listOfRecords.add(quoteLineItemRecords);
        RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('test',listOfRecords);
        
        //Place sales transaction API call
        RevSalesTrxn.PlaceSalesTransactionResponse resp =
            RevSalesTrxn.PlaceSalesTransactionExecutor.execute(graph, pricingPrefEnum, configurationExecutionEnum, new RevSalesTrxn.ConfigurationOptionsInput(), null,null, null, null);
        System.debug(resp);
    }
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-revsalestrxn-placesalestransactionexecutor.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
