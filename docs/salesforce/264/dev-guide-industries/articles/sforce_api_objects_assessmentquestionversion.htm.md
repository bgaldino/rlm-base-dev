---
page_id: sforce_api_objects_assessmentquestionversion.htm
title: AssessmentQuestionVersion
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_assessmentquestionversion.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_standard_objects.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# AssessmentQuestionVersion

Stores the question versions for the assessment questions. This
      object is available in API version 55.0 and later.

      

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
| ActivationDateTime | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The date when the assessment question version was set to active. |
| AdditionalInformation | **Type** textarea **Properties** Create, Nillable, Update **Description** The additional details for an UI element, such as the disclosure text. |
| AssessmentQuestionId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** Required. The ID of the assessment question associated with this record. This is a relationship field. **Relationship Name** AssessmentQuestion **Relationship Type** Lookup **Refers To** AssessmentQuestion |
| AssessmentQuestionSourceDocId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The ID of the assessment question source document that's associated with the assessment question version. This field is a relationship field. **Relationship Name** AssessmentQuestionSourceDoc **Relationship Type** Lookup **Refers To** AssessmentQuestionSourceDoc This field is available in API version 61.0 and later for users with the Generative AI Assessment Questions user license. |
| DataType | **Type** picklist **Properties** Filter, Group, Nillable, Restricted picklist, Sort **Description** The data type of the assessment question associated with this record. Possible values are: `Checkbox` `Currency` `Date` `DateTime` `Decimal` `Disclosure` `EditBlock`—Edit Block `Email` `File` `Formula` `Integer` `Multiselect`—Multi-select `Radio` `RadioGroup`—Radio Group `Select` `Telephone` `Text` `TextArea`—Text Area `TextBlock`—Text Block `Time` `URL` |
| DeactivationDateTime | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The date when the assessment question version was set to inactive. |
| Description | **Type** textarea **Properties** Create, Filter, Nillable, Sort, Update **Description** The description for the assessment question. This text is not rendered on the assessment. |
| DisplayTextCategory | **Type** picklist **Properties** Filter, Group, Nillable, Restricted picklist, Sort **Description** Specifies the category of the display text when the data type is Text Block. Possible values are: `Instruction` `Legal` `Security` |
| HelpText | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The text that's added as an infobubble in the UI element related to the assessment question. |
| IsActive | **Type** boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Indicates whether the current version of the assessment question is set to active (`true`) or not (`false`). The default value is `false`. |
| IsOptionSourceResponseValue | **Type** boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Indicates whether the response value source for an assessment question is configured as custom or SObject in the OmniStudio designer (`true`) or not (`false`). The default value is `false`. |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp for when the current user last viewed a record related to this record. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| MaximumScore | **Type** double **Properties** Create, Filter, Nillable, Sort, Update **Description** Maximum score derived from all applicable response choices for a question, used as the denominator in percentage calculations. This field is visible only if you have the QualityManagementEnabled permission enabled for your organization.This field is available in API version 67.0 and later. |
| Name | **Type** string **Properties** Create, Filter, Group, idLookup, Sort, Update **Description** Required. The name of the assessment question version record. |
| QuestionCreationType | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** Specifies how the assessment question is created from the assessment question source document. Possible values are: `GenAI` This field is available in API version 61.0 and later for users with the Generative AI Assessment Questions user license. |
| QuestionText | **Type** textarea **Properties** Create, Filter, Sort, Update **Description** Required. The assessment question text. Holds the label for the assessment question that appears on the assessment. |
| ResponseValues | **Type** textarea **Properties** Create, Nillable, Update **Description** Specifies the values to be defined in the picklist, multiselect picklist, or radio buttons. |
| Status | **Type** string **Properties** Filter, Group, Nillable, Sort **Description** The status of the assessment question version. |
| VersionNumber | **Type** int **Properties** Filter, Group, Nillable, Sort **Description** The assessment question version number. |

      

      

## Associated Objects

         
         

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
               

**[AssessmentQuestionVersionChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm)**

               
: Change events are available for the object.

            
            
               

**[AssessmentQuestionVersionFeed](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm)**

               
: Feed tracking is available for the object.

            
            
               

**[AssessmentQuestionVersionHistory](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm)**

               
: History is available for tracked fields of the object.

            
            
               

**[AssessmentQuestionVersionOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_ownersharingrule.htm)**

               
: Sharing rules are available for the object.

            
            
               

**[AssessmentQuestionVersionShare](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm)**

               
: Sharing is available for the object.
