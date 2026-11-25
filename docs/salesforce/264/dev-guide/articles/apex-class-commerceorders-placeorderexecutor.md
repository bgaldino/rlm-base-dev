---
page_id: apex-class-commerceorders-placeorderexecutor
title: PlaceOrderExecutor Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-commerceorders-placeorderexecutor.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-commerceorders
legacy_page_id: apex_class_commerceorders_PlaceOrderExecutor.htm
fetched_at: 2026-11-25
---

# PlaceOrderExecutor Class

Contains methods to place an order with details of the graph request, pricing preferences, and configuration options.

## Namespace

[CommerceOrders](./apex-namespace-commerceorders.md)

## Example

```
CommerceOrders.PlaceOrderResult resp = CommerceOrders.PlaceOrderExecutor.execute(graph,internalEnum,cEnum,cInput,catalogRatesPreference);
```

- 

**[PlaceOrderExecutor Methods](#placeorderexecutor-methods)**

Learn more about the methods available with the `PlaceOrderExecutor` class.

- 

**[PlaceOrderExecutor Example Implementation](#placeorderexecutor-example-implementation)**

Place orders with integrated pricing, configuration, and validation, and manage them throughout their entire lifecycle. To place an order from Apex, refer to the example implementation of the `PlaceOrderExecutor` class.

## PlaceOrderExecutor Methods

Learn more about the methods available with the `PlaceOrderExecutor` class.

The `PlaceOrderExecutor` class includes these methods.

- 

**[execute(graphRequest, pricingPreferenceEnum, configurationInputEnum, configurationOptionsInput)](#executegraphrequest-pricingpreferenceenum-configurationinputenum-configurationoptionsinput)**

Use the method in the `PlaceOrderExecutor` class to execute the Place Order Apex API request by assigning the properties for graph request, pricing reference, and configuration options.

- 

**[execute(graphRequest, pricingPreferenceEnum, catalogRatesPreference, configurationInputEnum, configurationOptionsInput)](#executegraphrequest-pricingpreferenceenum-catalogratespreference-configurationinputenum-configurationoptionsinput)**

Use the method in the `PlaceOrderExecutor` class to execute the Place Order Apex API request by assigning the properties for graph request, pricing reference, and configuration options. This method also includes the property to define fetching of rate card entries.

- 

**[execute(graphRequest)](#executegraphrequest)**

Use the method in the `PlaceOrderExecutor` class to execute the Place Order Apex API request by assigning the properties for graph request.

### execute(graphRequest, pricingPreferenceEnum, configurationInputEnum, configurationOptionsInput)

Use the method in the `PlaceOrderExecutor` class to execute the Place Order Apex API request by assigning the properties for graph request, pricing reference, and configuration options.

#### Signature

`public static commerceorders.PlaceOrderResult execute(commerceorders.GraphRequest graphRequest, commerceorders.PricingPreferenceEnum pricingPreferenceEnum, commerceorders.ConfigurationInputEnum configurationInputEnum, commerceorders.ConfigurationOptionsInput configurationOptionsInput)`

#### Parameters

***graphRequest***

Type: [commerceorders.GraphRequest](./apex-class-commerceorders-graphrequest.md#graphrequest-class)

The sObject graph values of the order payload to be ingested.

***pricingPreferenceEnum***

Type: [commerceorders.PricingPreferenceEnum](./apex-enum-commerceorders-pricingpreferenceenum.md)

Pricing preference during the order process.

***configurationInputEnum***

Type: [commerceorders.ConfigurationInputEnum](./apex-enum-commerceorders-configurationinputenum.md)

Configuration input for the place order process.

***configurationOptionsInput***

Type: [commerceorders.ConfigurationOptionsInput](./apex-class-commerceorders-configurationoptionsinput.md#configurationoptionsinput-class)

Configuration options during the ingestion process.

#### Return Value

Type: [commerceorders.PlaceOrderResult](./apex-class-commerceorders-placeorderresult.md#placeorderresult-class)

### execute(graphRequest, pricingPreferenceEnum, catalogRatesPreference, configurationInputEnum, configurationOptionsInput)

Use the method in the `PlaceOrderExecutor` class to execute the Place Order Apex API request by assigning the properties for graph request, pricing reference, and configuration options. This method also includes the property to define fetching of rate card entries.

#### Signature

`public static commerceorders.PlaceOrderResult execute(commerceorders.GraphRequest graphRequest, commerceorders.PricingPreferenceEnum pricingPreferenceEnum, commerceorders.CatalogRatesPreferenceEnum catalogRatesPreferenceEnum, commerceorders.ConfigurationInputEnum configurationInputEnum, commerceorders.ConfigurationOptionsInput configurationOptionsInput)`

#### Parameters

***graphRequest***

Type: [commerceorders.GraphRequest](./apex-class-commerceorders-graphrequest.md#graphrequest-class)

The sObject graph values of the order payload to be ingested.

***pricingPreferenceEnum***

Type: [commerceorders.PricingPreferenceEnum](./apex-enum-commerceorders-pricingpreferenceenum.md)

Pricing preference during the order process.

***catalogRatesPreference***

Type: [commerceorders.CatalogRatesPreferenceEnum](./apex-enum-commerceorders-catalogratespreferenceenum.md)

The rate card entries defined in the catalog that must be fetched for order items, with usage-based pricing during the order creation process. The `CatalogRatesPreferenceEnum` enum is available when the Usage-Based Selling feature is enabled.

***configurationInputEnum***

Type: [commerceorders.ConfigurationInputEnum](./apex-enum-commerceorders-configurationinputenum.md)

Configuration input for the place order process.

***configurationOptionsInput***

Type: [commerceorders.ConfigurationOptionsInput](./apex-class-commerceorders-configurationoptionsinput.md#configurationoptionsinput-class)

Configuration options during the ingestion process.

#### Return Value

Type: [commerceorders.PlaceOrderResult](./apex-class-commerceorders-placeorderresult.md#placeorderresult-class)

### execute(graphRequest)

Use the method in the `PlaceOrderExecutor` class to execute the Place Order Apex API request by assigning the properties for graph request.

#### Signature

`public static commerceorders.PlaceOrderResult execute(commerceorders.GraphRequest graphRequest)`

#### Parameters

***graphRequest***

Type: [commerceorders.GraphRequest](./apex-class-commerceorders-graphrequest.md#graphrequest-class)

The sObject graph values of the order payload to be ingested.

#### Return Value

Type: [commerceorders.PlaceOrderResult](./apex-class-commerceorders-placeorderresult.md#placeorderresult-class)

## PlaceOrderExecutor Example Implementation

Place orders with integrated pricing, configuration, and validation, and manage them throughout their entire lifecycle. To place an order from Apex, refer to the example implementation of the `PlaceOrderExecutor` class.

### Namespace

[commerceorders](./apex-namespace-commerceorders.md)

### Usage

Customize this example to suit your requirements. Create the list of records to be ingested by using these steps. Replace the respective IDs with the values that are present in your org. For example, replace the value of `${Pricebook2Id}` field with the price book ID that’s present in the org.

### Example

- 

Create the list of records by constructing the `Map<String, Object>` map of field values of an order.

```
List<CommerceOrders.RecordWithReferenceRequest> recordNodes = new List<CommerceOrders.RecordWithReferenceRequest>();
    
// Prepare for the Order 
Map<String,Object> orderFieldValues = new Map<String,Object>();
orderFieldValues.put('Pricebook2Id', '01sDU0000000lEIYAY');
orderFieldValues.put('AccountId', '001DU000001nIPKYA2');
orderFieldValues.put('EffectiveDate', '2024-01-01');
```

- 

To create a record object from the field values, create an instance of the `RecordResource` class.

```
CommerceOrders.RecordResource orderRecord = new CommerceOrders.RecordResource(Order.getSobjectType(), 'POST');
orderRecord.fieldValues = orderFieldValues;
```

- 

To associate the Record object with a reference identifier, create an instance of the `RecordWithReferenceRequest` class.

```
CommerceOrders.RecordWithReferenceRequest orderRecordNode = new CommerceOrders.RecordWithReferenceRequest('refOrder', orderRecord);
recordNodes.add(orderRecordNode);

// Prepare for the App Usage Assignment
Map<String,Object> auaFieldValues = new Map<String,Object>();
auaFieldValues.put('AppUsageType', 'RevenueLifecycleManagement');
auaFieldValues.put('RecordId', '@{refOrder.id}');

CommerceOrders.RecordResource auaRecord = new CommerceOrders.RecordResource(AppUsageAssignment.getSobjectType(), 'POST');
auaRecord.fieldValues = auaFieldValues;

CommerceOrders.RecordWithReferenceRequest auaRecordNode = new CommerceOrders.RecordWithReferenceRequest('refAppTag', auaRecord);
recordNodes.add(auaRecordNode);

// Prepare for the Order Item
Map<String,Object> oiFieldValues = new Map<String,Object>();
oiFieldValues.put('OrderId', '@{refOrder.id}');
oiFieldValues.put('PricebookEntryId', '01uDU000000YPkIYAW');
oiFieldValues.put('Product2Id', '01tDU000000ESCSYA4');
oiFieldValues.put('Quantity', 2);
oiFieldValues.put('UnitPrice', 800);

CommerceOrders.RecordResource oiRecord = new CommerceOrders.RecordResource(OrderItem.getSobjectType(), 'POST');
oiRecord.fieldValues = oiFieldValues;

CommerceOrders.RecordWithReferenceRequest oiRecordNode = new CommerceOrders.RecordWithReferenceRequest('refOrderItem', oiRecord);
recordNodes.add(oiRecordNode);
```

- 

Invoke the Place Order Apex API.

**Note:**

The `CatalogRatesPreferenceEnum` enum is available when the Usage-Based Selling feature is enabled.

```
// Invoke the Place Order Apex API
CommerceOrders.PricingPreferenceEnum pricingPreference = CommerceOrders.PricingPreferenceEnum.System;
CommerceOrders.CatalogRatesPreferenceEnum catalogRatesPreference = CommerceOrders.CatalogRatesPreferenceEnum.Fetch;
CommerceOrders.ConfigurationInputEnum configurationPreference = CommerceOrders.ConfigurationInputEnum.RunAndAllowErrors;
CommerceOrders.ConfigurationOptionsInput configurationInput = new CommerceOrders.ConfigurationOptionsInput();
configurationInput.validateProductCatalog = true;
configurationInput.validateAmendRenewCancel = true;
configurationInput.executeConfigurationRules = true;
configurationInput.addDefaultConfiguration = true;
```

- 

To contain all record objects, create an instance of the `GraphRequest` class.

```
CommerceOrders.GraphRequest graph = new CommerceOrders.GraphRequest('testGraph', recordNodes);
CommerceOrders.PlaceOrderResult result = CommerceOrders.PlaceOrderExecutor.execute(graph, pricingPreference, catalogRatesPreference, configurationPreference, configurationInput);

// Process any error, if exists
if (!result.success) {
  List<ConnectApi.PlaceOrderErrorResponse> errors = result.responseError;
  for (ConnectApi.PlaceOrderErrorResponse error : errors) {
    System.debug(error.errorCode + ': ' + error.message);
  }
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-commerceorders-placeorderexecutor.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
