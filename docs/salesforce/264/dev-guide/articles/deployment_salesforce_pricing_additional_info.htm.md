---
page_id: deployment_salesforce_pricing_additional_info.htm
title: Salesforce Pricing Additional Information
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_salesforce_pricing_additional_info.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Management Deployment
parent_page: deployment_appendix_C.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Salesforce Pricing Additional Information

Get to know additional deployment information for Salesforce Pricing in Revenue Management,
    including active or inactive states, object information, and migration
    considerations.

    

## Object-Specific Information

   
      
      

          
          
          
          
            
              

              

              

            

          

          
            
              

              

              
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

            

            
          

        
| Object Name | Object API | Notes |
| --- | --- | --- |
| Attribute Based Adjustment | AttributeBasedAdjustment | [Considerations for Migrating Decision Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm&language=en_US) [Considerations for Migrating Expression Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm&language=en_US) [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm&language=en_US) |
| Price Adjustment Tier | PriceAdjustmentTier | [Considerations for Migrating Decision Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm&language=en_US) [Considerations for Migrating Expression Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm&language=en_US) [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm&language=en_US) |
| Bundle Based Adjustment | BundleBasedAdjustment | [Considerations for Migrating Decision Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm&language=en_US) [Considerations for Migrating Expression Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm&language=en_US) [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm&language=en_US) |
| Product Price Range | ProductPriceRange | [Considerations for Migrating Decision Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm&language=en_US) [Considerations for Migrating Expression Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm&language=en_US) [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm&language=en_US) |

    

   
    

## Other Information

      
      
        
- You need active context definitions for pricing recipes. A pricing recipe is marked as
          default in an org. A System Admin can access the PricingRecipe object whereas a Pricing
          Admin can't access this object internally. You can’t create or update fields of a
          PricingRecipe object.

        
- You must activate decision tables and pricing procedures.

        
- You need a refresh of the decision table for any new or modified records. For example,
          any modification in price book entries requires a refresh of the Price Book Entries
          decision table.

        
- You must migrate the Apex class if Apex is selected for Procedure Plan definitions. See
            [Customize Your Procedure Plans
            with Apex Hooks](https://help.salesforce.com/s/articleView?id=ind.pricing_customize_pricing_procedures_with_apex_hooks.htm&language=en_US).

        
- You can’t delete a standard price book. A price book can be deleted after all references
          are removed. Instead, set the price book to Inactive status.

        
- If you delete a price adjustment schedule, all associated data is deleted without any
          warning or error messages. The adjustment method and status of a price adjustment schedule
          aren’t considered for resolution. If you edit or delete an active price adjustment
          schedule, an error is thrown.

        
- The EffectiveFrom and EffectiveTo field values of a price adjustment tier,
          attribute-based adjustment, and bundle-based adjustment must be within the EffectiveFrom
          and EffectiveTo field values.

        
- Product and product selling model must be a part of the product selling model option
          before you create values in a price book entry.

        
- You can’t delete an inactive or active product selling model. You can delete a draft
          product selling model by deleting all references. You can’t change status from Active or
          Inactive to Draft.

        
- You can’t edit a product price range after you've created it. Enable price tracking to
          edit a product price range.

        
- Salesforce Pricing doesn’t consider the Active status of a price book when fetching the
          values. Also, it doesn't consider the validity date ranges of a price book.

        
- The pricing term and pricing term unit of a price adjustment tier aren’t considered for
          resolution.

        
- The IsActive field of a price book entry and price adjustment schedule aren’t considered
          for resolution.

      

    

  

- 
**[Salesforce Pricing Migration Scenarios](./deployment_salesforce_pricing_migration_scenarios.htm.md)**  

Review these considerations to understand the Salesforce Pricing data migration process     along with migration order and prerequisites.
