---
page_id: apex-class-renew-assets-summary-renewalopptydetail
title: RenewalOpptyDetail Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-renew-assets-summary-renewalopptydetail.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-renew-assets-summary
legacy_page_id: apex_class_renew_assets_summary_RenewalOpptyDetail.htm
fetched_at: 2026-11-25
---

# RenewalOpptyDetail Class

Contains asset details and renewal pricing information for creating renewal opportunities.

## Namespace

[renew_assets_summary](./apex-namespace-renew-assets-summary.md)

- 

**[RenewalOpptyDetail Constructors](#renewalopptydetail-constructors)**

Learn more about the constructors available with the RenewalOpptyDetail class.

- 

**[RenewalOpptyDetail Properties](#renewalopptydetail-properties)**

Learn more about the properties available with the RenewalOpptyDetail class.

## RenewalOpptyDetail Constructors

Learn more about the constructors available with the RenewalOpptyDetail class.

The `RenewalOpptyDetail` class includes these constructors.

- 

**[RenewalOpptyDetail(assetId, startDate, endDate, productId, account, priceBookId, priceBookEntryId, lastAssetActionSubtype, renewalPriceDetails, opportunityProductId, orderItem, rootAssetOpportunity, lastAssetAction, totalLineAmount)](#renewalopptydetailassetid-startdate-enddate-productid-account-pricebookid-pricebookentryid-lastassetactionsubtype-renewalpricedetails-opportunityproductid-orderitem-rootassetopportunity-lastassetaction-totallineamount)**

Initializes the RenewalOpptyDetail class that contains asset details and renewal pricing information.

### RenewalOpptyDetail(assetId, startDate, endDate, productId, account, priceBookId, priceBookEntryId, lastAssetActionSubtype, renewalPriceDetails, opportunityProductId, orderItem, rootAssetOpportunity, lastAssetAction, totalLineAmount)

Initializes the RenewalOpptyDetail class that contains asset details and renewal pricing information.

#### Signature

`public RenewalOpptyDetail(String assetId, Date startDate, Date endDate, String productId, String account, String priceBookId, String priceBookEntryId, String lastAssetActionSubtype, List<renew_assets_summary.RenewalPriceDetail> renewalPriceDetails, String opportunityProductId, String orderItem, String rootAssetOpportunity, String lastAssetAction, Decimal totalLineAmount)`

#### Parameters

***assetId***

Type: String

The ID of the asset.

***startDate***

Type: Date

The start date of the asset.

***endDate***

Type: Date

The end date of the asset.

***productId***

Type: String

The ID of the product associated with the asset.

***account***

Type: String

The ID of the account.

***priceBookId***

Type: String

The ID of the price book.

***priceBookEntryId***

Type: String

The ID of the price book entry.

***lastAssetActionSubtype***

Type: String

The subtype of the last action performed on the asset. Valid value is `Start Date Adjustment`.

***renewalPriceDetails***

Type: List<[renew_assets_summary.RenewalPriceDetail](./apex-class-renew-assets-summary-renewalpricedetail.md#renewalpricedetail-class)>

List of renewal price details for the asset.

***opportunityProductId***

Type: String

The ID of the associated opportunity product.

***orderItem***

Type: String

The ID of the associated order item.

***rootAssetOpportunity***

Type: String

The ID of the root asset opportunity.

***lastAssetAction***

Type: String

The last action performed on the asset.

- `Initial Sale`

- `Upsell`

- `Downsell`

- `Renewal`

- `Cancellation`

***totalLineAmount***

Type: Decimal

The total line amount for the asset.

## RenewalOpptyDetail Properties

Learn more about the properties available with the RenewalOpptyDetail class.

The `RenewalOpptyDetail` class includes these properties.

- 

**[account](#account)**

Get or set the ID of the account.

- 

**[assetId](#assetid)**

Get or set the ID of the asset.

- 

**[endDate](#enddate)**

Get or set the end date of the asset.

- 

**[lastAssetAction](#lastassetaction)**

Get or set the last action performed on the asset.

- 

**[lastAssetActionSubtype](#lastassetactionsubtype)**

Get or set the subtype of the last action performed on the asset.

- 

**[opportunityProductId](#opportunityproductid)**

Get or set the ID of the associated opportunity product.

- 

**[orderItem](#orderitem)**

Get or set the ID of the associated order item.

- 

**[priceBookEntryId](#pricebookentryid)**

Get or set the ID of the price book entry.

- 

**[priceBookId](#pricebookid)**

Get or set the ID of the price book.

- 

**[productId](#productid)**

Get or set the ID of the product associated with the asset.

- 

**[renewalPriceDetails](#renewalpricedetails)**

Get or set the list of renewal price details for the asset.

- 

**[rootAssetOpportunity](#rootassetopportunity)**

Get or set the ID of the root asset opportunity.

- 

**[startDate](#startdate)**

Get or set the start date of the asset.

- 

**[totalLineAmount](#totallineamount)**

Get or set the total line amount for the asset.

### account

Get or set the ID of the account.

#### Signature

`public String account {get; set;}`

#### Property Value

Type: String

### assetId

Get or set the ID of the asset.

#### Signature

`public String assetId {get; set;}`

#### Property Value

Type: String

### endDate

Get or set the end date of the asset.

#### Signature

`public Date endDate {get; set;}`

#### Property Value

Type: Date

### lastAssetAction

Get or set the last action performed on the asset.

#### Signature

`public String lastAssetAction {get; set;}`

#### Property Value

Type: String

Valid values are:

- `Initial Sale`

- `Upsell`

- `Downsell`

- `Renewal`

- `Cancellation`

### lastAssetActionSubtype

Get or set the subtype of the last action performed on the asset.

#### Signature

`public String lastAssetActionSubtype {get; set;}`

#### Property Value

Type: String

Valid value is `Start Date Adjustment`.

### opportunityProductId

Get or set the ID of the associated opportunity product.

#### Signature

`public String opportunityProductId {get; set;}`

#### Property Value

Type: String

### orderItem

Get or set the ID of the associated order item.

#### Signature

`public String orderItem {get; set;}`

#### Property Value

Type: String

### priceBookEntryId

Get or set the ID of the price book entry.

#### Signature

`public String priceBookEntryId {get; set;}`

#### Property Value

Type: String

### priceBookId

Get or set the ID of the price book.

#### Signature

`public String priceBookId {get; set;}`

#### Property Value

Type: String

### productId

Get or set the ID of the product associated with the asset.

#### Signature

`public String productId {get; set;}`

#### Property Value

Type: String

### renewalPriceDetails

Get or set the list of renewal price details for the asset.

#### Signature

`public List<renew_assets_summary.RenewalPriceDetail> renewalPriceDetails {get; set;}`

#### Property Value

Type: List<[renew_assets_summary.RenewalPriceDetail](./apex-class-renew-assets-summary-renewalpricedetail.md#renewalpricedetail-class)>

### rootAssetOpportunity

Get or set the ID of the root asset opportunity.

#### Signature

`public String rootAssetOpportunity {get; set;}`

#### Property Value

Type: String

### startDate

Get or set the start date of the asset.

#### Signature

`public Date startDate {get; set;}`

#### Property Value

Type: Date

### totalLineAmount

Get or set the total line amount for the asset.

#### Signature

`public Decimal totalLineAmount {get; set;}`

#### Property Value

Type: Decimal

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-renew-assets-summary-renewalopptydetail.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
