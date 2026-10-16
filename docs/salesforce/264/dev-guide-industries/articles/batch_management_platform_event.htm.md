---
page_id: batch_management_platform_event.htm
title: Common Platform Event
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/batch_management_platform_event.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Common Platform Event

Batch Management jobs and Data Processing Engine definitions are run using invocable
   actions in Flows. Use the BatchJobStatusChanged event to notify subscribers after a Batch
   Management job or a Data Processing Engine definition is processed in a flow.

  

    
     
      

     

     
      

     

     
      

     

    

   
| Available in: Lightning Experience |
| --- |
| Available in: [View product and edition availability for Data Processing Engine.](https://help.salesforce.com/s/articleView?id=ind.dpe_editions.htm&language=en_US) |
| Available in: [View product and edition availability for Batch Management.](https://help.salesforce.com/s/articleView?id=ind.concept_batch_management_editions.htm&language=en_US) |

  

 

- 
**[BatchJobStatusChangedEvent](./sforce_api_objects_batchjobstatuschangedevent.htm.md)**  

Notifies subscribers of when a batch job is completed in a 			flow. This object is available in API version 51.0 and later.
