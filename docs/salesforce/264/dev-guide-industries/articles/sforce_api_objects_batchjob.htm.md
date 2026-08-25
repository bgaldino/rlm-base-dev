---
page_id: sforce_api_objects_batchjob.htm
title: BatchJob
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_batchjob.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: monitor_workflow_services_dev_overview.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# BatchJob

    Represents an instance of a batch job that is either running and has been
      run. This object is available in API version 51.0 and later. 

    

## Supported Calls

      
      

        `delete()`, `describeLayout()`, `describeSObjects()`,
          `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`,
          `undelete()`
      

    

    

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
- 
- 

            

            
              

              

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
- 
- 

            

            
              

              

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
- 
- 
- 
- 
- 
- 
- 

            

            
              

              

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
- 

            

            
              

              

: 

: 

: 
: 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 

            

            
              

              

: 

: 

: 

            

            
              

              

: 

: 

: 

            

          

        
| Field | Details |
| --- | --- |
| AdditionalInformation | **Type** textarea **Properties** Create, Nillable, Update **Description** A JSON that contains additional context about the batch jon. |
| ApiVersion | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The Salesforce API version in which this definition was created. |
| BatchJobDefinitionId | **Type** reference **Properties** Filter, Group, Sort **Description** The unique identifier of the associated batch job definition. This is a relationship field. **Relationship Name** BatchJobDefinition **Relationship Type** Lookup **Refers To** BatchJobDefinition |
| BatchJobDefinitionName | **Type** string **Properties** Filter, Group, Sort **Description** The developer name of the associated batch job definition. |
| DefinitionType | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** The type of batch calculation job definition that was used to create this batch job. Possible values are: `Calcservice` |
| EndTime | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp when the batch job run was completed. |
| ErrorDescription | **Type** string **Properties** Filter, Nillable, Sort **Description** The error message in case the batch job run failed. |
| ExecutionStage | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** Specifies the stage at which the batch job's run failed. This field is available in API version 66.0 and later. Possible values are: `Datasync` `Execution` `Preprocessing` `Writeback` |
| ExternalReference | **Type** string **Properties** Filter, Group, Nillable, Sort **Description** The unique identifier of the process that's running or has run the batch job. |
| IsDebugOn | **Type** boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Indicates whether debug mode was turned on (true) or not (false) when a definition was run. The default value is `false`. |
| IsDebugRecipeDeleted | **Type** boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Indicates whether debug recipes and datasets were deleted (true) or not (false). When the IsDebugOn is set to True, and the definition is run, after 7 days IsDebugRecipeDeleted is automatically set to True, and debug recipes and datasets are deleted. The default value is `false`. |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp for when the current user last viewed the batch job. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp for when the current user last viewed this item. |
| Name | **Type** string **Properties** Filter, Group, idLookup, Sort **Description** The name of the batch job. |
| OwnerId | **Type** reference **Properties** Filter, Group, Sort **Description** Unique identifier of the user who initiated the batch job run. This is a polymorphic relationship field. **Relationship Name** Owner **Relationship Type** Lookup **Refers To** Group, User |
| ProcessGroup | **Type** string **Properties** Filter, Group, Sort **Description** The group or team for which the batch job is run. |
| QueuingRetryCount | **Type** int **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The number of times the scheduler attempted to queue the batch job before succeeding. |
| RetryCount | **Type** int **Properties** Filter, Group, Nillable, Sort **Description** The number of times the batch job run is automatically rerun in case it fails. |
| RunByUser | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The ID of the user who initiated the batch job execution. |
| RuntimeParameter | **Type** textarea **Properties** Nillable **Description** The values of the input variables that are used as filter criteria in a Batch Management job. |
| StartTime | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp when the batch job run was started. |
| Status | **Type** picklist **Properties** Filter, Group, Restricted picklist, Sort **Description** The status of the batch job run. Possible values are: `Canceled` `Canceling` `Completed` `CompletedWithFailures` `Failed` `InProgress` `Queued` `QueueingInProgress` `Submitted` |
| TotalInputRecordCount | **Type** int **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The total number of records that were provided as input to the batch job. This field is available in API version 66.0 and later. |
| TotalProcessedRecordCount | **Type** int **Properties** Filter, Group, Nillable, Sort **Description** The total number of records that were processed by all the batch job parts associated with the batch job. This field is available in API version 66.0 and later. |
| TriggerType | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** Specifies the mode with which this batch job is triggered. Possible values are: `API` `RunNow` `Schedule` |
| Type | **Type** picklist **Properties** Defaulted on create, Filter, Group, Restricted picklist, Sort **Description** The type of batch job that is run. Possible values are: `BulkUpdate` `Calc`—Data Processing Engine `ConsumptionOveragesCalculation` `DecisionTableRefresh` `DeepCloneSalesAgreement` `FlattenAccountIOUHierarchyBatchJob` `Flow` `EnergyUseRecordCreationBatchJob` `EntitlementCreationBatchJob` `HighScaleBreProcess` `IndustriesLSCommercial` `InvoiceDTPRunBatchJob` `InvoiceRecoveryRunBatchJob` `InvoiceRunBatchJob` `LifeSciProviderActivityGoalSharingBatchJob` `LoyaltyProgramProcess` `NetUnitRateCalculation` `NextGenCommitmentBatchProcessingJob` `ManagerProvisioning` `PbbToOptyConversion` `ProductCatalogCacheRefresh` `PromotionChannelPropagationBatchJob` `RatableSummaryCreation` `ServiceProcess` `StoreAssortmentPropagationBatchJob` `SummaryCreation` `WorkDotComToHRManagerProvisioning` The process types available to you vary depending on the licenses available in your org. |
| UtilisedExecutionLimit | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The CRM Analytics or Data 360 execution capacity utilized by Data Processing Engine batch jobs before the current run started. This field is available in API version 66.0 and later. |
| UtilisedWritebackLimit | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The CRM Analytics or Data 360 writeback capacity utilized by Data Processing Engine batch jobs before the current run started. This field is available in API version 66.0 and later. |

    

    

## Associated Objects

      
      

This object has the following associated objects. If the API version isn’t specified,
        they’re available in the same API versions as this object. Otherwise, they’re available in
        the specified API version and later.

      
        
          

**BatchJobFeed**

          
: Feed tracking is available for the object.

        
        
          

**BatchJobHistory**

          
: History is available for tracked fields of the object.
