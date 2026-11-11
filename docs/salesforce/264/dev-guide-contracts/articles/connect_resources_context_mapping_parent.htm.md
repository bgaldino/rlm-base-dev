---
page_id: connect_resources_context_mapping_parent.htm
title: Context Mapping Extraction Resources
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_context_mapping_parent.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_resources.htm
fetched_at: 2026-10-13
---

# Context Mapping Extraction Resources

Manage custom mappings used in the extraction flow of documents before their fields
      are sent for extraction. Use the Extraction Context Mapping resource to map extracted field
      values to their own set of custom fields relevant to their contract types and business
      cases.

      
         

Available resource is:

         

               
               
               
                  
                     

                     

                  

               

               
                  
                     

                     

                  

                  
                     

                     

                  

               

            
| Resource | Description |
| --- | --- |
| [`/connect/clm/extraction-context-mappings` (POST)](./connect_resources_extraction_context_mapping.htm.md) | Create extraction context-mapping details that show how extracted data is associated with Salesforce fields. |
| [`/connect/clm/extraction-context-mappings/${contextUseCaseMappingId}` (DELETE, GET, PATCH)](./connect_resources_extraction_context_mappings_get_delete_patch.htm.md) | Delete extraction context mapping details based on the specified context use case mapping ID. Get extraction context mapping details based on the specified context use case mapping ID. Update extraction context mapping details based on the specified context use case mapping ID. |

      

   

- 
**[Extraction Context Mapping (POST)](./connect_resources_extraction_context_mapping.htm.md)**  

Create extraction context-mapping details that show how extracted       data is associated with Salesforce fields.

- 
**[Extraction Context Mappings (DELETE, GET, PATCH)](./connect_resources_extraction_context_mappings_get_delete_patch.htm.md)**  

Delete extraction context mapping details based on the specified       context use case mapping ID. Get extraction context mapping details based on the specified       context use case mapping ID. Update extraction context mapping details based on the specified       context use case mapping ID.
