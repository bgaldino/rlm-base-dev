---
page_id: quote-and-order-capture-standard-objects
title: Transaction Management Standard Objects
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/quote-and-order-capture-standard-objects.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-overview
legacy_page_id: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-11-25
---

# Transaction Management Standard Objects

The Transaction Management data model provides objects and fields to manage transactions.

These objects are documented in the [Salesforce Object Reference](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_list.htm).

- 

[Asset](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_asset.htm)

- 

[AssetAction](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_assetaction.htm)

- 

[AssetActionSource](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_assetactionsource.htm)

- 

[AssetContractRelationship](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_assetcontractrelationship.htm)

- 

[AssetDowntimePeriod](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_assetdowntimeperiod.htm)

- 

[AssetOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_assetownersharingrule.htm)

- 

[AssetRateAdjustment](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_assetrateadjustment.htm)

- 

[AssetRateCardEntry](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_assetratecardentry.htm)

- 

[AssetRelationship](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_assetrelationship.htm)

- 

[AssetShare](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_assetshare.htm)

- 

[AssetStatePeriod](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_assetstateperiod.htm)

- 

[AssetStatePeriodAttribute](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_assetstateperiodattribute.htm)

- 

[AssetTag](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_assettag.htm)

- 

[AssetTokenEvent](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_assettokenevent.htm)

- 

[AssetWarranty](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_assetwarranty.htm)

- 

[OrderDeliveryMethod](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_orderdeliverymethod.htm)

- 

[QuoteAction](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_quoteaction.htm)

- 

[QuoteItemTaxItem](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_quoteitemtaxitem.htm)

- 

**[AssetActionSrcPriceAdjustment](./sforce-api-objects-assetactionsrcpriceadjustment.md)**

Each row represents a junction between an asset and the calculated price adjustment that’s applied to an asset. This object is available in API version 66.0 and later.

- 

**[BindingObjUsageRsrcPlcy](./sforce-api-objects-bindingobjusagersrcplcy.md)**

Represents the policies that are used for the usage resource that’s associated with an asset or a binding object. This object is available in API version 65.0 and later.

- 

**[ContractItemPrice](./sforce-api-objects-contractitemprice.md)**

Represents an object that’s used to capture a price for a product on a contract. This object is available in API version 61.0 and later.

- 

**[ContractItemPriceAdjTier](./sforce-api-objects-contractitempriceadjtier.md)**

Represents the tiers of a price adjustment to a product on a contract. This object is available in API version 63.0 and later.

- 

**[ContractItemPriceHistory](./sforce-api-objects-contractitempricehistory.md)**

Represents the history of changes to the values in the fields of a ContractItemPrice object. This object is available in API version 61.0 and later.

- 

**[OrderItemAttribute](./sforce-api-objects-orderitemattribute.md)**

Represents a virtual object that stores an attribute specified for an order item.This object is available in API version 60.0 and later.

- 

**[OrderItemDetail](./sforce-api-objects-orderitemdetail.md)**

Represents the breakdown details of an order product. Revenue Management generates these records to capture pricing and quantity changes, such as negative quantity reductions, early renewals, derived pricing or repricing during an amendment, and bundle or product attribute reconfigurations. This object is available in API version 60.0 and later.

- 

**[OrderItemRateAdjustment](./sforce-api-objects-orderitemrateadjustment.md)**

Represents the negotiated rate adjustment for an order product. This object is available in API version 62.0 and later.

- 

**[OrderItemRateCardEntry](./sforce-api-objects-orderitemratecardentry.md)**

Represents the catalog and negotiated rates of a usage metric associated with an order item that’s used to charge overage consumption. This object is available in API version 62.0 and later.

- 

**[OrderItemUsageRsrcGrant](./sforce-api-objects-orderitemusagersrcgrant.md)**

Represents the negotiated grants for the usage resource that’s associated with the usage product added in the order item. This object is available in API version 65.0 and later.

- 

**[OrderItemUsageRsrcPlcy](./sforce-api-objects-orderitemusagersrcplcy.md)**

Represents the policies that are used for the usage resource that’s associated with the usage product added in the order item. This object is available in API version 65.0 and later.

- 

**[SalesTransactionType](./sforce-api-objects-salestransactiontype.md)**

Represents the type of the sales transaction. This object is available in API version 61.0 and later.

- 

**[QuoteLineDetail](./sforce-api-objects-quotelinedetail.md)**

Represents the breakdown details of a quote line item. Revenue Management generates these records to capture pricing and quantity changes, such as negative quantity reductions, early renewals, derived pricing or repricing during an amendment, and bundle or product attribute reconfigurations. This object is available in API version 60.0 and later.

- 

**[QuoteLineGroup](./sforce-api-objects-quotelinegroup.md)**

Stores the group information for line items in a quote. It also stores the aggregated line field information (subtotal). It contains a parent-child relationship to quote. This object is available in API version 61.0 and later.

- 

**[QuoteLineItemAttribute](./sforce-api-objects-quotelineitemattribute.md)**

Represents a virtual object that stores an attribute specified for a quote line item. This object is available in API version 59.0 and later.

- 

**[QuotLineItmUseRsrcGrant](./sforce-api-objects-quotlineitmusersrcgrant.md)**

Represents the negotiated grants for the usage resource that’s associated with the usage product added in the quote line item. This object is available in API version 65.0 and later.

- 

**[QuotLineItmUsageRsrcPlcy](./sforce-api-objects-quotlineitmusagersrcplcy.md)**

Represents the policies that are used for the usage resource that’s associated with the usage product added in the quote line item. This object is available in API version 65.0 and later.

- 

**[QuoteLineRateAdjustment](./sforce-api-objects-quotelinerateadjustment.md)**

Represents the negotiated rate adjustment for a quote line item. This object is available in API version 62.0 and later.

- 

**[QuoteLineRateCardEntry](./sforce-api-objects-quotelineratecardentry.md)**

Represents the catalog and negotiated rates of a usage resource associated with a quote line item that’s used to charge overage consumption. This object is available in API version 62.0 and later.

- 

**[QuoteToOpportunitySyncEvent](./sforce-api-objects-quotetoopportunitysyncevent.md)**

Represents an asynchronous quote to opportunity synchronization event. It tracks whether the sync succeeded or failed and notifies associated subscribers upon completion. This object is available in API version XX.0 and later.

**See Also**

- [*Object Reference for the platform*: Overview of Salesforce Objects and Fields](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_concepts.htm)

- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/sforce_api_quickstart_intro.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/quote-and-order-capture-standard-objects.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
