---
page_id: connect_resources_data_true_up_resources.htm
title: Data True-Up Resources
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_data_true_up_resources.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_resources.htm
fetched_at: 2026-10-13
---

# Data
      True-Up Resources

Keep contract documents and Salesforce records perfectly aligned by synchronizing
      token values between them. From the Microsoft 365 add-in, you can pull the latest data from
      Salesforce into the document or push the document changes back to the Salesforce record. This
      simple, two-way process ensures that your information is always consistent across both
      locations, preventing data mismatches.

      
         

The available resource is:

         

               
               
               
                  
                     

                     

                  

               

               
                  
                     

                     

                  

                  
                     

                     

                  

               

            
| Resource | Description |
| --- | --- |
| [`/connect/content-link/load`](./connect_resources_contentlink_load.htm.md) | Fetches the content data for a specified reference ID or set of content link IDs. |
| [`/connect/content-link/data-sync`](./connect_resources_contentlink_data_sync.htm.md) (POST) | Synchronize and save the updated values for a specified reference ID and a set of content link IDs. |

      

   

- 
**[Content Link Load (POST)](./connect_resources_contentlink_load.htm.md)**  

Fetches the content data for a specified reference ID or set of       content link IDs.

- 
**[Data Sync (POST)](./connect_resources_contentlink_data_sync.htm.md)**  

Synchronize and save the updated values for a specified reference ID       and a set of content link IDs.
