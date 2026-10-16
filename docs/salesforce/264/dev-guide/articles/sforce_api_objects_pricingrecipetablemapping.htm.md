---
page_id: sforce_api_objects_pricingrecipetablemapping.htm
title: PricingRecipeTableMapping
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_pricingrecipetablemapping.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_tooling_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# PricingRecipeTableMapping

      Represents the mapping of pricing components of a lookup table with the
         chosen pricing recipe. This object is available in API version 60.0 and later. 

      

## Supported Calls

      
      

         `create()`, 
         `delete()`, 
         `describeSObjects()`, 
         `query()`, 
         `retrieve()`, 
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
- 
- 
- 
- 
- 
- 
- 
- 
- 
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

                  

            

            
| Field | Details |
| --- | --- |
| FileBasedDecisionTableName | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** Name of the file-based decision table. |
| IsInternal | **Type** boolean **Properties** Defaulted on create, Filter, Group, Sort **Description** Indicates if the price recipe field mapping record is created internally by the platform (true) or not (false). The default value is `false`. |
| LookupTableId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The lookup table associated with the mapped fields. This field is a polymorphic relationship field. **Relationship Name** LookupTable **Relationship Type** Lookup **Refers To** DecisionMatrixDefinition, DecisionTable |
| PricingComponentType | **Type** Pricing Element Type enumerated list **Properties** Create, Filter, Group, Restricted picklist, Sort, Update **Description** The pricing component field data on which the decision table is built. Possible values are: `AttributeDiscount`—Attribute Based Discount `BundleDiscount`—Bundle Based Discount `DerivedPricing` `ListPrice`—List Price `PriceAdjustmentMatrix` `PromotionsDiscount` `VolumeDiscount`—Volume Based Discount `VolumeTierDiscount`—Tier Discount `DiscountDistributionService`. This value is available in API version 60.0 and later. `MinimumPrice`. This value is available in API version 62.0 and later. `RuleFetch`. This value is available in API version 64.0 and later. `AssetDiscovery`. This value is available in API version 64.0 and later. |
| PricingRecipeId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** The pricing data store associated with this pricing recipe field mappings. This field is a relationship field. **Relationship Name** PricingRecipe **Relationship Type** Lookup **Refers To** PricingRecipe |
