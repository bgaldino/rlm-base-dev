---
page_id: quote_and_order_capture_standard_objects.htm
title: Transaction Management Standard Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_standard_objects.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_overview.htm
fetched_at: 2026-06-09
---

# Transaction Management Standard Objects

The Transaction Management data model provides objects and fields to manage
transactions.

- **[Asset](./sforce_api_objects_asset.htm.md)**  
  Represents an item of commercial value, such as a product sold by your company or a competitor, that a customer has purchased.
- **[AssetAction](./sforce_api_objects_assetaction.htm.md)**  
  Represents a change made to a lifecycle-managed asset. The fields can’t be edited. This object is available in API version 50.0 and later.
- **[AssetActionSource](./sforce_api_objects_assetactionsource.htm.md)**  
  Represents an optional way to record what transactions caused changes to lifecycle-managed assets. Use it to trace financial and other information about asset actions. This object supports Salesforce order products and work order line items, and transaction IDs from other systems. The fields can’t be edited. This object is available in API version 50.0 and later.
- **[AssetActionSrcPriceAdjustment](./sforce_api_objects_assetactionsrcpriceadjustment.htm.md)**  
  Each row represents a junction between an asset and the calculated price adjustment that's applied to an asset. This object is available in API version 66.0 and later.
- **[AssetContractRelationship](./sforce_api_objects_assetcontractrelationship.htm.md)**  
  Represents a relationship between an asset and a contract. This object is available in API version 60.0 and later.
- **[AssetDowntimePeriod](./sforce_api_objects_assetdowntimeperiod.htm.md)**  
  Represents a period during which an asset is not able to perform as expected. Downtime periods include planned activities, such as maintenance, and unplanned events, such as mechanical breakdown. This object is available in API version 49.0 and later.
- **[AssetOwnerSharingRule](./sforce_api_objects_assetownersharingrule.htm.md)**  
  Represents the rules for sharing an Asset with users other than the owner. This object is available in API version 33.0 and later.
- **[AssetRateAdjustment](./sforce_api_objects_assetrateadjustment.htm.md)**  
  Stores the tier rate adjustments for the asset rate card entries.This object is available in API version 62.0 and later.
- **[AssetRateCardEntry](./sforce_api_objects_assetratecardentry.htm.md)**  
  Stores the negotiated rate card entries that are associated with an asset in Revenue Cloud. This object is available in API version 62.0 and later.
- **[AssetRelationship](./sforce_api_objects_assetrelationship.htm.md)**  
  Represents a non-hierarchical relationship between assets due to an asset modification; for example, a replacement, upgrade, or other circumstance. In Revenue Lifecycle Management, this object represents an asset or assets grouped in a bundle or set. This object is available in API version 41.0 and later.
- **[AssetShare](./sforce_api_objects_assetshare.htm.md)**  
  Represents a sharing entry on an Asset. This object is available in API version 33.0 and later.
- **[AssetStatePeriod](./sforce_api_objects_assetstateperiod.htm.md)**  
  Represents a time span when an asset has the same quantity, amount, and monthly recurring revenue (MRR). An asset has as many asset state periods as there are changes to it (asset actions) during its lifecycle. The dashboard and related pages show the current asset state period. The fields can’t be edited. This object is available in API version 50.0 and later.
- **[AssetStatePeriodAttribute](./sforce_api_objects_assetstateperiodattribute.htm.md)**  
  Represents a virtual object that holds the key-value pair of the asset attribute in a specified asset state period. This object is a child object of AssetStatePeriod. This object is available in API version 60.0 and later.
- **[AssetTag](./sforce_api_objects_assettag.htm.md)**  
  Associates a word or short phrase with an Asset.
