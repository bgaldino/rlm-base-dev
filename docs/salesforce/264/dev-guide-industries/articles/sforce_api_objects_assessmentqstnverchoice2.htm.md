---
page_id: sforce_api_objects_assessmentqstnverchoice2.htm
title: AssessmentQstnVerChoice2
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_assessmentqstnverchoice2.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_standard_objects.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# AssessmentQstnVerChoice2

      Represents a choice a user can select for an assessment question
         version. This object is available in API version 63.0 and later. 

      

## Supported Calls

      
      

         `create()`, 
         `delete()`, 
         `describeLayout()`, 
         `describeSObjects()`, 
         `getDeleted()`,
         `getUpdated()`,
         `query()`, 
         `retrieve()`, 
         `search()`, 
         `undelete()`, 
         `update()`, 
         `upsert()`
      

      

      

## Supported Calls

Only users with the Education Cloud Full Access
            permission set can access this object.

      

      

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

                  

               

            
| Field | Details |
| --- | --- |
| AssessmentQuestionVersionId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** The assessment question version related to the assessment question version choice. This field is a relationship field. **Relationship Name** AssessmentQuestionVersion **Relationship Type** Master-detail **Refers To** AssessmentQuestionVersion (the master object) |
| ChoiceDescription | **Type** textarea **Properties** Create, Nillable, Update **Description** The description of the criteria that determine when the assessment question version choice is valid for evaluation. This field is visible only if you have the QualityManagementEnabled permission enabled for your organization.This field is available in API version 67.0 and later. |
| ChoiceScore | **Type** double **Properties** Create, Filter, Nillable, Sort, Update **Description** The score assigned for evaluating the assessment question version. This field is visible only if you have the QualityManagementEnabled permission enabled for your organization.This field is available in API version 67.0 and later. |
| CurrencyIsoCode | **Type** picklist **Properties** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** The ISO code for the currency related to the assessment question version choice. Possible values are: `GBP`—British Pound `USD`—U.S. Dollar The default value is `USD`. |
| DisplayOrder | **Type** int **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The order in which the question choices is displayed for an assessment question version. |
| Icon | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The name of the icon presented as a question choice when the assessment question is of the icon type. |
| IsExcludedFromScoring | **Type** boolean **Properties** Defaulted on create, Filter, Group, Sort, Update **Description** Indicates whether the specific choice is excluded when calculating the total score (`true`) or not (`false`). The default value is `false`. This field is available in API version 68.0 and later. |
| Key | **Type** string **Properties** Create, Filter, Group, Sort, Update **Description** A unique code or identifier for a question choice that's mapped to an assessment question version. |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp when the current user last accessed this record, a record related to this record, or a list view. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp when the current user last viewed this record or list view. If this value is null, the user might have only accessed this record or list view (LastReferencedDate) but not viewed it. |
| Name | **Type** string **Properties** Create, Filter, Group, idLookup, Sort, Update **Description** The name of the assessment question version choice. |
| UniqueIndex | **Type** string **Properties** Filter, Group, idLookup, Nillable, Sort **Description** The unique index for the AssessmentQuestionVersionId and Key pair. This field is a calculated field. |
