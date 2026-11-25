---
page_id: apex-enum-revsalestrxn-persistpreferenceenum
title: PersistPreferenceEnum Enum
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-enum-revsalestrxn-persistpreferenceenum.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-revsalestrxn
legacy_page_id: apex_enum_RevSalesTrxn_PersistPreferenceEnum.htm
fetched_at: 2026-11-25
---

# PersistPreferenceEnum Enum

Specifies whether to persist pricing changes for each sales transaction record. Available in API version 65.0 and later.

## Enum Values

The `RevSalesTrxn.PersistPreferenceEnum` enum includes this value.

| Value | Description |
| --- | --- |
| `Skip` | Skips the persistence of pricing changes for each sales transaction record. To persist pricing changes, specify `null` as the value in the method signature. If this value isn’t specified, then request to persist pricing changes is performed by default. |

Example `Skip`:

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-enum-revsalestrxn-persistpreferenceenum.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
