---
page_id: connect_resources_batch_job_cancel.htm
title: Batch Job Cancel
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_batch_job_cancel.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch_management_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Batch Job Cancel

Cancel a batch job of type data processing engine (calc job) and batch
      management. A batch job with only the status Submitted or In Progress can be
    canceled.

        
          

**Special Access Rules**

          
: To know the permissions needed to access this resource, See [User Permissions for Data Processing Engine](https://help.salesforce.com/s/articleView?id=ind.dpe_setup.htm&language=en_US) or [User Permissions for Batch Management](https://help.salesforce.com/s/articleView?id=ind.concept_batch_management_editions.htm&language=en_US).

        
        
          

**Resource**

          
: 
            

```
/connect/batch-job/batchJobId/cancel-job
```

          

        
        
          

**Resource example**

          
: 
            

```
/connect/batch-job/0mdxx00000000fxAAA/cancel-job
```

          

        
        
          

**Available version**

          
: 52.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
          
: POST

#### Note

POST doesn’t take
              request
              parameters or a request body.

        
        
          

**Response body for POST**

          
: Returns HTTP 201 on success.

          
: See [Batch Job Cancel Output](./connect_responses_batch_job_cancel.htm.md) for HTTP code descriptions that are
            unique to this resource in case of failure of the batch job cancel request.
