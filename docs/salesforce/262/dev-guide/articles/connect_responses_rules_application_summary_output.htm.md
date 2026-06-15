---
page_id: connect_responses_rules_application_summary_output.htm
title: Rules Application Summary
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_rules_application_summary_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Rules Application Summary

Output representation of the summary of the application rule. This includes the number of
payments and credit memos for the account, the total number of payments and credit memos that's
applied to invoices, and whether all invoices for an account are considered (true) or not
(false).

JSON example
:   This example shows the rules application summary.

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
