---
page_id: sforce_api_objects_assetrateadjustment.htm
title: AssetRateAdjustment
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_assetrateadjustment.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# AssetRateAdjustment

Stores the tier rate adjustments for the asset rate card
         entries.This object is available in API version 62.0 and later.

      
         

#### Important

Where possible, we changed noninclusive terms
            to align with our company value of Equality. We maintained certain terms to avoid any
            effect on customer implementations.

      

      

## Supported Calls

         
         

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`

      

      

## Special Access Rules

         
         

This object is available in orgs where Revenue Cloud is enabled.

      

      

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

                  

               

            
| Field | Details |
| --- | --- |
| AdjustmentType | **Type** picklist **Properties** Create, Filter, Group, Restricted picklist, Sort, Update **Description** The type of rate adjustment. Valid values are: `Amount`—Adjusts rate by using a specific amount. `Override`—Adjusts rate by using the override rate. `Percentage`—Adjusts rate by using a percentage. |
| AdjustmentValue | **Type** double **Properties** Create, Filter, Sort, Update **Description** The value of the adjustment. |
| AssetRateCardEntryId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** The ID of the parent asset rate card entry record associated with the asset rate adjustment. This field is a relationship field. **Relationship Name** AssetRateCardEntry **Relationship Type** Master-detail **Refers To** AssetRateCardEntry (the master object) |
| LowerBound | **Type** double **Properties** Create, Filter, Nillable, Sort, Update **Description** The minimum quantity for the adjustment to be applicable. |
| Name | **Type** string **Properties** Create, Filter, Group, idLookup, Sort, Update **Description** The name of the asset rate adjustment. |
| UpperBound | **Type** double **Properties** Create, Filter, Nillable, Sort, Update **Description** The maximum quantity for the adjustment to be applicable. |
