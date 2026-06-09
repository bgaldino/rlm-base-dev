---
page_id: apex_class_commerceorders_PlaceOrderExecutor.htm
title: PlaceOrderExecutor Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commerceorders_PlaceOrderExecutor.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commerceorders.htm
fetched_at: 2026-06-09
---

# PlaceOrderExecutor Class

Contains methods to place an order with details of the graph request, pricing
preferences, and configuration options.

## Namespace

[CommerceOrders](./apex_namespace_commerceorders.htm.md "The CommerceOrders namespace provides classes and methods to place orders with integrated pricing, configuration, and validation.")

## Example

```
CommerceOrders.PlaceOrderResult resp = CommerceOrders.PlaceOrderExecutor.execute(graph,internalEnum,cEnum,cInput,catalogRatesPreference);
```

- **[PlaceOrderExecutor Methods](./apex_class_commerceorders_PlaceOrderExecutor.htm.md#apex_commerceorders_PlaceOrderExecutor_methods)**  
  Learn more about the methods available with the `PlaceOrderExecutor` class.
- **[PlaceOrderExecutor Example Implementation](./apex_class_commerceorders_PlaceOrderExecutor.htm.md#apex_commerceorders_PlaceOrderExecutor_example_implementation)**  
  Place orders with integrated pricing, configuration, and validation, and manage them throughout their entire lifecycle. To place an order from Apex, refer to the example implementation of the `PlaceOrderExecutor` class.

## PlaceOrderExecutor Methods

Learn more about the methods available with the `PlaceOrderExecutor` class.

The `PlaceOrderExecutor` class includes these methods.

- **[execute(graphRequest, pricingPreferenceEnum, configurationInputEnum, configurationOptionsInput)](./apex_class_commerceorders_PlaceOrderExecutor.htm.md#apex_commerceorders_PlaceOrderExecutor_execute_1)**  
  Use the method in the `PlaceOrderExecutor` class to execute the Place Order Apex API request by assigning the properties for graph request, pricing reference, and configuration options.
- **[execute(graphRequest, pricingPreferenceEnum, catalogRatesPreference, configurationInputEnum, configurationOptionsInput)](./apex_class_commerceorders_PlaceOrderExecutor.htm.md#apex_commerceorders_PlaceOrderExecutor_execute_3)**  
  Use the method in the `PlaceOrderExecutor` class to execute the Place Order Apex API request by assigning the properties for graph request, pricing reference, and configuration options. This method also includes the property to define fetching of rate card entries.
- **[execute(graphRequest)](./apex_class_commerceorders_PlaceOrderExecutor.htm.md#apex_commerceorders_PlaceOrderExecutor_execute_2)**  
  Use the method in the `PlaceOrderExecutor` class to execute the Place Order Apex API request by assigning the properties for graph request.

### execute(graphRequest, pricingPreferenceEnum, configurationInputEnum, configurationOptionsInput)

Use the method in the `PlaceOrderExecutor` class
to execute the Place Order Apex API request by assigning the properties for graph request,
pricing reference, and configuration options.

#### Signature

`public static commerceorders.PlaceOrderResult
execute(commerceorders.GraphRequest graphRequest, commerceorders.PricingPreferenceEnum
pricingPreferenceEnum, commerceorders.ConfigurationInputEnum configurationInputEnum,
commerceorders.ConfigurationOptionsInput configurationOptionsInput)`

#### Parameters

graphRequest
:   Type: [commerceorders.GraphRequest](./apex_class_commerceorders_GraphRequest.htm.md#apex_class_commerceorders_GraphRequest "Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains the field values of an order.")
:   The sObject graph values of the order payload to be ingested.

pricingPreferenceEnum
:   Type: [commerceorders.PricingPreferenceEnum](./apex_enum_commerceorders_PricingPreferenceEnum.htm.md "Specifies the pricing preference during the create order process.")
:   Pricing preference during the order process.

configurationInputEnum
:   Type: [commerceorders.ConfigurationInputEnum](./apex_enum_commerceorders_ConfigurationInputEnum.htm.md "Specifies the configuration input for the request to place an order.")
:   Configuration input for the place order process.

configurationOptionsInput
:   Type: [commerceorders.ConfigurationOptionsInput](./apex_class_commerceorders_ConfigurationOptionsInput.htm.md#apex_class_commerceorders_ConfigurationOptionsInput "Contains methods and properties to set the configuration options for the input to the product configurator.")
:   Configuration options during the ingestion process.

#### Return Value

Type: [commerceorders.PlaceOrderResult](./apex_class_commerceorders_PlaceOrderResult.htm.md#apex_class_commerceorders_PlaceOrderResult "Contains properties to hold the response to the place order request.")

### execute(graphRequest, pricingPreferenceEnum, catalogRatesPreference, configurationInputEnum, configurationOptionsInput)

Use the method in the `PlaceOrderExecutor` class
to execute the Place Order Apex API request by assigning the properties for graph request,
pricing reference, and configuration options. This method also includes the property to define
fetching of rate card entries.

#### Signature

`public static commerceorders.PlaceOrderResult
execute(commerceorders.GraphRequest graphRequest, commerceorders.PricingPreferenceEnum
pricingPreferenceEnum, commerceorders.CatalogRatesPreferenceEnum
catalogRatesPreferenceEnum, commerceorders.ConfigurationInputEnum configurationInputEnum,
commerceorders.ConfigurationOptionsInput configurationOptionsInput)`

#### Parameters

graphRequest
:   Type: [commerceorders.GraphRequest](./apex_class_commerceorders_GraphRequest.htm.md#apex_class_commerceorders_GraphRequest "Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains the field values of an order.")
:   The sObject graph values of the order payload to be ingested.

pricingPreferenceEnum
:   Type: [commerceorders.PricingPreferenceEnum](./apex_enum_commerceorders_PricingPreferenceEnum.htm.md "Specifies the pricing preference during the create order process.")
:   Pricing preference during the order process.

catalogRatesPreference
:   Type: [commerceorders.CatalogRatesPreferenceEnum](./apex_enum_commerceorders_CatalogRatesPreferenceEnum.htm.md "Specifies the rate card entries defined in the catalog that must be fetched for order items, with usage-based selling during the order creation process.")
:   The rate card entries defined in the catalog that must be fetched for order items,
    with usage-based pricing during the order creation process. The `CatalogRatesPreferenceEnum` enum is available when the
    Usage-Based Selling feature is enabled.

configurationInputEnum
:   Type: [commerceorders.ConfigurationInputEnum](./apex_enum_commerceorders_ConfigurationInputEnum.htm.md "Specifies the configuration input for the request to place an order.")
:   Configuration input for the place order process.

configurationOptionsInput
:   Type: [commerceorders.ConfigurationOptionsInput](./apex_class_commerceorders_ConfigurationOptionsInput.htm.md#apex_class_commerceorders_ConfigurationOptionsInput "Contains methods and properties to set the configuration options for the input to the product configurator.")
:   Configuration options during the ingestion process.

#### Return Value

Type: [commerceorders.PlaceOrderResult](./apex_class_commerceorders_PlaceOrderResult.htm.md#apex_class_commerceorders_PlaceOrderResult "Contains properties to hold the response to the place order request.")

### execute(graphRequest)

Use the method in the `PlaceOrderExecutor` class to
execute the Place Order Apex API request by assigning the properties for graph
request.

#### Signature

`public static commerceorders.PlaceOrderResult execute(commerceorders.GraphRequest graphRequest)`

#### Parameters

graphRequest
:   Type: [commerceorders.GraphRequest](./apex_class_commerceorders_GraphRequest.htm.md#apex_class_commerceorders_GraphRequest "Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains the field values of an order.")
:   The sObject graph values of the order payload to be ingested.

#### Return Value

Type: [commerceorders.PlaceOrderResult](./apex_class_commerceorders_PlaceOrderResult.htm.md#apex_class_commerceorders_PlaceOrderResult "Contains properties to hold the response to the place order request.")

## PlaceOrderExecutor Example Implementation

Place orders with integrated pricing, configuration, and validation, and manage them
throughout their entire lifecycle. To place an order from Apex, refer to the example
implementation of the `PlaceOrderExecutor`
class.

### Namespace

[commerceorders](./apex_namespace_commerceorders.htm.md "The CommerceOrders namespace provides classes and methods to place orders with integrated pricing, configuration, and validation.")

### Usage

Customize this example to suit your requirements. Create the list of records to be
ingested by using these steps. Replace the respective IDs with the values that are
present in your org. For example, replace the value of `${Pricebook2Id}` field with the price book ID that’s present in the
org.

### Example

- Create the list of records by constructing the `Map<String, Object>` map of field
  values of an
  order.

  ```
  List<CommerceOrders.RecordWithReferenceRequest> recordNodes = new List<CommerceOrders.RecordWithReferenceRequest>();
      
  // Prepare for the Order 
  Map<String,Object> orderFieldValues = new Map<String,Object>();
  orderFieldValues.put('Pricebook2Id', '01sDU0000000lEIYAY');
  orderFieldValues.put('AccountId', '001DU000001nIPKYA2');
  orderFieldValues.put('EffectiveDate', '2024-01-01');
  ```
- To create a record object from the field values, create an instance of the
  `RecordResource`
  class.

  ```
  CommerceOrders.RecordResource orderRecord = new CommerceOrders.RecordResource(Order.getSobjectType(), 'POST');
  orderRecord.fieldValues = orderFieldValues;
  ```
- To associate the Record object with a reference identifier, create an instance
  of the `RecordWithReferenceRequest`
  class.

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
- Invoke the Place Order Apex API.

  ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

  #### Note

  The `CatalogRatesPreferenceEnum` enum is available when the
  Usage-Based Selling feature is
  enabled.

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
- To contain all record objects, create an instance of the `GraphRequest`
  class.

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
