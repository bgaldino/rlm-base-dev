---
page_id: sforce_api_objects_costbook.htm
title: CostBook
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_costbook.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# CostBook

Represents the cost book that contains multiple cost book
         entries. This object is available in API version 61.0 and later.

      

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

: 

                  

            

            
| Field | Details |
| --- | --- |
| EffectiveFrom | **Type** dateTime **Properties** Create, Filter, Sort, Update **Description** Date and time when the cost book comes into effect. |
| EffectiveTo | **Type** dateTime **Properties** Create, Filter, Nillable, Sort, Update **Description** Date and time till when the cost book is no longer in effect. |
| IsDefault | **Type** boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Indicates whether the cost book is default (`true`) or not (`false`). The default value is `true`. |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** Timestamp for when the current user last referred to this record. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** Timestamp for when the current user last viewed a record related to this record. |
| Name | **Type** string **Properties** Create, Filter, Group, idLookup, Sort, Update **Description** Name of the cost book. |
| OwnerId | **Type** reference **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** ID of the user who created the record. This field is a polymorphic relationship field. **Relationship Name** Owner **Relationship Type** Lookup **Refers To** Group, User |

      

      

## Associated Objects

         
         

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
            
               

**[CostBookFeed](./sforce_api_associated_objects_feed.htm.md)**

               
: Feed tracking is available for the object.

            
            
               

**[CostBookHistory](./sforce_api_associated_objects_history.htm.md)**

               
: History is available for tracked fields of the object.

            
            
            
               

**[CostBookShare](./sforce_api_associated_objects_share.htm.md)**

               
: Sharing is available for the object.
