---
page_id: apex_class_renew_assets_summary_RenewalPriceDetail.htm
title: RenewalPriceDetail Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_renew_assets_summary_RenewalPriceDetail.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_renew_assets_summary.htm
fetched_at: 2026-06-09
---

# RenewalPriceDetail Class

Contains net unit price and quantity details for an asset to set as sales price for renewal opportunities.

## Namespace

[renew\_assets\_summary](./apex_namespace_renew_assets_summary.htm.md "Retrieve details about renewable assets to create renewal opportunities.")

- **[RenewalPriceDetail Constructors](./apex_class_renew_assets_summary_RenewalPriceDetail.htm.md#apex_renew_assets_summary_RenewalPriceDetail_constructors)**  
  Learn more about the constructors available with the RenewalPriceDetail class.
- **[RenewalPriceDetail Properties](./apex_class_renew_assets_summary_RenewalPriceDetail.htm.md#apex_renew_assets_summary_RenewalPriceDetail_properties)**  
  Learn more about the properties available with the RenewalPriceDetail class.

## RenewalPriceDetail Constructors

Learn more about the constructors available with the RenewalPriceDetail
class.

The `RenewalPriceDetail` class includes these
constructors.

- **[RenewalPriceDetail(netUnitPrice, quantity)](./apex_class_renew_assets_summary_RenewalPriceDetail.htm.md#apex_renew_assets_summary_RenewalPriceDetail_ctor)**  
  Initializes the RenewalPriceDetail class that contains net unit price and quantity information.

### RenewalPriceDetail(netUnitPrice, quantity)

Initializes the RenewalPriceDetail class that contains net unit price and quantity information.

#### Signature

`public RenewalPriceDetail(Decimal netUnitPrice, Decimal quantity)`

```
renew_assets_summary.RenewalPriceDetail, newinstance, [Decimal, Decimal], renew_assets_summary.RenewalPriceDetail
```

#### Parameters

netUnitPrice
:   Type: Decimal
:   The net unit price of the asset.

quantity
:   Type: Decimal
:   The quantity of the asset.

## RenewalPriceDetail Properties

Learn more about the properties available with the RenewalPriceDetail
class.

The `RenewalPriceDetail` class includes these
properties.

- **[netUnitPrice](./apex_class_renew_assets_summary_RenewalPriceDetail.htm.md#apex_renew_assets_summary_RenewalPriceDetail_netUnitPrice)**  
  Get or set the net unit price of the asset.
- **[quantity](./apex_class_renew_assets_summary_RenewalPriceDetail.htm.md#apex_renew_assets_summary_RenewalPriceDetail_quantity)**  
  Get or set the quantity of the asset.

### netUnitPrice

Get or set the net unit price of the asset.

#### Signature

`public Decimal netUnitPrice {get; set;}`

```
renew_assets_summary.RenewalPriceDetail, netUnitPrice
```

#### Property Value

Type: Decimal

### quantity

Get or set the quantity of the asset.

#### Signature

`public Decimal quantity {get; set;}`

```
renew_assets_summary.RenewalPriceDetail, quantity
```

#### Property Value

Type: Decimal
