---
page_id: sforce_api_objects_fulfillmentassetstateperiod.htm
title: FulfillmentAssetStatePeriod
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentassetstateperiod.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# FulfillmentAssetStatePeriod

      Represents the period during which the fulfillment asset configuration is
         applicable. This object is available in API version 67.0 and later. 

      

## Supported Calls

         
         

            `create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`
         

      

      

## Special Access Rules

         
         
      

      

## Fields

         
         

               
               
               
                  
                     

                     

                  

               

               
                  
                     

                     

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

                  

               

            
| Field | Details |
| --- | --- |
| CurrencyIsoCode | **Type** picklist **Properties** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** Possible values are: `EUR`—Euro `INR`—Indian Rupee `USD`—U.S. Dollar The default value is `USD`. |
| EndTime | **Type** dateTime **Properties** Create, Filter, Nillable, Sort, Update **Description** Represents the end time of the state period. If null, the configuration is effective from Start Time. If Start Time is also null, the configuration is effective at all times. |
| FulfillmentAssetId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** Represents the fulfillment asset to which this fulfillment asset state period applies. This field is a relationship field. **Relationship Name** FulfillmentAsset **Relationship Type** Master-detail **Refers To** FulfillmentAsset (the master object) |
| IsSuperseded | **Type** boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Indicates if the state period is superseded and the record is replaced by a newer version due to updates by the fulfillment process. The default value is `false`. |
| Name | **Type** string **Properties** Autonumber, Defaulted on create, Filter, idLookup, Sort **Description** The name of the fulfillment asset state period. |
| Quantity | **Type** double **Properties** Create, Filter, Sort, Update **Description** Represents the fulfillment product quantity applicable for the state period. |
| StartTime | **Type** dateTime **Properties** Create, Filter, Nillable, Sort, Update **Description** Represents the start time of the state period. If null, the configuration is effective until End Time. If End Time is also null, the configuration is effective at all times. |
