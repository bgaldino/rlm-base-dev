---
page_id: apex-enum-placequote-configurationinputenum
title: ConfigurationInputEnum Enum
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-enum-placequote-configurationinputenum.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-placequote
legacy_page_id: apex_enum_placequote_ConfigurationInputEnum.htm
fetched_at: 2026-11-25
---

# ConfigurationInputEnum Enum

Specifies the configuration input for the request to place a quote.

## Usage

Use these enum values for the `configurationInputEnum` property in the [PlaceQuoteRLMApexProcessor](./apex-class-placequote-placequoterlmapexprocessor.md) class.

## Enum Values

The `placequote.ConfigurationInputEnum` enum has these values.

| Value | Description |
| --- | --- |
| `RunAndAllowErrors` | Run the configuration and proceed with order ingestion upon encountering any configuration errors. |
| `RunAndBlockErrors` | Run the configuration and block order ingestion upon encountering any configuration errors. |
| `Skip` | Skip the configuration execution. |

Example `RunAndAllowErrors`:

Example `RunAndBlockErrors`:

Example `Skip`:

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-enum-placequote-configurationinputenum.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
