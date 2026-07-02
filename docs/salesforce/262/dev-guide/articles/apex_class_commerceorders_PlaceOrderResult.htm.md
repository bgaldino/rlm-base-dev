---
page_id: apex_class_commerceorders_PlaceOrderResult.htm
title: PlaceOrderResult Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commerceorders_PlaceOrderResult.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commerceorders.htm
fetched_at: 2026-06-09
---

# PlaceOrderResult Class

Contains properties to hold the response to the place order request.

## Namespace

[CommerceOrders](./apex_namespace_commerceorders.htm.md "The CommerceOrders namespace provides classes and methods to place orders with integrated pricing, configuration, and validation.")

## Example

```
CommerceOrders.PlaceOrderResult resp = CommerceOrders.PlaceOrderExecutor.execute(graph,internalEnum,cEnum,cInput,catalogRatesPreference);
```

- **[PlaceOrderResult Properties](./apex_class_commerceorders_PlaceOrderResult.htm.md#apex_commerceorders_PlaceOrderResult_properties)**  
  Learn more about the available properties with the `PlaceOrderResult` class.

## PlaceOrderResult Properties

Learn more about the available properties with the `PlaceOrderResult` class.

The `PlaceOrderResult` class includes these
properties.

- **[orderId](./apex_class_commerceorders_PlaceOrderResult.htm.md#apex_commerceorders_PlaceOrderResult_orderId)**  
  Get the ID of the order that’s created after a successful request.
- **[requestIdentifier](./apex_class_commerceorders_PlaceOrderResult.htm.md#apex_commerceorders_PlaceOrderResult_requestIdentifier)**  
  Get the request ID of the process to query the asynchronous status of the Place Order Apex API.
- **[responseError](./apex_class_commerceorders_PlaceOrderResult.htm.md#apex_commerceorders_PlaceOrderResult_responseError)**  
  Get the list of errors encountered during the synchronous processing of the API request.
- **[statusURL](./apex_class_commerceorders_PlaceOrderResult.htm.md#apex_commerceorders_PlaceOrderResult_statusURL)**  
  Get the asynchronous status URL of the request, if available.
- **[success](./apex_class_commerceorders_PlaceOrderResult.htm.md#apex_commerceorders_PlaceOrderResult_success)**  
  Get the request status of the synchronous part of the processing.

### orderId

Get the ID of the order that’s created after a successful request.

#### Signature

`public String orderId {get; set;}`

#### Property Value

Type: String

### requestIdentifier

Get the request ID of the process to query the asynchronous status of the Place Order
Apex API.

#### Signature

`public String requestIdentifier {get; set;}`

#### Property Value

Type: String

### responseError

Get the list of errors encountered during the synchronous processing of the API
request.

#### Signature

`public List<commerceorders.PlaceOrderErrorResponse> responseError {get; set;}`

#### Property Value

Type: List<ConnectApi.PlaceOrderErrorResponse>

### statusURL

Get the asynchronous status URL of the request, if available.

#### Signature

`public String statusURL {get; set;}`

#### Property Value

Type: String

### success

Get the request status of the synchronous part of the processing.

#### Signature

`public Boolean success {get; set;}`

#### Property Value

Type: Boolean

Indicates whether the synchronous part
of the processing is successful (`true`) or not (`false`).
