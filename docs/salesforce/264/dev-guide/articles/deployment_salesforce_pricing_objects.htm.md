---
page_id: deployment_salesforce_pricing_objects.htm
title: Salesforce Pricing Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_salesforce_pricing_objects.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Management Deployment
parent_page: deployment_appendix_A.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Salesforce Pricing Objects

This table provides the deployment sequence, object types, API names, lookup fields,
    and data translation requirements for Salesforce Pricing objects in Revenue Management.

    
      

#### Important

Where possible, we changed noninclusive terms to align with our company
        value of Equality. We maintained certain terms to avoid any effect on customer
        implementations.

    

    
      

#### Note

Internal objects aren't accessible.

    

    

        
        
        
        
        
        
          
            

            

            

            

            

          

        

        
          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

        

      
| Object Use Type | Object Name | Object API | Deployment Sequence | Lookup Fields (Foreign Keys) |
| --- | --- | --- | --- | --- |
| Configuration | Product Selling Model Translation table: Product Selling Model Data Translation | ProductSellingModel Translation table: ProductSelling​ModelData​Translation | 1 |  |
| Configuration | Product Selling Model Option Translation table: Product Selling Model Option Data Translation | ProductSellingModelOption Translation table: ProductSelling​ModelOption​Data​Translation | 2 | ProductSellingModel (Master-Detail), Product2 (Foreign key), ProrationPolicy (Foreign key) |
| Configuration | Price Book | Pricebook2 | 3 | Pricebook2 (Foreign Key) |
| Configuration | Cost Book | CostBook | 4 |  |
| Configuration | Price Book Entry | PriceBookEntry | 5 | Pricebook2 (Foreign Key), Product2 (Foreign key), ProductSellingModel (Foreign Key) |
| Configuration | Cost Book Entry | CostBookEntry | 6 | CostBook (Master-Detail), Product (Foreign Key) |
| Configuration | Price Adjustment Schedule | PriceAdjustmentSchedule | 7 | Pricebook2 (Foreign Key), Contract (Foreign Key) |
| Configuration | Price Adjustment Tier | Price Adjustment Tier | 8 | PriceAdjustmentSchedule (Master-Detail), ProductSellingModel (Foreign Key), Product2 (Foreign key) |
| Configuration | Price Book Entry Derived Price | PriceBookEntryDerivedPrice | 9 | Product2 (Foreign Key), PricebookEntry (Foreign Key), Pricebook2 (Foreign Key), ProductSellingModel (Foreign Key) |
| Configuration | Bundle Based Adjustment | BundleBasedAdjustment | 10 | PriceAdjustmentSchedule (Master-Detail), Product2 (Foreign key), ProductSellingModel (Foreign Key) |
| Configuration | Attribute Based Adjustment Rule | AttributeBasedAdjRule | 11 |  |
| Configuration | Attribute Adjustment Condition | AttributeAdjustmentCondition | 12 | AttributeBasedAdjRule (Master-Detail), AttributeDefinition (Foreign Key), Product2 (Foreign Key) |
| Configuration | Attribute Based Adjustment | AttributeBasedAdjustment | 13 | PriceAdjustmentSchedule (Master-Detail), ProductSellingModel (Foreign Key), AttributeBasedAdjRule (Foreign Key), Product2 (Foreign key) |
| Configuration | Index rate (extended from Financial Services Cloud) | IndexRate | 30 |  |
| Metadata | Price Book Price Guidance | PriceBookPriceGuidance | 35 | PricebookEntry (Foreign Key), Pricebook (Foreign Key), Product (Foreign Key), ProductSellingModel (Foreign Key) |
| Metadata | Pricing Procedure Resolution | PricingProcedureResolution | 40 | ExpressionSet (Foreign Key) |
| Configuration | Pricing Procedure Output Map | PricingProcedureOutputMap | 40 | PricingRecipeTableMapping (Foreign Key), OutputFieldName (Foreign Key) |
| Metadata | Pricing Recipe | PricingRecipe | 50 | ExpressionSetDefinition (Foreign Key) |
| Configuration | Proration Policy | ProrationPolicy | 50 |  |
| Configuration | Product Price Range | ProductPriceRange | 90 | Pricebook2 (Foreign Key) |
| Configuration | Price Revision Policy | PriceRevisionPolicy |  |  |
| Metadata | Pricing Recipe Table Mapping (Internal) | PricingRecipeTableMapping |  | PricingRecipe (Master-Detail), LookupTable (Foreign Key) |
| Configuration | Product Price History Log (Internal) | ProductPriceHistoryLog |  | ProductPriceRange (Master-Detail) |
| Configuration | Pricing Adjustment Batch Job (Internal) | PricingAdjBatchJob |  |  |
| Configuration | Pricing Adjustment Batch Job Log (Internal) | PricingAdjBatchJobLog |  | PricingAdjBatchJob (Master-Detail) |
| Configuration | Procedure Plan Definition (Internal) | ProcedurePlanDefinition |  |  |
| Configuration | Procedure Plan Definition Version (Internal) | ProcedurePlanDefinitionVersion |  | ProcedurePlanDefinition (Master-Detail) |
| Configuration | Procedure Plan Criterion (Internal) | ProcedurePlanCriterion |  | ProcedurePlanOption (Master-Detail), DecisionTableParameter (Foreign Key) |
| Configuration | Procedure Plan Option (Internal) | ProcedurePlanOption |  | ProcedurePlanSection (Master-Detail), ExpressionSetDefinition (Foreign Key), DecisionTable (Foreign Key), DecisionTableParameter (Foreign Key), DecisionTableParameter (Foreign Key), DecisionTableParameter (Foreign Key), ApexClass (Foreign Key) |
| Configuration | Procedure Plan Variable (Internal) | ProcedurePlanVariable |  | ProcedurePlanDefinitionVersion (Master-Detail) |
| Configuration | Procedure Plan Section (Internal) | ProcedurePlanSection |  | ProcedurePlanDefinitionVersion (Master-Detail) |

  

#### See Also

- [*Revenue Cloud Developer Guide*: Salesforce Pricing Standard Objects](./pricing_std_objects_parent.htm.md)

- [Explore the Revenue Cloud Data Model](https://help.salesforce.com/s/articleView?id=ind.data_model_overview.htm&language=en_US)
