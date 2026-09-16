---
page_id: usage_management_flow_metadata_api.htm
title: Flow for Usage Management
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/usage_management_flow_metadata_api.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_metadata_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Flow for Usage Management

Represents the metadata associated with a flow. With Flow, you can create an
    application that navigates users through a series of screens to query and update records in the
    database. You can also execute logic and provide branching capability based on user input to
    build dynamic applications.

    

## FlowActionCall

      
      

Usage Management exposes additional actionType values for the FlowActionCall Metadata
        type.

      

          
          
          
          
            
              

              

              

            

          

          
            
              

              

              

- 
- 
- 
- 

            

          

        
| Field Name | Field Type | Description |
| --- | --- | --- |
| actionType | InvocableActionType (enumeration of type string) | Required. The action type. Additional valid values only for Usage Management include: `invokeSummaryCreationService`—Invoke the service that creates various summaries, such as usage, ratable, and liable summaries where the usage amount is zero. The service also checks and updates the billing period of the usage entitlement account if the billing period is expired. `processConsumptionOverages`—Process consumption overages for the usage summary records with `SummaryComplete` status. This action uses the entitlement service to process the overages. `refreshUsageEntitlementBucket`—Refresh entitlements by evaluating the usage entitlement bucket records and creating a new usage entitlement entry. `retriggerEntlCreaProc`—Retrigger entitlement creation process for failed or unprocessed assets. |
