---
page_id: clm_flow_metadata_api.htm
title: Flow for Salesforce Contracts
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/clm_flow_metadata_api.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_metadata_api_parent.htm
fetched_at: 2026-10-13
---

# Flow for Salesforce Contracts

Represents the metadata associated with a flow. With Flow, you can create an application that navigates users through a series of screens to query and update records in the database. You can also execute logic and provide branching capability based on user input to build dynamic applications.

    

## FlowActionCall

      
      

Salesforce Contracts exposes additional actionType values for the FlowActionCall Metadata type.

      

          
          
          
          
            
              

              

              

            

          

          
            
              

              

              

            

          

        
| Field Name | Field Type | Description |
| --- | --- | --- |
| actionType | InvocableActionType (enumeration of type string) | Required. The action type. Additional valid values only for Salesforce Contracts includes `searchContractDocument`—Search the latest contract document version based on the user's query. |
