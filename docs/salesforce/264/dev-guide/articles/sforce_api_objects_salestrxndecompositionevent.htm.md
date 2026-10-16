---
page_id: sforce_api_objects_salestrxndecompositionevent.htm
title: SalesTrxnDecompositionEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_salestrxndecompositionevent.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_events_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# SalesTrxnDecompositionEvent

      Notifies when the decomposition process status changes. This object is
      available in API version 66.0 and later. 

      
         

         
         

      

      

## Supported Calls

      
      

            `describeSObjects()`
         

      

      

## Supported Subscribers

         
         

               
               
               
                  
                     

                     

                  

               

               
                  
                     

                     

                  

                  
                     

                     

                  

                  
                     

                     

                  

                  
                     

                     

                  

                  
                     

                     

                  

               

            
| Subscriber | Supported? |
| --- | --- |
| Apex Triggers |  |
| Flows |  |
| Processes |  |
| Pub/Sub API |  |
| Streaming API (CometD) |  |

      

      

## Streaming API Subscription Channel

         
         

`/event/SalesTrxnDecompositionEvent`

      

      

## Special Access Rules

         
         

This object is available in orgs with Revenue Management.

      

      

## Event Delivery Allocation Enforced

         
         

Yes

      

      

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

                  

            

            
| Field | Details |
| --- | --- |
| ErrorCode | **Type** string **Properties** Create, Nillable **Description** The error code returned for a decomposition process failure. |
| EventUuid | **Type** string **Properties** Nillable **Description** A universally unique identifier (UUID) that identifies a platform event message. |
| ReplayId | **Type** string **Properties** Nillable **Description** Represents an ID value that is populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window. |
| SalesTransactionIdentifier | **Type** string **Properties** Create, Nillable **Description** The sales transaction being decomposed. |
| Status | **Type** string **Properties** Create, Nillable **Description** The status of the decomposition process. |
