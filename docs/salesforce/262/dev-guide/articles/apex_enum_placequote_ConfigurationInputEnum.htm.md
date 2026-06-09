---
page_id: apex_enum_placequote_ConfigurationInputEnum.htm
title: ConfigurationInputEnum Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_placequote_ConfigurationInputEnum.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_placequote.htm
fetched_at: 2026-06-09
---

# ConfigurationInputEnum Enum

Specifies the configuration input for the request to place a quote.

## Usage

Use these enum values for the `configurationInputEnum` property
in the [PlaceQuoteRLMApexProcessor](./apex_class_placequote_PlaceQuoteRLMApexProcessor.htm.md "Contains methods to place a quote with details of the graph request, pricing preferences, and configuration options.") class.

## Enum Values

The `placequote.ConfigurationInputEnum` enum has these
values.

| Value | Description |
| --- | --- |
| `RunAndAllowErrors` | Run the configuration and proceed with order ingestion upon encountering any configuration errors. |
| `RunAndBlockErrors` | Run the configuration and block order ingestion upon encountering any configuration errors. |
| `Skip` | Skip the configuration execution. |
