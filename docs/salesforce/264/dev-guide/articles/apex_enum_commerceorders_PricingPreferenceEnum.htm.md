---
page_id: apex_enum_commerceorders_PricingPreferenceEnum.htm
title: PricingPreferenceEnum Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_commerceorders_PricingPreferenceEnum.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commerceorders.htm
fetched_at: 2026-11-23
---

# PricingPreferenceEnum Enum

Specifies the pricing preference during the create order process.

## Usage

Used by the [PlaceOrderExecutor](./apex_class_commerceorders_PlaceOrderExecutor.htm.md#apex_class_commerceorders_PlaceOrderExecutor "Contains methods to place an order with details of the graph request, pricing preferences, and configuration options.") class.

## Enum Values

The `commerceorders.PricingPreferenceEnum` enum includes these values.

| Value | Description |
| --- | --- |
| `Force` | Enforce pricing during the order ingestion process. |
| `Skip` | Skip pricing during the order ingestion process. |
| `System` | Determine whether a pricing calculation is required. |

Example `Force`:

Example `Skip`:

Example `System`:

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_commerceorders_PricingPreferenceEnum.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
