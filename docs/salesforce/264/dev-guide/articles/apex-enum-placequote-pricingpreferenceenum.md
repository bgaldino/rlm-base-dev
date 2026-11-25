---
page_id: apex-enum-placequote-pricingpreferenceenum
title: PricingPreferenceEnum Enum
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-enum-placequote-pricingpreferenceenum.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-placequote
legacy_page_id: apex_enum_placequote_PricingPreferenceEnum.htm
fetched_at: 2026-11-25
---

# PricingPreferenceEnum Enum

Specifies the pricing preference during the create quote process.

## Usage

Used by the [PlaceQuoteRLMApexProcessor](./apex-class-placequote-placequoterlmapexprocessor.md) class.

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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-enum-placequote-pricingpreferenceenum.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
