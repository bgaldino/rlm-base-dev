---
page_id: sforce_api_objects_attributebasedadjrule.htm
title: AttributeBasedAdjRule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_attributebasedadjrule.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# AttributeBasedAdjRule

      Represents the attribute conditions in a rule associated with the attribute
         based adjustment made for a product or service being sold. This object is available in
      API version 60.0 and later. 

      

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
- 
- 

                  

            

            
| Field | Details |
| --- | --- |
| AttributeCount | **Type** int **Properties** Filter, Group, Nillable, Sort **Description** The number of attributes. |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The date the attribute based adjustment rule was last referenced. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp for when the current user last viewed a record related to this record. |
| Name | **Type** string **Properties** Create, Filter, Group, idLookup, Sort, Update **Description** Name of the attribute based adjustment rule. |
| OwnerId | **Type** reference **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** ID of the owner of the attribute based adjustment rule. This field is a polymorphic relationship field. **Relationship Name** Owner **Relationship Type** Lookup **Refers To** Group, User |
| UsageType | **Type** picklist **Properties** Create, Filter, Group, Restricted picklist, Sort, Update **Description** The type of record where the attribute-based adjustment rule is used. Possible values are: `Pricing` `Rating` |

      

      

## Associated Objects

         
         

This object has these associated objects. If the API version isn’t specified, they’re
            available in the same API versions as this object. Otherwise, they’re available in the
            specified API version and later.

         
            
            
               

**[AttributeBasedAdjRuleFeed](./sforce_api_associated_objects_feed.htm.md)**

               
: Feed tracking is available for the object.

            
            
               

**[AttributeBasedAdjRuleHistory](./sforce_api_associated_objects_history.htm.md)**

               
: History is available for tracked fields of the object.

            
            
            
               

**[AttributeBasedAdjRuleShare](./sforce_api_associated_objects_share.htm.md)**

               
: Sharing is available for the object.
