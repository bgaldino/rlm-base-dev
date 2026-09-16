---
page_id: sforce_api_objects_contractitempriceadjtier.htm
title: ContractItemPriceAdjTier
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_contractitempriceadjtier.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ContractItemPriceAdjTier

      Represents the tiers of a price adjustment to a product on a contract.
      This object is available in API version 63.0 and later. 

      
         

#### Important

Where possible, we changed noninclusive terms to align with our
            company value of Equality. We maintained certain terms to avoid any effect on customer
            implementations.

      

      

## Supported Calls

         
         

            `create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`
         

      

      

## Special Access Rules

         
         

This object is available with Revenue Management.

      

      

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
- 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

               

            
| Field | Details |
| --- | --- |
| ContractItemPriceId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** The contract item price ID associated with the contract item price adjustment tier. This field is a relationship field. **Relationship Name** ContractItemPrice **Relationship Type** Master-detail **Refers To** ContractItemPrice (the master object) |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp when the current user last accessed this record, a record related to this record, or a list view. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** Timestamp when the current user last viewed this record or list view. If this value is null, the user accessed this record or list view (LastReferencedDate) but didn’t view it. |
| LowerBound | **Type** double **Properties** Create, Filter, Sort, Update **Description** The minimum quantity for the adjustment to be applicable. |
| Name | **Type** string **Properties** Autonumber, Defaulted on create, Filter, idLookup, Sort **Description** The name of the record. |
| TierType | **Type** picklist **Properties** Create, Filter, Group, Restricted picklist, Sort, Update **Description** The type of adjustment tier. Valid values are: `AdjustmentAmount` `AdjustmentPercentage` `OverrideAmount` |
| TierValue | **Type** double **Properties** Create, Filter, Sort, Update **Description** The price adjustment value. |
| UpperBound | **Type** double **Properties** Create, Filter, Nillable, Sort, Update **Description** The maximum quantity for the adjustment to be applicable. |

      

      

## Associated Objects

         
         

This object has associated objects. If the API version isn’t specified, they’re
            available in the same API versions as this object. Otherwise, they’re available in the
            specified API version and later.

         
            
               

**[ContractItemPriceAdjTierFeed](./sforce_api_associated_objects_feed.htm.md)**

               
: Feed tracking is available for the object.

            
            
               

**[ContractItemPriceAdjTierHistory](./sforce_api_associated_objects_history.htm.md)**

               
: History is available for tracked fields of the object.
