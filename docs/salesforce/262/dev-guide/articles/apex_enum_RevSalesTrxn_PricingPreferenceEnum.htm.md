---
page_id: apex_enum_RevSalesTrxn_PricingPreferenceEnum.htm
title: PricingPreferenceEnum Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_RevSalesTrxn_PricingPreferenceEnum.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_RevSalesTrxn.htm
fetched_at: 2026-06-09
---

# PricingPreferenceEnum Enum

Specifies the pricing preference during the creation of a sales transaction.

## Usage

Used by the [PlaceSalesTransactionExecutor](./apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor.htm.md#apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor "Contains methods to place a sales transaction with details of the graph request, pricing preferences, and configuration options.") class.

## Enum Values

The `RevSalesTrxn.PricingPreferenceEnum` enum includes these
values.

| Value | Description |
| --- | --- |
| `Force` | Specifies to enforce pricing during the creation of sales transactions. |
| `Skip` | Specifies to skip pricing during the creation of sales transactions. |
| `System` | Specifies the system to determine whether a pricing calculation is required. The default value is `System`. |
