---
page_id: connect_responses_rules_application_output.htm
title: Rules Application
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_rules_application_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
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
| `rulesApplication​Summary` | [Rules Application Summary](./connect_responses_rules_application_summary_output.htm.md "Output representation of the summary of the application rule. This includes the number of payments and credit memos for the account, the total number of payments and credit memos that's applied to invoices, and whether all invoices for an account are considered (true) or not (false).") | Summary of the application rule. This includes the number of payments and credit memos for the account, the total number of payments and credit memos that are applied to invoices, and whether all invoices for an account are considered (`true`) or not (`false`). | Big, 66.0 | 66.0 |
| `applied​Rules` | String[] | Rules that were applied. Valid values are `Match ID`, `Match Balance`, `Prioritize Highest Balance Invoices`, or `Prioritize Oldest Invoices`. | Big, 66.0 | 66.0 |
| `errors` | [Rules Application Error](./connect_responses_rules_application_error_output.htm.md "Output representation of the error details for rules application failure.")[] | Details of the errors if the API request was unsuccessful. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_rules_application_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
