---
page_id: sforce_api_objects_quotetoopportunitysyncevent.htm
title: QuoteToOpportunitySyncEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_quotetoopportunitysyncevent.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# QuoteToOpportunitySyncEvent

      Represents an asynchronous quote to opportunity synchronization event. It
         tracks whether the sync succeeded or failed and notifies associated subscribers upon
         completion. This object is available in API version XX.0 and later. 

      

## Supported Calls

      
      

         `create()`, 
         `describeSObjects()`
      

      

      

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
| CorrelationIdentifier | **Type** string **Properties** Create, Nillable **Description** The caller-specified ID that matches this event to the originating request. |
| ErrorCode | **Type** string **Properties** Create, Nillable **Description** The error code returned when the sync fails. Null when Has Errors is False. |
| ErrorMessage | **Type** textarea **Properties** Create, Nillable **Description** The error message that explains why the sync failed. Null when Has Errors is False. |
| HasErrors | **Type** boolean **Properties** Create, Defaulted on create **Description** Indicates whether the sync failed. True if the sync completed with errors or False if the sync succeeded. The default value is `false`. |
| OpportunityRecordId | **Type** reference **Properties** Create, Nillable **Description** The ID of the Opportunity record being synced. Null if the sync fails before an Opportunity is associated. This field is a relationship field. **Relationship Name** OpportunityRecord **Refers To** Opportunity |
| QuoteRecordId | **Type** reference **Properties** Create **Description** The ID of the Quote record synced to its related Opportunity. This field is a relationship field. **Relationship Name** QuoteRecord **Refers To** Quote |
| RequestIdentifier | **Type** string **Properties** Create, Nillable **Description** The unique identifier for the request that triggered this sync event. |
| RevenueTransactionErrLogId | **Type** reference **Properties** Create, Nillable **Description** The ID of the Revenue Transaction Error Log record created when the sync fails. Null when Has Errors is False. This field is a relationship field. **Relationship Name** RevenueTransactionErrLog **Refers To** RevenueTransactionErrorLog |
