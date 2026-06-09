---
page_id: apex_enum_commerceorders_CatalogRatesPreferenceEnum.htm
title: CatalogRatesPreferenceEnum Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_commerceorders_CatalogRatesPreferenceEnum.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commerceorders.htm
fetched_at: 2026-06-09
---

# CatalogRatesPreferenceEnum Enum

Specifies the rate card entries defined in the catalog that must be fetched for order
items, with usage-based selling during the order creation process.

## Usage

This enum is available when the Usage-Based Selling feature is enabled.

## Enum Values

The `commerceorders.CatalogRatesPreferenceEnum` enum includes
these values.

| Value | Description |
| --- | --- |
| `Fetch` | Retrieves the rate card entries defined in the catalog for order items during the order creation process. |
| `Skip` | Skips the retrieval of rate card entries for order items during the order creation process. The default value is `Skip`. |
