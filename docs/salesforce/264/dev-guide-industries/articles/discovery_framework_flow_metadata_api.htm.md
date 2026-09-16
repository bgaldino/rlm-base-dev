---
page_id: discovery_framework_flow_metadata_api.htm
title: Flow for Discovery Framework
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/discovery_framework_flow_metadata_api.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_metadata_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Flow for Discovery Framework

Represents the metadata associated with a flow. With Flow, you can create an
    application that navigates users through a series of screens to query and update records in the
    database. You can also execute logic and provide branching capability based on user input to
    build dynamic applications.

    

## FlowActionCall

      
      

Discovery Framework exposes additional actionType values for the FlowActionCall Metadata
        type. For more information on Flow and FlowActionCall metadata types, see [Flow](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/meta_visual_workflow.htm).

      

          
          
          
          
            
              

              

              

            

          

          
            
              

              

              
- 

            

          

        
| Field Name | Field Type | Description |
| --- | --- | --- |
| actionType | InvocableActionType (enumeration of type string) | Required. The action type. Additional valid values only for Discovery Framework include: `getAssessmentResponseSummary`—Invoke the Get Assessment Response Summary action. This value is available in API version 57.0 and later. |
