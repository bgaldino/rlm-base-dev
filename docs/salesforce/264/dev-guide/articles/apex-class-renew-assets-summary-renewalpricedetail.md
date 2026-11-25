---
page_id: apex-class-renew-assets-summary-renewalpricedetail
title: RenewalPriceDetail Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-renew-assets-summary-renewalpricedetail.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-renew-assets-summary
legacy_page_id: apex_class_renew_assets_summary_RenewalPriceDetail.htm
fetched_at: 2026-11-25
---

# RenewalPriceDetail Class

Contains net unit price and quantity details for an asset to set as sales price for renewal opportunities.

## Namespace

[renew_assets_summary](./apex-namespace-renew-assets-summary.md)

- 

**[RenewalPriceDetail Constructors](#renewalpricedetail-constructors)**

Learn more about the constructors available with the RenewalPriceDetail class.

- 

**[RenewalPriceDetail Properties](#renewalpricedetail-properties)**

Learn more about the properties available with the RenewalPriceDetail class.

## RenewalPriceDetail Constructors

Learn more about the constructors available with the RenewalPriceDetail class.

The `RenewalPriceDetail` class includes these constructors.

- 

**[RenewalPriceDetail(netUnitPrice, quantity)](#renewalpricedetailnetunitprice-quantity)**

Initializes the RenewalPriceDetail class that contains net unit price and quantity information.

### RenewalPriceDetail(netUnitPrice, quantity)

Initializes the RenewalPriceDetail class that contains net unit price and quantity information.

#### Signature

`public RenewalPriceDetail(Decimal netUnitPrice, Decimal quantity)`

#### Parameters

***netUnitPrice***

Type: Decimal

The net unit price of the asset.

***quantity***

Type: Decimal

The quantity of the asset.

## RenewalPriceDetail Properties

Learn more about the properties available with the RenewalPriceDetail class.

The `RenewalPriceDetail` class includes these properties.

- 

**[netUnitPrice](#netunitprice)**

Get or set the net unit price of the asset.

- 

**[quantity](#quantity)**

Get or set the quantity of the asset.

### netUnitPrice

Get or set the net unit price of the asset.

#### Signature

`public Decimal netUnitPrice {get; set;}`

#### Property Value

Type: Decimal

### quantity

Get or set the quantity of the asset.

#### Signature

`public Decimal quantity {get; set;}`

#### Property Value

Type: Decimal

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-renew-assets-summary-renewalpricedetail.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
