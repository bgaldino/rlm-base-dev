---
page_id: rate_management_flow_metadata_api.htm
title: Flow for Rate Management
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/rate_management_flow_metadata_api.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_metadata_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Flow for Rate Management

Represents the metadata associated with a flow. With Flow, you can create an
    application that takes users through a series of pages to query and update the records in the
    database. You can also run logic and provide branching capability based on user input to build
    dynamic applications.

    

## FlowActionCall

      
      

Rate Management exposes additional actionType values for the FlowActionCall metadata
        type.

      

          
          
          
          
            
              

              

              

            

          

          
            
              

              

              

- 

            

          

        
| Field Name | Field Type | Description |
| --- | --- | --- |
| actionType | InvocableActionType (enumeration of type string) | Required. The action type. Additional valid values for Rate Management include: `invokeRatingService`—Invoke the rating service to rate the usage records. |
