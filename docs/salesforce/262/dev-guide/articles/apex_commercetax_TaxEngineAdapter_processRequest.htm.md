---
page_id: apex_commercetax_TaxEngineAdapter_processRequest.htm
title: processRequest(requestType)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_commercetax_TaxEngineAdapter_processRequest.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: apex_commercetax_TaxEngineAdapter_methods.htm
fetched_at: 2026-06-09
---

# processRequest(requestType)

The `processRequest` method takes
an instance of `TaxEngineContext` class and returns a
response with the calculated tax details through the `TaxDetailsResponse` class or an error response through the `ErrorResponse` class.

## Signature

`global commercetax.TaxEngineResponse
processRequest(commercetax.TaxEngineContext var1)`

## Parameters

var1
:   Type: [TaxEngineContext](./apex_class_commercetax_TaxEngineContext.htm.md#apex_class_commercetax_TaxEngineContext "Wrapper class that stores details about the type of a tax calculation request.")
:   Wrapper class that stores information about the type of a tax calculation
    request.

## Return Value

Type:
TaxEngineResponse

Generic interface representing a response from a tax engine.
