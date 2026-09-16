---
page_id: apex_enum_RevSalesTrxn_CatalogRatesPreferenceEnum.htm
title: CatalogRatesPreferenceEnum Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_RevSalesTrxn_CatalogRatesPreferenceEnum.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_RevSalesTrxn.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# CatalogRatesPreferenceEnum Enum

Specifies the rate card entries defined in the catalog that must be fetched for quote
    line items, with usage-based selling during the place sales transaction process.

## Usage

This enum is available when [Usage Selling](https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_usage_sellling.htm&language=en_US) is enabled.

## Enum Values

The `RevSalesTrxn.CatalogRatesPreferenceEnum` enum includes
        these values.

| Value | Description |
| --- | --- |
| `Fetch` | Retrieves the rate card entries defined in the catalog for quote line items during the quote creation process. |
| `Skip` | Skips the retrieval of rate card entries for quote line items during the quote creation process. The default value is `Skip`. |
