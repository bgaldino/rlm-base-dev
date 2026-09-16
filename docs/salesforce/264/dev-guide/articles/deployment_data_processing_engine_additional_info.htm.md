---
page_id: deployment_data_processing_engine_additional_info.htm
title: Data Processing Engine Additional Information
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_data_processing_engine_additional_info.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Management Deployment
parent_page: deployment_appendix_C.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Data Processing Engine Additional Information

Get to know additional deployment information for Data Processing Engine in Revenue
    Cloud.

    

## Deployment Considerations

      
      
        
- Data Processing Engine objects have `Draft` and
            `Active` states.

        
- The objects must be created in `Draft` state and
          activated later. The activation is done through API.

        
- Configuration can’t be changed after an object is updated to `Active` state.

        
- Set the state of the object to `Inactive` for any
          modifications, and then set the state to `Active`.

      

    

    

## Other Information

      
      
        
- Data Processing Engine has dependencies on these components.
            
  - CRM Analytics or Data Cloud

            
  - Bulk API

          

        
- You can deploy Data Processing Engine definitions from one organization to another. Both
          organizations must be on the same Salesforce release version.
