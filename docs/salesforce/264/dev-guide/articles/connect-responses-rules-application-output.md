---
page_id: connect-responses-rules-application-output
title: Rules Application
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-rules-application-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_rules_application_output.htm
fetched_at: 2026-11-25
---

# Rules Application

Output representation of the details of rules application.

## JSON Example

This example shows the rules application response.

```
{
  "isSuccess": true,
  "rulesApplicationSummary": {
    "fetchedPaymentsCount": 250,
    "fetchedCreditMemosCount": 250,
    "totalPaymentApplications": 250,
    "totalCreditMemoApplications": 200,
    "areAllInvoicesConsidered": true
  },
  "appliedRules": [
    "Match ID",
    "Match Balance"
  ],
  "errors": []
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `isSuccess` | Boolean | Indicates whether the rules are applied (`true`) or not (`false`). | Big, 66.0 | 66.0 |
| `rulesApplication​Summary` | [Rules Application Summary](./connect-responses-rules-application-summary-output.md) | Summary of the application rule. This includes the number of payments and credit memos for the account, the total number of payments and credit memos that are applied to invoices, and whether all invoices for an account are considered (`true`) or not (`false`). | Big, 66.0 | 66.0 |
| `applied​Rules` | String[] | Rules that were applied. Valid values are `Match ID`, `Match Balance`, `Prioritize Highest Balance Invoices`, or `Prioritize Oldest Invoices`. | Big, 66.0 | 66.0 |
| `errors` | [Rules Application Error](./connect-responses-rules-application-error-output.md)[] | Details of the errors if the API request was unsuccessful. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-rules-application-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
