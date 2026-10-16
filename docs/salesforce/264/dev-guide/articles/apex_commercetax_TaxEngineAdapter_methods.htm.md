---
page_id: apex_commercetax_TaxEngineAdapter_methods.htm
title: TaxEngineAdapter Methods
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_commercetax_TaxEngineAdapter_methods.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_tax_engine_adapter_interface_for_standard_tax.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# TaxEngineAdapter Methods

Learn more about the available methods with the `TaxEngineAdapter` class.

    
      

The `TaxEngineAdapter` class includes these
        methods.

    

    
  

- 
**[processRequest(requestType)](./apex_commercetax_TaxEngineAdapter_processRequest.htm.md)**  

The `processRequest` method takes       an instance of `TaxEngineContext` class and returns a       response with the calculated tax details through the `TaxDetailsResponse` class or an error response through the `ErrorResponse` class.
