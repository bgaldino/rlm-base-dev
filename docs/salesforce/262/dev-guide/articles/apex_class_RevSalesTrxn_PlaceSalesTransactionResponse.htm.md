---
page_id: apex_class_RevSalesTrxn_PlaceSalesTransactionResponse.htm
title: PlaceSalesTransactionResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_RevSalesTrxn_PlaceSalesTransactionResponse.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_RevSalesTrxn.htm
fetched_at: 2026-06-09
---

# PlaceSalesTransactionResponse Class

Contains properties to hold the response to the place sales transaction
request.

## Namespace

[RevSalesTrxn](./apex_namespace_RevSalesTrxn.htm.md "Create a sales transaction, such as a quote or an order, with integrated pricing and configuration. Additionally, update an order or a quote, and insert and delete order or quote line items to calculate the estimated tax.")

## Example

```
RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(graph, pricingPrefEnum, configurationExecutionEnum, new RevSalesTrxn.ConfigurationOptionsInput(), null);
```

- **[PlaceSalesTransactionResponse Properties](./apex_class_RevSalesTrxn_PlaceSalesTransactionResponse.htm.md#apex_RevSalesTrxn_PlaceSalesTransactionResponse_properties)**  
  Learn more about the available properties with the PlaceSalesTransactionResponse class.

## PlaceSalesTransactionResponse Properties

Learn more about the available properties with the PlaceSalesTransactionResponse
class.

The `PlaceSalesTransactionResponse` class includes these
properties.

- **[contextDetails](./apex_class_RevSalesTrxn_PlaceSalesTransactionResponse.htm.md#apex_RevSalesTrxn_PlaceSalesTransactionResponse_contextDetails)**  
  Get the details of the context that’s created for the sales transaction.
- **[errorResponse](./apex_class_RevSalesTrxn_PlaceSalesTransactionResponse.htm.md#apex_RevSalesTrxn_PlaceSalesTransactionResponse_errorResponse)**  
  Get the list of errors encountered during the synchronous processing of the API request.
- **[isSuccess](./apex_class_RevSalesTrxn_PlaceSalesTransactionResponse.htm.md#apex_RevSalesTrxn_PlaceSalesTransactionResponse_isSuccess)**  
  Get the request status of the synchronous part of the processing.
- **[salesTransactionId](./apex_class_RevSalesTrxn_PlaceSalesTransactionResponse.htm.md#apex_RevSalesTrxn_PlaceSalesTransactionResponse_salesTransactionId)**  
  Get the ID of the sales transaction, such as a quote or an order.
- **[statusUrl](./apex_class_RevSalesTrxn_PlaceSalesTransactionResponse.htm.md#apex_RevSalesTrxn_PlaceSalesTransactionResponse_statusUrl)**  
  Get the asynchronous status URL of the request, if available.
- **[trackerId](./apex_class_RevSalesTrxn_PlaceSalesTransactionResponse.htm.md#apex_RevSalesTrxn_PlaceSalesTransactionResponse_trackerId)**  
  Get the unique identifier assigned to a specific operation or request that's used for tracking and referencing the operation.

### contextDetails

Get the details of the context that’s created for the sales transaction.

#### Signature

`public ConnectApi.ContextDetails contextDetails {get; set;}`

#### Property Value

Type: ConnectApi.ContextDetails

### errorResponse

Get the list of errors encountered during the synchronous processing of the API
request.

#### Signature

`public List<ConnectApi.PlaceSalesTransactionErrorResponse> errorResponse {get; set;}`

#### Property Value

Type: List<ConnectApi.PlaceSalesTransactionErrorResponse>

### isSuccess

Get the request status of the synchronous part of the processing.

#### Signature

`public Boolean isSuccess {get; set;}`

#### Property Value

Type: Boolean

Indicates whether the synchronous part of the processing is successful
(`true`) or not (`false`).

### salesTransactionId

Get the ID of the sales transaction, such as a quote or an order.

#### Signature

`public String salesTransactionId {get; set;}`

#### Property Value

Type: String

### statusUrl

Get the asynchronous status URL of the request, if available.

#### Signature

`public String statusUrl {get; set;}`

#### Property Value

Type: String

### trackerId

Get the unique identifier assigned to a specific operation or request that's used for
tracking and referencing the operation.

#### Signature

`public String trackerId {get; set;}`

#### Property Value

Type: String
