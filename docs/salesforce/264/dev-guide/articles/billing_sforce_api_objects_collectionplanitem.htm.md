---
page_id: billing_sforce_api_objects_collectionplanitem.htm
title: Billing Fields on CollectionPlanItem
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_collectionplanitem.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Billing Fields on CollectionPlanItem

      Standard fields extend the CollectionPlanItem object for use in Billing to
         represent information about the invoice balance. This object is available in API
      version 64.0 and later.

      

## Supported Calls

         
         

            `create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`
         

      

      

## Special Access Rules

         
         

You need the Revenue Cloud Billing license, and the Billing Collections and Recovery
            Specialist permission set to access this object.

      

      

## Fields

         
         

               
               
               
                  
                     

                     

                  

               

               
                  
                     

                     

: 

: 

: 

                  

               

            
| Field | Details |
| --- | --- |
| InvoiceBalance | **Type** currency **Properties** Filter, Nillable, Sort **Description** The balance amount of the invoice associated with the collection plan item. |

      

      

## Associated Objects

         
         

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
               

**[CollectionPlanItemChangeEvent](./sforce_api_associated_objects_change_event.htm.md)**

               
: Change events are available for the object.

            
            
               

**[CollectionPlanItemFeed](./sforce_api_associated_objects_feed.htm.md)**

               
: Feed tracking is available for the object.

            
            
               

**[CollectionPlanItemHistory](./sforce_api_associated_objects_history.htm.md)**

               
: History is available for tracked fields of the object

            
         

      

   

#### See Also

- [*Industries Common Resources Developer Guide*: CollectionPlanItem](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_objects_collectionplanitem.htm)