- **[AssetTokenEvent](./sforce_api_objects_assettokenevent.htm.md)**  
  The documentation has moved to [AssetTokenEvent](https://developer.salesforce.com/docs/atlas.en-us.262.0.platform_events.meta/platform_events/sforce_api_objects_assettokenevent.htm "HTML (New Window)") in the Platform Events Developer Guide.
- **[AssetWarranty](./sforce_api_objects_assetwarranty.htm.md)**  
  Defines the warranty terms applicable to an asset along with any exclusions and extensions. This object is available in API version 50.0 and later.
- **[BindingObjUsageRsrcPlcy](./sforce_api_objects_bindingobjusagersrcplcy.htm.md)**  
  Represents the policies that are used for the usage resource that's associated with an asset or a binding object. This object is available in API version 65.0 and later.
- **[ContractItemPrice](./sforce_api_objects_contractitemprice.htm.md)**  
  Represents an object that’s used to capture a price for a product on a contract. This object is available in API version 61.0 and later.
- **[ContractItemPriceAdjTier](./sforce_api_objects_contractitempriceadjtier.htm.md)**  
  Represents the tiers of a price adjustment to a product on a contract. This object is available in API version 63.0 and later.
- **[ContractItemPriceHistory](./sforce_api_objects_contractitempricehistory.htm.md)**  
  Represents the history of changes to the values in the fields of a ContractItemPrice object. This object is available in API version 61.0 and later.
- **[OrderDeliveryMethod](./sforce_api_objects_orderdeliverymethod.htm.md)**  
  Shows the customizations and options that a buyer selected for their delivery method. This object is available in API version 48.0 and later.
- **[OrderItemAttribute](./sforce_api_objects_orderitemattribute.htm.md)**  
  Represents a virtual object that stores an attribute specified for an order item.This object is available in API version 60.0 and later.
- **[OrderItemDetail](./sforce_api_objects_orderitemdetail.htm.md)**  
  Represents the breakdown details of an order product. Revenue Cloud generates these records to capture pricing and quantity changes, such as negative quantity reductions, early renewals, derived pricing or repricing during an amendment, and bundle or product attribute reconfigurations. This object is available in API version 60.0 and later.
- **[OrderItemRateAdjustment](./sforce_api_objects_orderitemrateadjustment.htm.md)**  
  Represents the negotiated rate adjustment for an order product. This object is available in API version 62.0 and later.
- **[OrderItemRateCardEntry](./sforce_api_objects_orderitemratecardentry.htm.md)**  
  Represents the catalog and negotiated rates of a usage metric associated with an order item that's used to charge overage consumption. This object is available in API version 62.0 and later.
- **[OrderItemUsageRsrcGrant](./sforce_api_objects_orderitemusagersrcgrant.htm.md)**  
  Represents the negotiated grants for the usage resource that's associated with the usage product added in the order item. This object is available in API version 65.0 and later.
- **[OrderItemUsageRsrcPlcy](./sforce_api_objects_orderitemusagersrcplcy.htm.md)**  
  Represents the policies that are used for the usage resource that's associated with the usage product added in the order item. This object is available in API version 65.0 and later.
- **[SalesTransactionType](./sforce_api_objects_salestransactiontype.htm.md)**  
  Represents the type of the sales transaction. This object is available in API version 61.0 and later.
- **[QuoteAction](./sforce_api_objects_quoteaction.htm.md)**  
  Indicates the type of sales transaction that’s being quoted; for example, a renewal sale. This object is available in API version 59.0 and later.
- **[QuoteItemTaxItem](./sforce_api_objects_quoteitemtaxitem.htm.md)**  
  The tax that is applied to a quote line item. This object is available in API version 55.0 and later.
- **[QuoteLineDetail](./sforce_api_objects_quotelinedetail.htm.md)**  
  Represents the breakdown details of a quote line item. Revenue Cloud generates these records to capture pricing and quantity changes, such as negative quantity reductions, early renewals, derived pricing or repricing during an amendment, and bundle or product attribute reconfigurations. This object is available in API version 60.0 and later.
- **[QuoteLineGroup](./sforce_api_objects_quotelinegroup.htm.md)**  
  Stores the group information for line items in a quote. It also stores the aggregated line field information (subtotal). It contains a parent-child relationship to quote. This object is available in API version 61.0 and later.
- **[QuoteLineItemAttribute](./sforce_api_objects_quotelineitemattribute.htm.md)**  
  Represents a virtual object that stores an attribute specified for a quote line item. This object is available in API version 59.0 and later.
- **[QuotLineItmUseRsrcGrant](./sforce_api_objects_quotlineitmusersrcgrant.htm.md)**  
  Represents the negotiated grants for the usage resource that's associated with the usage product added in the quote line item. This object is available in API version 65.0 and later.
- **[QuotLineItmUsageRsrcPlcy](./sforce_api_objects_quotlineitmusagersrcplcy.htm.md)**  
  Represents the policies that are used for the usage resource that's associated with the usage product added in the quote line item. This object is available in API version 65.0 and later.
- **[QuoteLineRateAdjustment](./sforce_api_objects_quotelinerateadjustment.htm.md)**  
  Represents the negotiated rate adjustment for a quote line item. This object is available in API version 62.0 and later.
- **[QuoteLineRateCardEntry](./sforce_api_objects_quotelineratecardentry.htm.md)**  
  Represents the catalog and negotiated rates of a usage resource associated with a quote line item that's used to charge overage consumption. This object is available in API version 62.0 and later.

#### See Also

- [*Object Reference for the Salesforce Platform*: Overview of Salesforce Objects
  and Fields](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_concepts.htm "Object Reference for the Salesforce Platform: Overview of Salesforce Objects
         and Fields  - HTML (New Window)")
- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.262.0.api.meta/api/sforce_api_quickstart_intro.htm "SOAP API Developer Guide: Introduction to SOAP API - HTML (New Window)")
