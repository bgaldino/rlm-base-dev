---
page_id: apex-enum-revsalestrxn-catalogratespreferenceenum
title: CatalogRatesPreferenceEnum Enum
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-enum-revsalestrxn-catalogratespreferenceenum.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-revsalestrxn
legacy_page_id: apex_enum_RevSalesTrxn_CatalogRatesPreferenceEnum.htm
fetched_at: 2026-11-25
---

# CatalogRatesPreferenceEnum Enum

Specifies the rate card entries defined in the catalog that must be fetched for quote line items, with usage-based selling during the place sales transaction process.

## Usage

This enum is available when [Usage Selling](https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_usage_sellling.htm) is enabled.

## Enum Values

The `RevSalesTrxn.CatalogRatesPreferenceEnum` enum includes these values.

| Value | Description |
| --- | --- |
| `Fetch` | Retrieves the rate card entries defined in the catalog for quote line items during the quote creation process. |
| `Skip` | Skips the retrieval of rate card entries for quote line items during the quote creation process. The default value is `Skip`. |

Example `Fetch`:

Example `Skip`:

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-enum-revsalestrxn-catalogratespreferenceenum.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
