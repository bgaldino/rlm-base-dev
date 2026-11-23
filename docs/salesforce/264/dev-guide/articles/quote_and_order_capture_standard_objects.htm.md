---
page_id: quote_and_order_capture_standard_objects.htm
title: Transaction Management Standard Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_standard_objects.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_overview.htm
fetched_at: 2026-11-23
---

# Transaction Management Standard Objects

The Transaction Management data model provides objects and fields to manage
transactions.

These objects are documented in the [Salesforce Object Reference](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_list.htm).

- [Asset](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_asset.htm "HTML (New Window)")
- [AssetAction](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_assetaction.htm "HTML (New Window)")
- [AssetActionSource](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_assetactionsource.htm "HTML (New Window)")
- [AssetContractRelationship](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_assetcontractrelationship.htm "HTML (New Window)")
- [AssetDowntimePeriod](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_assetdowntimeperiod.htm "HTML (New Window)")
- [AssetOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_assetownersharingrule.htm "HTML (New Window)")
- [AssetRateAdjustment](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_assetrateadjustment.htm "HTML (New Window)")
- [AssetRateCardEntry](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_assetratecardentry.htm "HTML (New Window)")
- [AssetRelationship](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_assetrelationship.htm "HTML (New Window)")
- [AssetShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_assetshare.htm "HTML (New Window)")
- [AssetStatePeriod](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_assetstateperiod.htm "HTML (New Window)")
- [AssetStatePeriodAttribute](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_assetstateperiodattribute.htm "HTML (New Window)")
- [AssetTag](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_assettag.htm "HTML (New Window)")
- [AssetTokenEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_assettokenevent.htm "HTML (New Window)")
- [AssetWarranty](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_assetwarranty.htm "HTML (New Window)")
- [OrderDeliveryMethod](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_orderdeliverymethod.htm "HTML (New Window)")
- [QuoteAction](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_quoteaction.htm "HTML (New Window)")
- [QuoteItemTaxItem](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_quoteitemtaxitem.htm "HTML (New Window)")

- **[AssetActionSrcPriceAdjustment](./sforce_api_objects_assetactionsrcpriceadjustment.htm.md)**  
  Each row represents a junction between an asset and the calculated price adjustment that's applied to an asset. This object is available in API version 66.0 and later.
- **[BindingObjUsageRsrcPlcy](./sforce_api_objects_bindingobjusagersrcplcy.htm.md)**  
  Represents the policies that are used for the usage resource that's associated with an asset or a binding object. This object is available in API version 65.0 and later.
- **[ContractItemPrice](./sforce_api_objects_contractitemprice.htm.md)**  
  Represents an object that’s used to capture a price for a product on a contract. This object is available in API version 61.0 and later.
- **[ContractItemPriceAdjTier](./sforce_api_objects_contractitempriceadjtier.htm.md)**  
  Represents the tiers of a price adjustment to a product on a contract. This object is available in API version 63.0 and later.
- **[ContractItemPriceHistory](./sforce_api_objects_contractitempricehistory.htm.md)**  
  Represents the history of changes to the values in the fields of a ContractItemPrice object. This object is available in API version 61.0 and later.
- **[OrderItemAttribute](./sforce_api_objects_orderitemattribute.htm.md)**  
  Represents a virtual object that stores an attribute specified for an order item.This object is available in API version 60.0 and later.
- **[OrderItemDetail](./sforce_api_objects_orderitemdetail.htm.md)**  
  Represents the breakdown details of an order product. Revenue Management generates these records to capture pricing and quantity changes, such as negative quantity reductions, early renewals, derived pricing or repricing during an amendment, and bundle or product attribute reconfigurations. This object is available in API version 60.0 and later.
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
- **[QuoteLineDetail](./sforce_api_objects_quotelinedetail.htm.md)**  
  Represents the breakdown details of a quote line item. Revenue Management generates these records to capture pricing and quantity changes, such as negative quantity reductions, early renewals, derived pricing or repricing during an amendment, and bundle or product attribute reconfigurations. This object is available in API version 60.0 and later.
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
- **[QuoteToOpportunitySyncEvent](./sforce_api_objects_quotetoopportunitysyncevent.htm.md)**  
  Represents an asynchronous quote to opportunity synchronization event. It tracks whether the sync succeeded or failed and notifies associated subscribers upon completion. This object is available in API version XX.0 and later.

#### See Also

- [*Object Reference for the platform*: Overview of Salesforce Objects
  and Fields](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_concepts.htm "Object Reference for the platform: Overview of Salesforce Objects
         and Fields  - HTML (New Window)")
- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.264.0.api.meta/api/sforce_api_quickstart_intro.htm "SOAP API Developer Guide: Introduction to SOAP API - HTML (New Window)")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_standard_objects.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
