---
page_id: apex-class-revsalestrxn-placesalestransactionresponse
title: PlaceSalesTransactionResponse Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-revsalestrxn-placesalestransactionresponse.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-revsalestrxn
legacy_page_id: apex_class_RevSalesTrxn_PlaceSalesTransactionResponse.htm
fetched_at: 2026-11-25
---

# PlaceSalesTransactionResponse Class

Contains properties to hold the response to the place sales transaction request.

## Namespace

[RevSalesTrxn](./apex-namespace-revsalestrxn.md)

## Example

```
RevSalesTrxn.PlaceSalesTransactionResponse resp = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(graph, pricingPrefEnum, configurationExecutionEnum, new RevSalesTrxn.ConfigurationOptionsInput(), null);
```

- 

**[PlaceSalesTransactionResponse Properties](#placesalestransactionresponse-properties)**

Learn more about the available properties with the PlaceSalesTransactionResponse class.

## PlaceSalesTransactionResponse Properties

Learn more about the available properties with the PlaceSalesTransactionResponse class.

The `PlaceSalesTransactionResponse` class includes these properties.

- 

**[contextDetails](#contextdetails)**

Get the details of the context that’s created for the sales transaction.

- 

**[errorResponse](#errorresponse)**

Get the list of errors encountered during the synchronous processing of the API request.

- 

**[isSuccess](#issuccess)**

Get the request status of the synchronous part of the processing.

- 

**[salesTransactionId](#salestransactionid)**

Get the ID of the sales transaction, such as a quote or an order.

- 

**[statusUrl](#statusurl)**

Get the asynchronous status URL of the request, if available.

- 

**[trackerId](#trackerid)**

Get the unique identifier assigned to a specific operation or request that’s used for tracking and referencing the operation.

### contextDetails

Get the details of the context that’s created for the sales transaction.

#### Signature

`public ConnectApi.ContextDetails contextDetails {get; set;}`

#### Property Value

Type: ConnectApi.ContextDetails

### errorResponse

Get the list of errors encountered during the synchronous processing of the API request.

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

Indicates whether the synchronous part of the processing is successful (`true`) or not (`false`).

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

Get the unique identifier assigned to a specific operation or request that’s used for tracking and referencing the operation.

#### Signature

`public String trackerId {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-revsalestrxn-placesalestransactionresponse.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
