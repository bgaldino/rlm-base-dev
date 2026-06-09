---
page_id: pricing_std_objects_parent.htm
title: Salesforce Pricing Standard Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/pricing_std_objects_parent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_overview.htm
fetched_at: 2026-06-09
---

# Salesforce Pricing Standard Objects

The Salesforce Pricing data model provides objects and fields to manage pricing
processes, such as product management and calculation and application of discounts.

- **[AttributeAdjustmentCondition](./sforce_api_objects_attributeadjustmentcondition.htm.md)**  
  Represents the condition applied to an attribute that determines the price of a product or service being sold. This object is available in API version 60.0 and later.
- **[AttributeBasedAdjRule](./sforce_api_objects_attributebasedadjrule.htm.md)**  
  Represents the attribute conditions in a rule associated with the attribute based adjustment made for a product or service being sold. This object is available in API version 60.0 and later.
- **[AttributeBasedAdjustment](./sforce_api_objects_attributebasedadjustment.htm.md)**  
  Represents the association between the product selling model and the price adjustment for product or service being sold based on its attributes. This object stores information about the attributes that define the price of the product or service, the discounts applied, along with its value for a given date range. This object is available in API version 60.0 and later.
- **[AttributeDefinition](./sforce_api_objects_attributedefinition.htm.md)**  
  Represents a product, asset, or object attribute, for example, a hardware specification or software detail. This object is available in API version 60.0 and later.
- **[BundleBasedAdjustment](./sforce_api_objects_bundlebasedadjustment.htm.md)**  
  Represents the association between the product selling model and the price adjustment for a product or service being sold as a bundle. This object stores information of the product or service's price, the discounts applied, along with its value for a given date range. This object is available in API version 60.0 and later.
- **[CostBook](./sforce_api_objects_costbook.htm.md)**  
  Represents the cost book that contains multiple cost book entries. This object is available in API version 61.0 and later.
- **[ContractItemPrice](./sforce_api_objects_pricing_contractitemprice.htm.md)**  
  Represents the price of a product on the contract. This object is available in API version 61.0 and later.
- **[CostBookEntry](./sforce_api_objects_costbookentry.htm.md)**  
  Represents the total cost of a product or service that’s determined based on various factors that affect a product's price. For example, when a product is manufactured, the weight of the raw material can be a cost factor based on the amount of material required and its shipping cost. This object is available in API version 61.0 and later.
- **[PriceAdjustmentSchedule](./sforce_api_objects_priceadjustmentschedule.htm.md)**  
  Represents a series of tiered discounts based on the number of items purchased.  This object is available in API version 60.0 and later.
- **[PriceAdjustmentTier](./sforce_api_objects_priceadjustmenttier.htm.md)**  
  Represents a discount tier in a price adjustment schedule.  This object is available in API version 60.0 and later.
- **[PriceBook2](./sforce_api_objects_pricebook2.htm.md)**  
  Represents a price book that contains the list of products that your org sells. This object is available in API version 60.0 and later.
- **[PriceBookEntry](./sforce_api_objects_pricebookentry.htm.md)**  
  Represents a product entry (an association between a Pricebook2 and Product2) in a price book. This object is available in API version 60.0 and later.
- **[PriceBookEntryDerivedPrice](./sforce_api_objects_pricebookentryderivedprice.htm.md)**  
  Represents the price of a product that’s derived from another source such as a product or an asset. This object is available in API version 61.0 and later.
- **[PriceRevisionPolicy](./sforce_api_objects_pricerevisionpolicy.htm.md)**  
  Represents the guidelines and methods used to modify product or service prices, often incorporating formulas based on price revision entries and various adjustments. For example, a policy might dictate that prices are revised based on a formula that considers the regional Consumer Price Index (CPI) with a specific adjustment percentage, effective from a defined date, and categorized as either a flat adjustment or one directly based on the price revision entry data. This object is available in API version 65.0 and later.
- **[PricingAdjBatchJob](./sforce_api_objects_pricingadjbatchjob.htm.md)**  
  Represents the collective update of multiple records on their prices and other adjustments. This object is available in API version 62.0 and later.
- **[PricingAdjBatchJobLog](./sforce_api_objects_pricingadjbatchjoblog.htm.md)**  
  Represents the report that contains a list of failed adjustment requests along with an error message that describes the reason for failure. This object is available in API version 62.0 and later.
- **[PricingAPIExecution](./sforce_api_objects_pricingapiexecution.htm.md)**  
  Represents the pricing resolution for an pricing element determined using strategy name and formula. This object is available in API version 63.0 and later.
- **[PricingProcedureResolution](./sforce_api_objects_pricingprocedureresolution.htm.md)**  
  Represents a selection for a pricing procedure to execute a pricing process from a list of pricing procedures available. This object is available in API version 60.0 and later.
- **[PricingProcessExecution](./sforce_api_objects_pricingprocessexecution.htm.md)**  
  Represents a record generated during the execution of a discovery or pricing procedure. Multiple procedures may be performed within a single API call, with each recorded in a Pricing API Execution record. This object is available in API version 63.0 and later.
- **[ProductPriceHistoryLog](./sforce_api_objects_productpricehistorylog.htm.md)**  
  Stores historical pricing data based on the product's price range. This object is available in API version 62.0 and later.
- **[ProductPriceRange](./sforce_api_objects_productpricerange.htm.md)**  
  Represents the price range of a product determined by using a product selling model that’s stored in the relevant price book. This object is available in API version 62.0 and later.
- **[ProductSellingModel](./sforce_api_objects_productsellingmodel.htm.md)**  
  Defines one method by which a product can be sold; for example, as a one-time sale, an evergreen subscription, or a termed subscription. If the product is sold on subscription, this object defines the subscription’s term. A product can have multiple product selling models.  This object is available in API version 60.0 and later.
- **[ProductSellingModelDataTranslation](./sforce_api_objects_productsellingmodeldatatranslation.htm.md)**  
  Represents the translated values of the data stored within the ProductSellingModel record’s fields. This object is available in API version 61.0 and later.
- **[ProductSellingModelOption](./sforce_api_objects_productsellingmodeloption.htm.md)**  
  A junction object between Product Selling Model and Product2. This object is available in API version 60.0 and later.
- **[ProcedurePlanCriterion](./sforce_api_objects_procedureplancriterion.htm.md)**  
  The procedure plan option associated with the procedure plan criterion record. This object is available in API version 67.0 and later.
- **[ProrationPolicy](./sforce_api_objects_prorationpolicy.htm.md)**  
  Represents the proration policy associated with a Product Selling Model Option that determines how a product's price is calculated based on subscription duration or billing periods. This object is available in API version 67.0 and later.

#### See Also

- [*Object Reference for the Salesforce Platform*: Overview of Salesforce Objects
  and Fields](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_concepts.htm "Object Reference for the Salesforce Platform: Overview of Salesforce Objects
         and Fields  - HTML (New Window)")
- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.262.0.api.meta/api/sforce_api_quickstart_intro.htm "SOAP API Developer Guide: Introduction to SOAP API - HTML (New Window)")
