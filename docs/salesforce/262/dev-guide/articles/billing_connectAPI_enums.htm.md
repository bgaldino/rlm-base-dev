---
page_id: billing_connectAPI_enums.htm
title: ConnectApi Enums
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_connectAPI_enums.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_connect_api_namespace.htm
fetched_at: 2026-06-09
---

# ConnectApi Enums

Enums specific to the `ConnectApi`
namespace.

`ConnectApi` enums inherit all properties and methods
of Apex enums.

Enums are not versioned. Enum values are returned in all API
versions.

| Enum | Description |
| --- | --- |
| `ConnectApi.InvoiceAction` | Type of invoice to be created. Valid values are:   - `Draft` - `Posted` |
| `ConnectApi.TaxStrategyEnum` | Tax strategy to be applied across invoice lines. You can override the tax strategy at the individual invoice line level or at the tax line level. Valid values are:   - `Ignore`—Specifies that the   creation of tax lines must be ignored. - `ManualOverride`—Specifies that the provided tax values must be   considered for taxes. - `CopyFromInvoiceLine`—Specifies   that tax values must be copied from the invoice line. - `Calculate`—Specifies that tax   must be calculated by using the API. |
| `ConnectApi.CreditMemoTypeEnum` | Type of credit memo to be created. Valid values are `Posted` and `Draft`. Specify `Draft` as a value in your request to create draft credit memos. |
| `ConnectApi.StandaloneTaxStrategyEnum` | Specifies how tax lines must be created for the standalone credit memos. Valid values are:   - `Ignore`—Specifies that the   creation of tax lines must be ignored. - `Manual   Override`—Specifies that the provided tax values must be   considered for taxes. - `Calculate`—Specifies that tax   must be calculated by using the API. |
| `ConnectApi.SequenceResponseStatusEnum` | Status of the sequence policy assignment. Valid values are:   - `PartialSuccess` - `Success` - `Failed` |
| `ConnectApi.StatusEnum` | The status of sequence reconciliation API request. Valid values are:   - `Submitted` - `NotSubmitted` |
