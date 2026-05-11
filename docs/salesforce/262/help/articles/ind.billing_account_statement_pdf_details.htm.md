---
article_id: ind.billing_account_statement_pdf_details.htm
title: Generated Statement Details
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_account_statement_pdf_details.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Generated Statement Details

The generated account statement PDF groups billing data into an account summary, transaction history, and balance due. The statement period filters transaction history, while summary and balance due reflect balances as of generation time.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Account Summary

The account summary shows the primary account’s current financial position, calculated as of the statement generation date. It includes all transactions regardless of the selected statement period, and amounts appear in the primary account currency.

Transaction History

The transaction history lists billing transactions for the selected accounts within the statement period. It includes only posted transactions with transaction dates that fall within the defined date range. Transactions must belong to the selected accounts and match the selected transaction types. The section includes invoices, credit memos, debit memos, payments, and refunds, grouped by account. Amounts are in their original currency.

Balance Due

The balance due section shows the total outstanding balance for the primary account as of the statement generation date.

Key Behaviors and Considerations

The statement period determines which transactions appear in transaction history. The account summary and balance due reflect the current balance as of the statement generation date, not a historical balance as of the statement end date. The system includes only posted transactions.
