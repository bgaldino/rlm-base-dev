---
page_id: apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor.htm
title: PlaceSalesTransactionExecutor Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_RevSalesTrxn.htm
fetched_at: 2026-06-09
---

# PlaceSalesTransactionExecutor Class

Contains methods to place a sales transaction with details of the graph request,
pricing preferences, and configuration options.

## Namespace

[RevSalesTrxn](./apex_namespace_RevSalesTrxn.htm.md "Create a sales transaction, such as a quote or an order, with integrated pricing and configuration. Additionally, update an order or a quote, and insert and delete order or quote line items to calculate the estimated tax.")

- **[PlaceSalesTransactionExecutor Methods](./apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor.htm.md#apex_RevSalesTrxn_PlaceSalesTransactionExecutor_methods)**  
  Learn more about the methods available with the `PlaceSalesTransactionExecutor` class.
- **[PlaceSalesTransactionExecutor Example Implementation](./apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor.htm.md#apex_RevSalesTrxn_PlaceSalesTransactionExecutor_example_implementation)**  
  To place a sales transaction from Apex, refer to the example implementation of the `PlaceSalesTransactionExecutor` class.

## PlaceSalesTransactionExecutor Methods

Learn more about the methods available with the `PlaceSalesTransactionExecutor` class.

The `PlaceSalesTransactionExecutor` class includes these
methods.

- **[execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId)](./apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor.htm.md#apex_RevSalesTrxn_PlaceSalesTransactionExecutor_execute)**  
  Use the method in the `PlaceSalesTransactionExecutor` class to execute the Place Sales Transaction Apex API request by assigning the properties for graph request, pricing references, and configurator options.
- **[execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId, catalogRatesPreferenceEnum)](./apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor.htm.md#apex_RevSalesTrxn_PlaceSalesTransactionExecutor_execute_1)**  
  Use the method in the `PlaceSalesTransactionExecutor` class to execute the Place Sales Transaction Apex API request by assigning the properties for graph request, pricing references, configurator options, and catalog rates.
- **[execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId, catalogRatesPreferenceEnum, taxPreferenceEnum, persistPreferenceEnum)](./apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor.htm.md#apex_RevSalesTrxn_PlaceSalesTransactionExecutor_execute_2)**  
  Use the method in the `PlaceSalesTransactionExecutor` class to execute the Place Sales Transaction Apex API request by assigning the properties for graph request, pricing and tax preferences, configurator options, and catalog rates.
- **[execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId, taxPreferenceEnum, persistPreferenceEnum, groupRampActionEnum)](./apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor.htm.md#apex_RevSalesTrxn_PlaceSalesTransactionExecutor_execute_3)**  
  Use the method in the `PlaceSalesTransactionExecutor` class to execute the Place Sales Transaction Apex API request by assigning the properties for graph request, pricing and tax preferences, configurator options, persist preference, and group ramp action.
- **[execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId, catalogRatesPreferenceEnum, taxPreferenceEnum, persistPreferenceEnum, groupRampActionEnum)](./apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor.htm.md#apex_RevSalesTrxn_PlaceSalesTransactionExecutor_execute_4)**  
  Use the method in the `PlaceSalesTransactionExecutor` class to execute the Place Sales Transaction Apex API request by assigning the properties for graph request, pricing and tax preferences, configurator options, catalog rates, persist preference, and group ramp action.

### execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId)

Use the method in the `PlaceSalesTransactionExecutor`
class to execute the Place Sales Transaction Apex API request by assigning the properties for
graph request, pricing references, and configurator options.

#### Signature

`public static revsalestrxn.PlaceSalesTransactionResponse
execute(revsalestrxn.GraphRequest graphRequest, revsalestrxn.PricingPreferenceEnum
pricingPreferenceEnum, revsalestrxn.ConfigurationExecutionEnum configurationExecutionEnum,
revsalestrxn.ConfiguratorOptions configuratorOptions, revsalestrxn.ContextId
contextId)`

#### Parameters

graphRequest
:   Type: [revsalestrxn.GraphRequest](./apex_class_RevSalesTrxn_GraphRequest.htm.md#apex_class_RevSalesTrxn_GraphRequest "Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains field values.")
:   The sObject graph values of the order payload to be ingested.

pricingPreferenceEnum
:   Type: [revsalestrxn.PricingPreferenceEnum](./apex_enum_RevSalesTrxn_PricingPreferenceEnum.htm.md "Specifies the pricing preference during the creation of a sales transaction.")
:   Pricing preference during the sales transaction process.

configurationExecutionEnum
:   Type: [revsalestrxn.ConfigurationExecutionEnum](./apex_enum_RevSalesTrxn_ConfigurationExecutionEnum.htm.md "Specifies the configuration method for the place sales transaction request.")
:   Configuration method for the sales transaction request.

configuratorOptions
:   Type: [revsalestrxn.ConfigurationOptionsInput](./apex_class_RevSalesTrxn_ConfigurationOptionsInput.htm.md#apex_class_RevSalesTrxn_ConfigurationOptionsInput "Contains methods and properties to set the configuration options for the input to the product configurator.")
:   Configuration options during the creation of the sales transaction.

contextId
:   Type: String
:   Context ID to assign to the sales transaction.

#### Return Value

Type: [revsalestrxn.PlaceSalesTransactionResponse](./apex_class_RevSalesTrxn_PlaceSalesTransactionResponse.htm.md#apex_class_RevSalesTrxn_PlaceSalesTransactionResponse "Contains properties to hold the response to the place sales transaction request.")

### execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId, catalogRatesPreferenceEnum)

Use the method in the `PlaceSalesTransactionExecutor`
class to execute the Place Sales Transaction Apex API request by assigning the properties for
graph request, pricing references, configurator options, and catalog rates.

#### Signature

[Usage Selling](https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_usage_sellling.htm&language=en_US "HTML (New Window)") must be enabled
to use this signature.

`public static
revsalestrxn.PlaceSalesTransactionResponse execute(revsalestrxn.GraphRequest graphRequest,
revsalestrxn.PricingPreferenceEnum pricingPreferenceEnum,
revsalestrxn.ConfigurationExecutionEnum configurationExecutionEnum,
revsalestrxn.ConfiguratorOptions configuratorOptions, revsalestrxn.ContextId contextId,
revsalestrxn.CatalogRatesPreferenceEnum
catalogRatesPreferenceEnum)`

#### Parameters

graphRequest
:   Type: [revsalestrxn.GraphRequest](./apex_class_RevSalesTrxn_GraphRequest.htm.md#apex_class_RevSalesTrxn_GraphRequest "Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains field values.")
:   The sObject graph values of the order payload to be ingested.

pricingPreferenceEnum
:   Type: [revsalestrxn.PricingPreferenceEnum](./apex_enum_RevSalesTrxn_PricingPreferenceEnum.htm.md "Specifies the pricing preference during the creation of a sales transaction.")
:   Pricing preference during the sales transaction process.

configurationExecutionEnum
:   Type: [revsalestrxn.ConfigurationExecutionEnum](./apex_enum_RevSalesTrxn_ConfigurationExecutionEnum.htm.md "Specifies the configuration method for the place sales transaction request.")
:   Configuration method for the sales transaction request.

configuratorOptions
:   Type: [revsalestrxn.ConfigurationOptionsInput](./apex_class_RevSalesTrxn_ConfigurationOptionsInput.htm.md#apex_class_RevSalesTrxn_ConfigurationOptionsInput "Contains methods and properties to set the configuration options for the input to the product configurator.")
:   Configuration options during the creation of the sales transaction.

contextId
:   Type: String
:   Context ID to assign to the sales transaction.

catalogRatesPreferenceEnum
:   Type: [revsalestrxn.CatalogRatesPreferenceEnum](./apex_enum_RevSalesTrxn_CatalogRatesPreferenceEnum.htm.md "Specifies the rate card entries defined in the catalog that must be fetched for quote line items, with usage-based selling during the place sales transaction process.")
:   Rate card entries defined in the catalog that must be fetched for quote line items,
    with usage-based selling during the place sales transaction process.

#### Return Value

Type: [revsalestrxn.PlaceSalesTransactionResponse](./apex_class_RevSalesTrxn_PlaceSalesTransactionResponse.htm.md#apex_class_RevSalesTrxn_PlaceSalesTransactionResponse "Contains properties to hold the response to the place sales transaction request.")

### execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId, catalogRatesPreferenceEnum, taxPreferenceEnum, persistPreferenceEnum)

Use the method in the `PlaceSalesTransactionExecutor`
class to execute the Place Sales Transaction Apex API request by assigning the properties for
graph request, pricing and tax preferences, configurator options, and catalog rates.

#### Signature

[Usage Selling](https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_usage_sellling.htm&language=en_US "HTML (New Window)") must be enabled
to use this signature.

`public static revsalestrxn.PlaceSalesTransactionResponse
execute(revsalestrxn.GraphRequest graphRequest, revsalestrxn.PricingPreferenceEnum
pricingPreferenceEnum, revsalestrxn.ConfigurationExecutionEnum configurationExecutionEnum,
revsalestrxn.ConfiguratorOptions configuratorOptions, revsalestrxn.ContextId contextId,
revsalestrxn.CatalogRatesPreferenceEnum catalogRatesPreferenceEnum,
revsalestrxn.TaxPreferenceEnum taxPreferenceEnum, revsalestrxn.PersistPreferenceEnum
persistPreferenceEnum)`

#### Parameters

graphRequest
:   Type: [revsalestrxn.GraphRequest](./apex_class_RevSalesTrxn_GraphRequest.htm.md#apex_class_RevSalesTrxn_GraphRequest "Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains field values.")
:   The sObject graph values of the order payload to be ingested.

pricingPreferenceEnum
:   Type: [revsalestrxn.PricingPreferenceEnum](./apex_enum_RevSalesTrxn_PricingPreferenceEnum.htm.md "Specifies the pricing preference during the creation of a sales transaction.")
:   Pricing preference during the sales transaction process.

configurationExecutionEnum
:   Type: [revsalestrxn.ConfigurationExecutionEnum](./apex_enum_RevSalesTrxn_ConfigurationExecutionEnum.htm.md "Specifies the configuration method for the place sales transaction request.")
:   Configuration method for the sales transaction request.

configuratorOptions
:   Type: [revsalestrxn.ConfigurationOptionsInput](./apex_class_RevSalesTrxn_ConfigurationOptionsInput.htm.md#apex_class_RevSalesTrxn_ConfigurationOptionsInput "Contains methods and properties to set the configuration options for the input to the product configurator.")
:   Configuration options during the creation of the sales transaction.

contextId
:   Type: String
:   Context ID to assign to the sales transaction.

catalogRatesPreferenceEnum
:   Type: [revsalestrxn.CatalogRatesPreferenceEnum](./apex_enum_RevSalesTrxn_CatalogRatesPreferenceEnum.htm.md "Specifies the rate card entries defined in the catalog that must be fetched for quote line items, with usage-based selling during the place sales transaction process.")
:   Rate card entries defined in the catalog that must be fetched for quote line items,
    with usage-based selling during the place sales transaction process.

taxPreferenceEnum
:   Type: [revsalestrxn.taxPreferenceEnum](./apex_enum_RevSalesTrxn_TaxPreferenceEnum.htm.md "Specifies whether to execute or skip the tax calculation step for each sales transaction record. Available in API version 65.0 and later.")
:   Tax preference during the sales transaction process. Available in API version 65.0 and
    later.

persistPreferenceEnum
:   Type: [revsalestrxn.persistPreferenceEnum](./apex_enum_RevSalesTrxn_PersistPreferenceEnum.htm.md "Specifies whether to persist pricing changes for each sales transaction record. Available in API version 65.0 and later.")
:   Persist preference during the sales transaction process. Available in API version 65.0
    and later.

#### Return Value

Type: [revsalestrxn.PlaceSalesTransactionResponse](./apex_class_RevSalesTrxn_PlaceSalesTransactionResponse.htm.md#apex_class_RevSalesTrxn_PlaceSalesTransactionResponse "Contains properties to hold the response to the place sales transaction request.")

### execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId, taxPreferenceEnum, persistPreferenceEnum, groupRampActionEnum)

Use the method in the `PlaceSalesTransactionExecutor`
class to execute the Place Sales Transaction Apex API request by assigning the properties for
graph request, pricing and tax preferences, configurator options, persist preference, and group ramp action.

#### Signature

`public static revsalestrxn.PlaceSalesTransactionResponse
execute(revsalestrxn.GraphRequest graphRequest, revsalestrxn.PricingPreferenceEnum
pricingPreferenceEnum, revsalestrxn.ConfigurationExecutionEnum configurationExecutionEnum,
revsalestrxn.ConfiguratorOptions configuratorOptions, revsalestrxn.ContextId contextId,
revsalestrxn.TaxPreferenceEnum taxPreferenceEnum, revsalestrxn.PersistPreferenceEnum
persistPreferenceEnum, revsalestrxn.GroupRampActionEnum groupRampActionEnum)`

#### Parameters

graphRequest
:   Type: [revsalestrxn.GraphRequest](./apex_class_RevSalesTrxn_GraphRequest.htm.md#apex_class_RevSalesTrxn_GraphRequest "Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains field values.")
:   The sObject graph values of the order payload to be ingested.

pricingPreferenceEnum
:   Type: [revsalestrxn.PricingPreferenceEnum](./apex_enum_RevSalesTrxn_PricingPreferenceEnum.htm.md "Specifies the pricing preference during the creation of a sales transaction.")
:   Pricing preference during the sales transaction process.

configurationExecutionEnum
:   Type: [revsalestrxn.ConfigurationExecutionEnum](./apex_enum_RevSalesTrxn_ConfigurationExecutionEnum.htm.md "Specifies the configuration method for the place sales transaction request.")
:   Configuration method for the sales transaction request.

configuratorOptions
:   Type: [revsalestrxn.ConfigurationOptionsInput](./apex_class_RevSalesTrxn_ConfigurationOptionsInput.htm.md#apex_class_RevSalesTrxn_ConfigurationOptionsInput "Contains methods and properties to set the configuration options for the input to the product configurator.")
:   Configuration options during the creation of the sales transaction.

contextId
:   Type: String
:   Context ID to assign to the sales transaction.

taxPreferenceEnum
:   Type: [revsalestrxn.taxPreferenceEnum](./apex_enum_RevSalesTrxn_TaxPreferenceEnum.htm.md "Specifies whether to execute or skip the tax calculation step for each sales transaction record. Available in API version 65.0 and later.")
:   Tax preference during the sales transaction process. Available in API version 65.0 and
    later.

persistPreferenceEnum
:   Type: [revsalestrxn.persistPreferenceEnum](./apex_enum_RevSalesTrxn_PersistPreferenceEnum.htm.md "Specifies whether to persist pricing changes for each sales transaction record. Available in API version 65.0 and later.")
:   Persist preference during the sales transaction process. Available in API version 65.0
    and later.

groupRampActionEnum
:   Type: [revsalestrxn.GroupRampActionEnum](./apex_enum_RevSalesTrxn_GroupRampActionEnum.htm.md "Specifies the action ‌that you want to perform on group ramp segments. Additionally, you can also convert a non-ramped group into a ramped group.")
:   Specifies the action that you want to perform on group ramp segments.

#### Return Value

Type: [revsalestrxn.PlaceSalesTransactionResponse](./apex_class_RevSalesTrxn_PlaceSalesTransactionResponse.htm.md#apex_class_RevSalesTrxn_PlaceSalesTransactionResponse "Contains properties to hold the response to the place sales transaction request.")

### execute(graphRequest, pricingPreferenceEnum, configurationExecutionEnum, configuratorOptions, contextId, catalogRatesPreferenceEnum, taxPreferenceEnum, persistPreferenceEnum, groupRampActionEnum)

Use the method in the `PlaceSalesTransactionExecutor`
class to execute the Place Sales Transaction Apex API request by assigning the properties for
graph request, pricing and tax preferences, configurator options, catalog rates, persist preference, and group ramp action.

#### Signature

[Usage Selling](https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_usage_sellling.htm&language=en_US "HTML (New Window)") must be enabled to use this signature.

`public static revsalestrxn.PlaceSalesTransactionResponse
execute(revsalestrxn.GraphRequest graphRequest, revsalestrxn.PricingPreferenceEnum
pricingPreferenceEnum, revsalestrxn.ConfigurationExecutionEnum configurationExecutionEnum,
revsalestrxn.ConfiguratorOptions configuratorOptions, revsalestrxn.ContextId contextId,
revsalestrxn.CatalogRatesPreferenceEnum catalogRatesPreferenceEnum,
revsalestrxn.TaxPreferenceEnum taxPreferenceEnum, revsalestrxn.PersistPreferenceEnum
persistPreferenceEnum, revsalestrxn.GroupRampActionEnum groupRampActionEnum)`

#### Parameters

graphRequest
:   Type: [revsalestrxn.GraphRequest](./apex_class_RevSalesTrxn_GraphRequest.htm.md#apex_class_RevSalesTrxn_GraphRequest "Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains field values.")
:   The sObject graph values of the order payload to be ingested.

pricingPreferenceEnum
:   Type: [revsalestrxn.PricingPreferenceEnum](./apex_enum_RevSalesTrxn_PricingPreferenceEnum.htm.md "Specifies the pricing preference during the creation of a sales transaction.")
:   Pricing preference during the sales transaction process.

configurationExecutionEnum
:   Type: [revsalestrxn.ConfigurationExecutionEnum](./apex_enum_RevSalesTrxn_ConfigurationExecutionEnum.htm.md "Specifies the configuration method for the place sales transaction request.")
:   Configuration method for the sales transaction request.

configuratorOptions
:   Type: [revsalestrxn.ConfigurationOptionsInput](./apex_class_RevSalesTrxn_ConfigurationOptionsInput.htm.md#apex_class_RevSalesTrxn_ConfigurationOptionsInput "Contains methods and properties to set the configuration options for the input to the product configurator.")
:   Configuration options during the creation of the sales transaction.

contextId
:   Type: String
:   Context ID to assign to the sales transaction.

catalogRatesPreferenceEnum
:   Type: [revsalestrxn.CatalogRatesPreferenceEnum](./apex_enum_RevSalesTrxn_CatalogRatesPreferenceEnum.htm.md "Specifies the rate card entries defined in the catalog that must be fetched for quote line items, with usage-based selling during the place sales transaction process.")
:   Rate card entries defined in the catalog that must be fetched for quote line items, with usage-based selling during the place sales transaction process.

taxPreferenceEnum
:   Type: [revsalestrxn.taxPreferenceEnum](./apex_enum_RevSalesTrxn_TaxPreferenceEnum.htm.md "Specifies whether to execute or skip the tax calculation step for each sales transaction record. Available in API version 65.0 and later.")
:   Tax preference during the sales transaction process. Available in API version 65.0 and later.

persistPreferenceEnum
:   Type: [revsalestrxn.persistPreferenceEnum](./apex_enum_RevSalesTrxn_PersistPreferenceEnum.htm.md "Specifies whether to persist pricing changes for each sales transaction record. Available in API version 65.0 and later.")
:   Persist preference during the sales transaction process. Available in API version 65.0 and later.

groupRampActionEnum
:   Type: [revsalestrxn.GroupRampActionEnum](./apex_enum_RevSalesTrxn_GroupRampActionEnum.htm.md "Specifies the action ‌that you want to perform on group ramp segments. Additionally, you can also convert a non-ramped group into a ramped group.")
:   Specifies the action that you want to perform on group ramp segments.

#### Return Value

Type: [revsalestrxn.PlaceSalesTransactionResponse](./apex_class_RevSalesTrxn_PlaceSalesTransactionResponse.htm.md#apex_class_RevSalesTrxn_PlaceSalesTransactionResponse "Contains properties to hold the response to the place sales transaction request.")

## PlaceSalesTransactionExecutor Example Implementation

To place a sales transaction from Apex, refer to the example implementation of the
`PlaceSalesTransactionExecutor` class.

### Namespace

[RevSalesTrxn](./apex_namespace_RevSalesTrxn.htm.md "Create a sales transaction, such as a quote or an order, with integrated pricing and configuration. Additionally, update an order or a quote, and insert and delete order or quote line items to calculate the estimated tax.")

### Usage

Customize this example to suit your requirements. Create the list of records to be
ingested by using these steps. Replace the respective IDs with the values that are
present in your org. For example, replace the value of `${Pricebook2Id}` field with the price book ID that’s present in the
org.

### Example

This example shows a sample request to create a sales transaction, update a quote with a quote
line item, delete a quote line item, or skip or persist pricing changes. It includes
these steps.

- Set up a quote and quote line item.
- To create a quote line relationship, create an instance of the `RecordResource` class. To create an object with
  its fields, specify the object that you want to create by using POST method.
  Create a map of the fields and its values by using put(key, value) operation.
  Assign this field map to the record object.
- To update an object's specific fields, specify the object you want to update by
  using the PATCH method along with the ID of the object. Create a map of the
  fields and its values by using put(key, value) operation. Only certain fields on
  an object can be updated. Add the fields that you want to update to the map.
  Assign this field map to the record object.
- To associate the Record object with a reference identifier, create an instance
  of the `RecordWithReferenceRequest` class.
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
