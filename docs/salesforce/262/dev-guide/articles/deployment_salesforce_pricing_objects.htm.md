---
page_id: deployment_salesforce_pricing_objects.htm
title: Salesforce Pricing Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_salesforce_pricing_objects.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_A.htm
fetched_at: 2026-06-09
---

# Salesforce Pricing Objects

This table provides the deployment sequence, object types, API names, lookup fields,
and data translation requirements for Salesforce Pricing objects in Revenue Cloud.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our company
value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

Internal objects aren't accessible.

| Object Use Type | Object Name | Object API | Deployment Sequence | Lookup Fields (Foreign Keys) |
| --- | --- | --- | --- | --- |
| Configuration | Product Selling Model  Translation table: Product Selling Model Data Translation | ProductSellingModel  Translation table: ProductSelling​ModelData​Translation | 1 |  |
| Configuration | Product Selling Model Option  Translation table: Product Selling Model Option Data Translation | ProductSellingModelOption  Translation table: ProductSelling​ModelOption​Data​Translation | 2 | ProductSellingModel (Master-Detail), Product2 (Foreign key), ProrationPolicy (Foreign key) |
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

- [*Revenue Cloud Developer Guide*: Salesforce Pricing Standard Objects](https://developer.salesforce.com/docs/./pricing_std_objects_parent.htm.md "Revenue Cloud Developer Guide: Salesforce Pricing Standard Objects - HTML (New Window)")
- [Explore the Revenue Cloud Data Model](https://help.salesforce.com/s/articleView?id=ind.data_model_overview.htm&language=en_US "Explore the Revenue Cloud Data Model - HTML (New Window)")
