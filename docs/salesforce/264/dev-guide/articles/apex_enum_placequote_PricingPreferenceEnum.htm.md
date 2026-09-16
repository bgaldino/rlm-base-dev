---
page_id: apex_enum_placequote_PricingPreferenceEnum.htm
title: PricingPreferenceEnum Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_placequote_PricingPreferenceEnum.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_placequote.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# PricingPreferenceEnum Enum

Specifies the pricing preference during the create quote process.

## Usage

Used by the [PlaceQuoteRLMApexProcessor](./apex_class_placequote_PlaceQuoteRLMApexProcessor.htm.md#apex_class_placequote_PlaceQuoteRLMApexProcessor) class.

## Enum Values

The `placequote.PricingPreferenceEnum` enum class includes these
        values.

| Value | Description |
| --- | --- |
| `Force` | Enforce pricing during the quote ingestion process. |
| `Skip` | Skip pricing during the quote ingestion process. |
| `System` | Determine whether a pricing calculation is required. |
