---
page_id: apex_enum_RevSalesTrxn_PricingPreferenceEnum.htm
title: PricingPreferenceEnum Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_RevSalesTrxn_PricingPreferenceEnum.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_RevSalesTrxn.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# PricingPreferenceEnum Enum

Specifies the pricing preference during the creation of a sales transaction.

## Usage

      

Used by the [PlaceSalesTransactionExecutor](./apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor.htm.md#apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor) class.

## Enum Values

The `RevSalesTrxn.PricingPreferenceEnum` enum includes these
        values.

| Value | Description |
| --- | --- |
| `Force` | Specifies to enforce pricing during the creation of sales transactions. |
| `Skip` | Specifies to skip pricing during the creation of sales transactions. |
| `System` | Specifies the system to determine whether a pricing calculation is required. The default value is `System`. |
