---
page_id: tooling_api_objects_batchdatasrcfiltercriteria.htm
title: BatchDataSrcFilterCriteria
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_batchdatasrcfiltercriteria.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch_management_setup_object.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# BatchDataSrcFilterCriteria

      Represents the details of a condition in the filter criteria used to retrieve
         records from the data source of a batch job. This object is available in API version
      66.0 and later. 

      

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
- 
- 
- 
- 

                  

               

            
| Field | Details |
| --- | --- |
| BatchDataSourceId | **Type** reference **Properties** Filter, Group, Sort **Description** The ID of the batch data source associated with the batch data source filter criteria. This field is a relationship field. **Relationship Name** BatchDataSource **Relationship Type** Master-detail **Refers To** BatchDataSource (the master object) |
| DomainObjectName | **Type** string **Properties** Filter, Group, Nillable, Sort **Description** The name of the object that contains the field that's used in the filter criteria condition. |
| DynamicValueType | **Type** picklist **Properties** Filter, Group, Nillable, Restricted picklist, Sort **Description** Specifies the data type of the input variable that's used in the filter criteria condition. Possible values are: `boolean` `currency` `date` `datetime` `double` `integer` `long` `number` `picklist` `reference` `string` |
| FieldName | **Type** string **Properties** Filter, Group, Sort **Description** The name of the field that's used in the filter criteria condition. |
| FieldPath | **Type** string **Properties** Filter, Group, Nillable, Sort **Description** The patch of the related object field that's used in the filter criteria condition. |
| FieldValue | **Type** string **Properties** Filter, Group, Sort **Description** The value of the specified field used to filter records of the data source. |
| FilterCriteriaSequence | **Type** int **Properties** Filter, Group, Sort **Description** The sequence number of the condition in the filter criteria. |
| IsDynamicValue | **Type** boolean **Properties** Defaulted on create, Filter, Group, Sort **Description** Indicates whether the value of the filter criteria condition is provided by an input variable. The default value is `false`. |
| Operator | **Type** picklist **Properties** Filter, Group, Restricted picklist, Sort **Description** Specifies the operator used in the filter criteria condition. Possible values are: `equals`—Equals `excludes`—Excludes `greaterThan`—Greater Than `greaterThanOrEqualTo`—Greater Than Or Equal To `in`—In `includes`—Includes `isNotNull`—Is Not Null `isNull`—Is Null `lessThan`—Less Than `lessThanOrEqualTo`—Less Than Or Equal To `like`—Like `notEquals`—Not Equals `notIn`—Not In |
