---
page_id: apex-enum-revsalestrxn-pricingpreferenceenum
title: PricingPreferenceEnum Enum
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-enum-revsalestrxn-pricingpreferenceenum.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-revsalestrxn
legacy_page_id: apex_enum_RevSalesTrxn_PricingPreferenceEnum.htm
fetched_at: 2026-11-25
---

# PricingPreferenceEnum Enum

Specifies the pricing preference during the creation of a sales transaction.

## Usage

Used by the [PlaceSalesTransactionExecutor](./apex-class-revsalestrxn-placesalestransactionexecutor.md) class.

## Enum Values

The `RevSalesTrxn.PricingPreferenceEnum` enum includes these values.

| Value | Description |
| --- | --- |
| `Force` | Specifies to enforce pricing during the creation of sales transactions. |
| `Skip` | Specifies to skip pricing during the creation of sales transactions. |
| `System` | Specifies the system to determine whether a pricing calculation is required. The default value is `System`. |

Example `Force`:

Example `Skip`:

Example `System`:

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-enum-revsalestrxn-pricingpreferenceenum.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
