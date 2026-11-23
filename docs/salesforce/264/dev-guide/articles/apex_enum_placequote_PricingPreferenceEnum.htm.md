---
page_id: apex_enum_placequote_PricingPreferenceEnum.htm
title: PricingPreferenceEnum Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_placequote_PricingPreferenceEnum.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_placequote.htm
fetched_at: 2026-11-23
---

# PricingPreferenceEnum Enum

Specifies the pricing preference during the create quote process.

## Usage

Used by the [PlaceQuoteRLMApexProcessor](./apex_class_placequote_PlaceQuoteRLMApexProcessor.htm.md#apex_class_placequote_PlaceQuoteRLMApexProcessor "Contains methods to place a quote with details of the graph request, pricing preferences, and configuration options.") class.

## Enum Values

The `placequote.PricingPreferenceEnum` enum class includes these values.

| Value | Description |
| --- | --- |
| `Force` | Enforce pricing during the quote ingestion process. |
| `Skip` | Skip pricing during the quote ingestion process. |
| `System` | Determine whether a pricing calculation is required. |

Example `Force`:

Example `Skip`:

Example `System`:

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_placequote_PricingPreferenceEnum.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
