---
page_id: tooling_api_objects_batchdatasource.htm
title: BatchDataSource
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_batchdatasource.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch_management_setup_object.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# BatchDataSource

      Represents the source of information from which a batch job retrieves records
         for processing. This object is available in API version 66.0 and later.

      

## Supported Calls

         
         

            `describeSObjects()`, `query()`, `retrieve()`
         

      

      

## Special Access Rules

         
         

To know the permissions needed to access this object, See [User Permissions for Batch Management](https://help.salesforce.com/s/articleView?id=ind.concept_batch_management_editions.htm&language=en_US).

      

      

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
- 
- 
- 
- 

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

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

               

            
| Field | Details |
| --- | --- |
| BatchJobDefinitionId | **Type** reference **Properties** Filter, Group, Sort **Description** The ID of the batch job definition associated with batch data source. This field is a relationship field. **Relationship Name** BatchJobDefinition **Relationship Type** Master-detail **Refers To** BatchJobDefinition (the master object) |
| CriteriaJoinCondition | **Type** string **Properties** Filter, Group, Nillable, Sort **Description** The logic that's used to decide how data source records are filtered. |
| CriteriaJoinType | **Type** picklist **Properties** Defaulted on create, Filter, Group, Restricted picklist, Sort **Description** Specifies the criteria type used to filter data source records. Possible values are: `all`—All conditions are met (AND) `any`—Any condition is met (OR) `custom`—Customize the logic `none`—No conditions are met The default value is `all`. |
| DataSourceType | **Type** picklist **Properties** Filter, Group, Nillable, Restricted picklist, Sort **Description** Specifies the type of data source. Possible values are: `MultipleSobjects` `SingleSobject` `File` |
| RelatedSobjects | **Type** string **Properties** Filter, Group, Nillable, Sort **Description** The list of objects that are used as data sources for the batch job definition. |
| SourceFieldName | **Type** string **Properties** Filter, Group, Nillable, Sort **Description** The field from the source object that's used to run the batch job. |
| SourceTableName | **Type** string **Properties** Filter, Group, Sort **Description** The name of the object from which records are processed by the batch job. |
