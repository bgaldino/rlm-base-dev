---
page_id: actions_obj_submit_failed_records_batchjob.htm
title: Submit Failed Records Batch Job
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/actions_obj_submit_failed_records_batchjob.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch_mgt_actions_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Submit Failed Records Batch Job

Run to resubmit an existing batch job with failed records for
   processing. This action executes the batch job asynchronously.

  
   

This object is available in API version 52.0 and later.

  

  

## Special Access Rules

To know the products and user permissions needed to
    access this action, See [Supported Editions and Permissions for Batch
    Management](https://help.salesforce.com/s/articleView?id=ind.concept_batch_management_editions.htm&language=en_US).

  

## Supported REST HTTP Methods

   
   
    
     

**URI**

     
: ``/services/data/vXX.X/`actions/standard/submitFailedRecordsBatchJob`

    
    
     

**Formats**

     
: JSON

    
    
     

**HTTP Methods**

     
: GET, POST

    
    
     

**Authentication**

     
: `Authorization: Bearer token`

    
   

  

  

## Inputs

   
   

     
     
     
      
       

       

      

     

     
      
       

       

: 

: 

      

      
       

       

: 

: 

      

     

    
| Input | Details |
| --- | --- |
| failedRecordIds | **Type** array **Description** The IDs of failed records in a batch job. |
| parentBatchJobId | **Type** string **Description** Required. The ID of a batch job with failed records. |

  

  

## Outputs

   
   

     
     
     
      
       

       

      

     

     
      
       

       

: 

: 

      

      
       

       

: 

: 

      

     

    
| Output | Details |
| --- | --- |
| batchJobId | **Type** string **Description** The ID of a batch job generated after the request is successful. This batch job ID is used to track the progress of the batch job in Monitor Workflow Services in the org. |
| status | **Type** string **Description** Indicates whether a batch job succeeded or failed. |

  

  

## Usage

   
   

**JSON Sample Request**

   
    

```
{
   "inputs": [{
      "parentBatchJobId": "0mdRM0000004DXrYAM",
      "failedRecordIds": [
         "001RM000005AG0bYAG", "001RM000005AERZYA4", "001RM000005AG0WYAW"
      ]
   }]
}
```

   

   

**JSON Sample Response**

   

```
[ {
   "actionName" : "submitFailedRecordsBatchJob",
   "errors" : null,
   "isSuccess" : true,
   "outputValues" : {
      "batchJobId" : "0mdRM0000004DZ9YAM"
   }
} ]
```
