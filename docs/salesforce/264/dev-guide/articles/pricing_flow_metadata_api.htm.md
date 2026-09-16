---
page_id: pricing_flow_metadata_api.htm
title: Flow for Salesforce Pricing
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/pricing_flow_metadata_api.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_metadata_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Flow for Salesforce Pricing

Represents the metadata associated with a flow. With Flow, you can create an
    application that navigates users through a series of screens to query and update records in the
    database. You can also execute logic and provide branching capability based on user input to
    build dynamic applications.

    

## FlowActionCall

      
      

Salesforce Pricing exposes additional actionType values for the FlowActionCall Metadata
        type.

      

          
          
          
          
            
              

              

              

            

          

          
            
              

              

              

- 
- 

            

          

        
| Field Name | Field Type | Description |
| --- | --- | --- |
| actionType | InvocableActionType (enumeration of type string) | Required. The action type. Additional valid values only for Salesforce Pricing include: `runSalesforcePricing`—Invoke the Pricing Connect API by providing the context, pricing procedure, and price waterfall details. `runSalesforceHeadlessPricing`—Invoke the Pricing Connect API by providing the pricing data and details of a context, pricing procedure, and price waterfall. |
