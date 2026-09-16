---
page_id: sforce_api_objects_batchjobpartfailedrecord.htm
title: BatchJobPartFailedRecord
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_batchjobpartfailedrecord.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: monitor_workflow_services_dev_overview.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# BatchJobPartFailedRecord

    Represents records that a batch job part couldn't successfully process.
    This object is available in API version 51.0 and later. 

    

## Supported Calls

      
      

`describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`,
          `retrieve()`

    

    

## Special Access Rules

      
      

To know the permissions needed to access this object, See [User Permissions for Data Processing Engine](https://help.salesforce.com/s/articleView?id=ind.dpe_setup.htm&language=en_US) or [User Permissions for Batch Management](https://help.salesforce.com/s/articleView?id=ind.concept_batch_management_editions.htm&language=en_US).

    

    

## Fields

      
      

          
          
          
            
              

              

            

          

          
            
              

              

: 

: 

: 
: 

: 

: 

: 

            

            
              

              

: 

: 

: 
: 

: 

: 

: 

            

            
              

              

: 

: 

: 

            

            
              

              

: 

: 

: 

            

            
              

              

: 

: 

: 

: 

            

            
              

              

: 

: 

: 

            

            
              

              

: 

: 

: 

            

            
              

              

: 

: 

: 
: 

: 

: 

: 

            

            
              

              

: 

: 

: 
: 
- 
- 

: 

            

          

        
| Field | Details |
| --- | --- |
| BatchJobId | **Type** reference **Properties** Filter, Group, Nillable, Sort **Description** The unique identifier of the associated batch job. This is a relationship field. **Relationship Name** BatchJob **Relationship Type** Lookup **Refers To** BatchJob |
| BatchJobPartId | **Type** reference **Properties** Filter, Group, Sort **Description** The unique identifier of the associated batch job part. This is a relationship field. **Relationship Name** BatchJobPart **Relationship Type** Lookup **Refers To** BatchJobPart |
| ErrorDescription | **Type** string **Properties** Filter, Nillable, Sort **Description** The error message that indicates why the batch job part couldn't process the records. |
| Name | **Type** string **Properties** Filter, Group, idLookup, Sort **Description** The name of the batch job part failed record. |
| ProcessingGroupKey | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Length** 100 **Description** The field used for creating batch job parts. It can be a Group By field selected from the UI or a Partition Key from the API. |
| Record | **Type** string **Properties** Filter, Group, Nillable, Sort **Description** The unique identifier of the batch record that processed the failed records. |
| RecordName | **Type** string **Properties** Filter, Group, Nillable, Sort **Description** The name of the record that's associated with the batch job part failed record. |
| ResubmittedBatchJobId | **Type** reference **Properties** Filter, Group, Nillable, Sort **Description** The batch job used to submit failed records. This field is available in API version 52.0 and later. This is a relationship field. **Relationship Name** ResubmittedBatchJob **Relationship Type** Lookup **Refers To** BatchJob |
| Status | **Type** picklist **Properties** Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort **Description** Specifies the status of the failed records. This field is available in API version 52.0 and later. Possible values are: `Failed` `Resubmitted` The default value is 'Failed'. |

    

    

## Associated Objects

      
      

This object has the following associated objects. If the API version isn’t specified,
        they’re available in the same API versions as this object. Otherwise, they’re available in
        the specified API version and later.

      
        
          

**BatchJobPartFailedRecordFeed**

          
: Feed tracking is available for the object.

        
        
          

**BatchJobPartFailedRecordHistory**

          
: History is available for tracked fields of the object.
