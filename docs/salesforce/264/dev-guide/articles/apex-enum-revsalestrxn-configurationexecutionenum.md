---
page_id: apex-enum-revsalestrxn-configurationexecutionenum
title: ConfigurationExecutionEnum Enum
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-enum-revsalestrxn-configurationexecutionenum.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-revsalestrxn
legacy_page_id: apex_enum_RevSalesTrxn_ConfigurationExecutionEnum.htm
fetched_at: 2026-11-25
---

# ConfigurationExecutionEnum Enum

Specifies the configuration method for the place sales transaction request.

## Usage

Use these enum values for the `configurationExecutionEnum` property in the [PlaceSalesTransactionExecutor](./apex-class-revsalestrxn-placesalestransactionexecutor.md) class.

## Enum Values

The `RevSalesTrxn.ConfigurationExecutionEnum` enum has these values.

| Value | Description |
| --- | --- |
| `Force` | Specifies to enforce the predefined configuration process during the sales transaction process. |
| `Skip` | Specifies to skip the configuration process during the quote creation process. The default value is `Skip`. |
| `System` | Specifies the system to determine whether the configuration process is required. |

Example `Force`:

Example `Skip`:

Example `System`:

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-enum-revsalestrxn-configurationexecutionenum.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
