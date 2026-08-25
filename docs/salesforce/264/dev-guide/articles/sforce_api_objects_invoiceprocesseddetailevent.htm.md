---
page_id: sforce_api_objects_invoiceprocesseddetailevent.htm
title: InvoiceProcessedDetailEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_invoiceprocesseddetailevent.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: sforce_api_objects_invoiceprocessedevent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# InvoiceProcessedDetailEvent

Represents the notification to customers regarding the results of an
         attempt to create an invoice from billing schedules as part of `/commerce/billing/invoices` request. The `InvoiceProcessedDetailEvent` platform event contains the results of an attempt
         to create an invoice from one or more billing schedules that share a grouping key. Each
            `InvoiceProcessedDetailEvent`platform event for an
         action is grouped within the parent `InvoiceProcessedDetailEvent` platform event. This object is available in
      API version 62.0 and later.

      

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

      

      

## Subscription Channel

         
         

`/event/InvoiceProcessedEvent`

      

      

## Event Delivery Allocation Enforced

         
         

No

      

      

## Special Access Rules

         
         

This object is available when Billing is enabled.

      

      

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

                  

            

            
| Field | Details |
| --- | --- |
| EventUuid | **Type** string **Properties** Nillable **Description** A universally unique identifier (UUID) that identifies a platform event message. |
| InvoiceErrorDetailEvents | **Type** [InvoiceErrorDetailEvent](./sforce_api_objects_invoiceerrordetailevent.htm.md)[] **Properties** Nillable **Description** A list of errors that occurred while attempting to create the invoice. |
| InvoiceId | **Type** reference **Properties** Nillable **Description** The ID of the new invoice. This field is a relationship field. **Relationship Name** Invoice **Refers To** Invoice |
| InvoiceStatus | **Type** string **Properties** Nillable **Description** The value of the Status field on the invoice. |
| IsSuccess | **Type** boolean **Properties** Defaulted on create **Description** Required. Indicates whether the invoice creation attempt was successful (`true`) or not (`false`). The default value is `false`. |
