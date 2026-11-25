---
page_id: billing-connectapi-enums
title: ConnectApi Enums
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-connectapi-enums.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-connect-api-namespace
legacy_page_id: billing_connectAPI_enums.htm
fetched_at: 2026-11-25
---

# ConnectApi Enums

Enums specific to the `ConnectApi` namespace.

`ConnectApi` enums inherit all properties and methods of Apex enums.

Enums are not versioned. Enum values are returned in all API versions.

| Enum | Description |
| --- | --- |
| `ConnectApi.InvoiceAction` | Type of invoice to be created. |
| `ConnectApi.TaxStrategyEnum` | Tax strategy to be applied across invoice lines. You can override the tax strategy at the individual invoice line level or at the tax line level. |
| `ConnectApi.CreditMemoTypeEnum` | Type of credit memo to be created. Valid values are `Posted` and `Draft`. Specify `Draft` as a value in your request to create draft credit memos. |
| `ConnectApi.StandaloneTaxStrategyEnum` | Specifies how tax lines must be created for the standalone credit memos. |
| `ConnectApi.SequenceResponseStatusEnum` | Status of the sequence policy assignment. |
| `ConnectApi.StatusEnum` | The status of sequence reconciliation API request. Valid values are `Submitted` or `NotSubmitted`. |

ConnectApi.InvoiceAction values:

- `Draft`

- `Posted`

ConnectApi.TaxStrategyEnum values:

- `Ignore`—Specifies that the creation of tax lines must be ignored.

- `ManualOverride`—Specifies that the provided tax values must be considered for taxes.

- `CopyFromInvoiceLine`—Specifies that tax values must be copied from the invoice line.

- `Calculate`—Specifies that tax must be calculated by using the API.

ConnectApi.StandaloneTaxStrategyEnum values:

- `Ignore`—Specifies that the creation of tax lines must be ignored.

- `Manual Override`—Specifies that the provided tax values must be considered for taxes.

- `Calculate`—Specifies that tax must be calculated by using the API.

ConnectApi.SequenceResponseStatusEnum values:

- `PartialSuccess`

- `Success`

- `Failed`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-connectapi-enums.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
