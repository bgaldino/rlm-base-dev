---
page_id: apex_enum_placequote_ConfigurationInputEnum.htm
title: ConfigurationInputEnum Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_placequote_ConfigurationInputEnum.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_placequote.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConfigurationInputEnum Enum

Specifies the configuration input for the request to place a quote.

## Usage

Use these enum values for the `configurationInputEnum` property
        in the [PlaceQuoteRLMApexProcessor](./apex_class_placequote_PlaceQuoteRLMApexProcessor.htm.md#apex_class_placequote_PlaceQuoteRLMApexProcessor) class.

## Enum Values

The `placequote.ConfigurationInputEnum` enum has these
        values.

| Value | Description |
| --- | --- |
| `RunAndAllowErrors` | Run the configuration and proceed with order ingestion upon encountering any configuration errors. |
| `RunAndBlockErrors` | Run the configuration and block order ingestion upon encountering any configuration errors. |
| `Skip` | Skip the configuration execution. |
