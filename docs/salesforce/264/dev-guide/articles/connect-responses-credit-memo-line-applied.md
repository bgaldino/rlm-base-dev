---
page_id: connect-responses-credit-memo-line-applied
title: Credit Memo Line Applied
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-credit-memo-line-applied.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_credit_memo_line_applied.htm
fetched_at: 2026-11-25
---

# Credit Memo Line Applied

Output representation of the list of applied credit memo line results.

## JSON Example

```
  {
  "appliedCreditResponses": [
   {
    "creditMemoLineInvoiceLineId": "4sGSG0000002pMb2AI",
    "errors": null,
    "invoiceLineId": "5TVSG0000003CuH4AU",
    "success": true
   }
  ]
 }
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `applied​CreditResponses` | [Credit Memo Line Applied Response](./connect-responses-credit-memo-line-applied-response.md)[] | Output list for the applied credit memo line results. | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-credit-memo-line-applied.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
