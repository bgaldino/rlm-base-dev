---
page_id: apex_enum_commerceorders_PricingPreferenceEnum.htm
title: PricingPreferenceEnum Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_commerceorders_PricingPreferenceEnum.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commerceorders.htm
fetched_at: 2026-06-09
---

# PricingPreferenceEnum Enum

Specifies the pricing preference during the create order process.

## Usage

Used by the [PlaceOrderExecutor](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commerceorders_PlaceOrderExecutor.htm "Contains methods to place an order with details of the graph request, pricing preferences, and configuration options.")
class.

## Enum Values

The `commerceorders.PricingPreferenceEnum` enum includes these
values.

| Value | Description |
| --- | --- |
| `Force` | Enforce pricing during the order ingestion process. |
| `Skip` | Skip pricing during the order ingestion process. |
| `System` | Determine whether a pricing calculation is required. |
