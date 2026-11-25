---
page_id: connect-responses-rules-application-summary-output
title: Rules Application Summary
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-rules-application-summary-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_rules_application_summary_output.htm
fetched_at: 2026-11-25
---

# Rules Application Summary

Output representation of the summary of the application rule. This includes the number of payments and credit memos for the account, the total number of payments and credit memos that’s applied to invoices, and whether all invoices for an account are considered (true) or not (false).

## JSON Example

This example shows the rules application summary.

```
{
  "rulesApplicationSummary": {
    "fetchedPaymentsCount": 5,
    "fetchedCreditMemosCount": 2,
    "totalPaymentApplications": 3,
    "totalCreditMemoApplications": 1,
    "areAllInvoicesConsidered": true
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `fetched​Payments​Count` | Integer | Total number of payments related to the account. | Big, 66.0 | 66.0 |
| `fetchedCredit​Memos​Count` | Integer | Total number of credit memos or credit memo lines related to the account. | Big, 66.0 | 66.0 |
| `totalPayment​Applications` | Integer | Total number of payments that are applied to the invoices or invoice lines. | Big, 66.0 | 66.0 |
| `totalCredit​Memo​Applications` | Integer | Total number of credit memos that are applied to the invoice or invoice lines. | Big, 66.0 | 66.0 |
| `areAll​Invoices​Considered` | Boolean | Indicates whether all invoices are considered (`true`) or not (`false`). | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-rules-application-summary-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
