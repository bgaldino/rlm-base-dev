---
page_id: connect-responses-credit-memo-line-unapplied
title: Credit Memo Line Unapplied
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-credit-memo-line-unapplied.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_credit_memo_line_unapplied.htm
fetched_at: 2026-11-25
---

# Credit Memo Line Unapplied

Output representation of the details of the credit memo line invoice line record with the status of the request.

## JSON Example

```
  {
  "creditMemoLineInvoiceLineId": "4sGSG0000002pOD2AY",
  "errors": [],
  "success": true
 }
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `creditMemo​LineInvoice​LineId` | String | ID of the credit memo line invoice line record. | Small, 62.0 | 62.0 |
| `errors` | [Error Response](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/connect_responses_error_response.htm) | List of errors encountered during the processing of the API request. | Big, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the credit memo line is successfully unapplied (`true`) or not (`false`). | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-credit-memo-line-unapplied.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
