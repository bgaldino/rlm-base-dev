---
page_id: apex_class_commerceorders_GraphRequest.htm
title: GraphRequest Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commerceorders_GraphRequest.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commerceorders.htm
fetched_at: 2026-06-09
---

# GraphRequest Class

Contains constructors and properties to set the graph ID and a list of records to be
ingested. The list of records is specified in a key-value map format that contains the field
values of an order.

## Namespace

[CommerceOrders](./apex_namespace_commerceorders.htm.md "The CommerceOrders namespace provides classes and methods to place orders with integrated pricing, configuration, and validation.")

## Example

Create the list of records to be ingested by using these steps.

- Create the list of records by constructing the `Map<String, Object>` map of field values of an
  order.

  ```
  List<CommerceOrders.RecordWithReferenceRequest> recordNodes = new List<CommerceOrders.RecordWithReferenceRequest>();
      
  // Prepare for the Order 
  Map<String,Object> orderFieldValues = new Map<String,Object>();
  orderFieldValues.put('Pricebook2Id', '01sDU0000000lEIYAY');
  orderFieldValues.put('AccountId', '001DU000001nIPKYA2');
  orderFieldValues.put('EffectiveDate', '2024-01-01');
  ```
- To create a record object from the field values, create an instance of the `RecordResource`
  class.

  ```
  CommerceOrders.RecordResource orderRecord = new CommerceOrders.RecordResource(Order.getSobjectType(), 'POST');
  orderRecord.fieldValues = orderFieldValues;
  ```
- To associate the Record object with a reference identifier, create an instance of the
  `RecordWithReferenceRequest`
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

  The `CatalogRatesPreferenceEnum` enum is available when the Usage-Based Selling
  feature is enabled.

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
- To contain all record objects, create an instance of the `GraphRequest` class.

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

- **[GraphRequest Constructors](./apex_class_commerceorders_GraphRequest.htm.md#apex_commerceorders_GraphRequest_constructors)**  
  Learn more about the available constructors with the `GraphRequest` class.
- **[GraphRequest Properties](./apex_class_commerceorders_GraphRequest.htm.md#apex_commerceorders_GraphRequest_properties)**  
  Learn more about the available properties with the `GraphRequest` class.

## GraphRequest Constructors

Learn more about the available constructors with the `GraphRequest` class.

The `GraphRequest` class includes these constructors.

- **[GraphRequest(graphId, records)](./apex_class_commerceorders_GraphRequest.htm.md#apex_commerceorders_GraphRequest_ctor)**  
  Creates an instance of the `GraphRequest` class to assign the graph ID and a list of records to be ingested.

### GraphRequest(graphId, records)

Creates an instance of the `GraphRequest` class to
assign the graph ID and a list of records to be ingested.

#### Signature

`public GraphRequest(String graphId, List<commerceorders.RecordWithReferenceRequest> records)`

#### Parameters

graphId
:   Type: String
:   ID of the graph.

records
:   Type: List<[commerceorders.RecordWithReferenceRequest](./apex_class_commerceorders_RecordWithReferenceRequest.htm.md#apex_class_commerceorders_RecordWithReferenceRequest "Contains constructors and properties to associate a record object with a reference identifier.")>
:   List of records to be ingested.

## GraphRequest Properties

Learn more about the available properties with the `GraphRequest` class.

The `GraphRequest` class includes these properties.

- **[graphId](./apex_class_commerceorders_GraphRequest.htm.md#apex_commerceorders_GraphRequest_graphId)**  
  Set the `graphId` property to assign the ID value of the graph.

### graphId

Set the `graphId` property to assign the ID value of
the graph.

#### Signature

`public String graphId {get; set;}`

#### Property Value

Type: String
