---
page_id: sforce_api_objects_fulfillmentplan.htm
title: FulfillmentPlan
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentplan.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# FulfillmentPlan

Represents a set of steps to be created to fulfill the order.
      This object is available in API version 61.0 and later.

      

## Supported Calls

      
      

         `create()`, 
         `delete()`, 
         `describeLayout()`, 
         `describeSObjects()`, 
         `getDeleted()`,
         `getUpdated()`,
         `query()`, 
         `retrieve()`, 
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

                  

               

            
| Field | Details |
| --- | --- |
| ExecutionUserId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** For internal use only. **Relationship Name** ExecutionUser **Refers To** User |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The most recent date when a user referenced this record. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The most recent date when a user viewed this record. |
| Name | **Type** string **Properties** Autonumber, Defaulted on create, Filter, idLookup, Sort **Description** The name of the fulfillment plan. |
| OwnerId | **Type** reference **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** The ID of the user who created the record. This field is a polymorphic relationship field. **Relationship Name** Owner **Refers To** Group, User |
| Priority | **Type** picklist **Properties** Filter, Group, Nillable, Restricted picklist, Sort **Description** The priority of the fulfillment plan execution. This field is available in API version 63.0 and later. Valid values are: `Default` `High` `Bulk` |
| SourceIdentifier | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update, idLookup (Available in API version 64.0 and later) **Description** For internal use only. |
| SourceType | **Type** string **Properties** Create, Filter, Group, Nillable, Sort **Description** The type of source for the fulfillment plan. This field is available in API version 62.0 and later. |
| State | **Type** picklist **Properties** Create, Filter, Group, Restricted picklist, Sort, Update **Description** The status of the fulfillment plan. Valid values are: `Completed` `InProgress` `NotStarted` |
| UsageType | **Type** picklist **Properties** Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update **Description** The business that uses Fulfillment Orchestration. Valid values are: `IntegrationOrchestrator` `Generic` `StageManagement` |

      

      

## Associated Objects

         
         

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
               

**[FulfillmentPlanChangeEvent](./sforce_api_associated_objects_change_event.htm.md)**

               
: Change events are available for the object.

            
            
            
               

**[FulfillmentPlanHistory](./sforce_api_associated_objects_history.htm.md)**

               
: History is available for tracked fields of the object starting API version
                  65.0.

            
            
            
               

**[FulfillmentPlanShare](./sforce_api_associated_objects_share.htm.md)**

               
: Sharing is available for the object.
