---
page_id: apex_class_placequote_PlaceQuoteResponse.htm
title: PlaceQuoteResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_placequote_PlaceQuoteResponse.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_placequote.htm
fetched_at: 2026-06-09
---

# PlaceQuoteResponse Class

Contains properties to hold the response to the place quote request.

## Namespace

[PlaceQuote](./apex_namespace_placequote.htm.md "The PlaceQuote namespace provides classes and methods to create or update quotes with pricing preferences and configuration options.")

## Example

```
PlaceQuote.PlaceQuoteResponse resp = PlaceQuote.PlaceQuoteExecutor.execute(internalEnum,graph);
```

- **[PlaceQuoteResponse Properties](./apex_class_placequote_PlaceQuoteResponse.htm.md#apex_placequote_PlaceQuoteResponse_properties)**  
  Learn more about the available properties with the `PlaceQuoteResponse` class.

## PlaceQuoteResponse Properties

Learn more about the available properties with the `PlaceQuoteResponse` class.

The `PlaceQuoteResponse` class includes these
properties.

- **[quoteId](./apex_class_placequote_PlaceQuoteResponse.htm.md#apex_placequote_PlaceQuoteResponse_quoteId)**  
  Get the ID of the quote that’s created after a successful request.
- **[requestIdentifier](./apex_class_placequote_PlaceQuoteResponse.htm.md#apex_placequote_PlaceQuoteResponse_requestIdentifier)**  
  Get the request ID of the process to query the asynchronous status of the Place Quote Apex API.
- **[responseError](./apex_class_placequote_PlaceQuoteResponse.htm.md#apex_placequote_PlaceQuoteResponse_responseError)**  
  Get the list of errors encountered during the synchronous processing of the API request.
- **[statusURL](./apex_class_placequote_PlaceQuoteResponse.htm.md#apex_placequote_PlaceQuoteResponse_statusURL)**  
  Get the asynchronous status URL of the request, if available.
- **[success](./apex_class_placequote_PlaceQuoteResponse.htm.md#apex_placequote_PlaceQuoteResponse_success)**  
  Get the request status of the synchronous part of the processing.

### quoteId

Get the ID of the quote that’s created after a successful request.

#### Signature

`public String quoteId {get; set;}`

#### Property Value

Type: String

### requestIdentifier

Get the request ID of the process to query the asynchronous status of the Place Quote
Apex API.

#### Signature

`public String requestIdentifier {get; set;}`

#### Property Value

Type: String

### responseError

Get the list of errors encountered during the synchronous processing of the API
request.

#### Signature

`public List<ConnectApi.PlaceQuoteErrorResponse> responseError {get; set;}`

#### Property Value

Type: List<ConnectApi.PlaceQuoteErrorResponse>

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
