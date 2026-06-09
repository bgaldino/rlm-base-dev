---
page_id: apex_enum_placequote_PricingPreferenceEnum.htm
title: PricingPreferenceEnum Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_placequote_PricingPreferenceEnum.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_placequote.htm
fetched_at: 2026-06-09
---

# PricingPreferenceEnum Enum

Specifies the pricing preference during the create quote process.

## Usage

Used by the [PlaceQuoteRLMApexProcessor](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_placequote_PlaceQuoteRLMApexProcessor.htm "Contains methods to place a quote with details of the graph request, pricing preferences, and configuration options.") class.

## Enum Values

The `placequote.PricingPreferenceEnum` enum class includes these
values.

| Value | Description |
| --- | --- |
| `Force` | Enforce pricing during the quote ingestion process. |
| `Skip` | Skip pricing during the quote ingestion process. |
| `System` | Determine whether a pricing calculation is required. |
