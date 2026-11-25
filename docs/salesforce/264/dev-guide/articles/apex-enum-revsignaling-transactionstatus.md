---
page_id: apex-enum-revsignaling-transactionstatus
title: TransactionStatus Enum
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-enum-revsignaling-transactionstatus.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: apex-namespace-revsignaling
legacy_page_id: apex_enum_RevSignaling_TransactionStatus.htm
fetched_at: 2026-11-25
---

# TransactionStatus Enum

Specifies the status of the transaction request.

## Enum Values

The `RevSignaling.TransactionStatus` enum includes these values.

| Value | Description |
| --- | --- |
| `FAILED` | The transaction request has failed. |
| `SUCCESS` | The transaction request was successful. |

Example `FAILED`:

```
RevSignaling.TransactionStatus, FAILED
```

Example `SUCCESS`:

```
RevSignaling.TransactionStatus, SUCCESS
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-enum-revsignaling-transactionstatus.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
