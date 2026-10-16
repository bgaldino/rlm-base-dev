---
page_id: apex_commercetax_TaxEngineAdapter_processRequest.htm
title: processRequest(requestType)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_commercetax_TaxEngineAdapter_processRequest.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: apex_commercetax_TaxEngineAdapter_methods.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# processRequest(requestType)

The `processRequest` method takes
      an instance of `TaxEngineContext` class and returns a
      response with the calculated tax details through the `TaxDetailsResponse` class or an error response through the `ErrorResponse` class.

    

## Signature

`global commercetax.TaxEngineResponse
          processRequest(commercetax.TaxEngineContext var1)`

    

## Parameters

        
- 
**var1**:

Type: [TaxEngineContext](./apex_class_commercetax_TaxEngineContext.htm.md#apex_class_commercetax_TaxEngineContext)

Wrapper class that stores information about

the type of a tax calculation
            request.

      

    

## Return Value

Type:
        TaxEngineResponse

Generic interface representing a response from a tax engine.
