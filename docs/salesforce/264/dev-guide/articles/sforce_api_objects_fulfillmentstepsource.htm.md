---
page_id: sforce_api_objects_fulfillmentstepsource.htm
title: FulfillmentStepSource
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentstepsource.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# FulfillmentStepSource

Represents a link between a fulfillment step and the corresponding
         order lines. This object is available in API version 61.0 and later.

      
         

#### Important

Where possible, we changed noninclusive terms to align with our
            company value of Equality. We maintained certain terms to avoid any effect on customer
            implementations.

      

      

## Supported Calls

         
         

            `create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`
         

      

      

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

                     
                  

                  
               

            
| Field | Details |
| --- | --- |
| Name | **Type** string **Properties** Autonumber, Defaulted on create, Filter, idLookup, Sort **Description** An automatically generated name for the fulfillment step source. |
| SourceIdentifier | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The identifier of the source order line item (order item or fulfillment order line). |
| SourceLineItemId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** For internal use only. This field is a polymorphic relationship field. **Relationship Name** SourceLineItem **Refers To** FulfillmentOrderLineItem, OrderItem |
| StepId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** The identifier of the fulfillment step. This field is a relationship field. **Relationship Name** Step **Relationship Type** Master-detail **Refers To** FulfillmentStep (the master object) |
| VersionGroupIdentifier | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The ID of the version group that's assigned to the fulfillment step source item. This field is available in API version 64.0 and later. |

      

      
      

## Associated Objects

         
         

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
               

**[FulfillmentStepSourceChangeEvent](./sforce_api_associated_objects_change_event.htm.md)**

               
: Change events are available for the object.
