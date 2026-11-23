---
article_id: ind.billing_account_statement_pdf_details.htm
title: Generated Statement Details
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_account_statement_pdf_details.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_account_statement.htm
fetched_at: 2026-11-23
---

# Generated Statement Details

The generated account statement PDF groups billing data into an account summary, transaction history, and balance due. The statement period filters transaction history, while the summary and balance due reflect balances as of the statement generation date.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Account Summary

The account summary shows the primary account’s current financial position, calculated as of the statement generation date. It includes all transactions regardless of the selected statement period, and amounts appear in the primary account currency.

Transaction History

The transaction history lists billing transactions for the selected accounts within the statement period. It includes only posted transactions with transaction dates that fall within the defined date range.

Transactions must belong to the selected accounts and match the selected transaction types. The section includes invoices, credit memos, debit memos, payments, and refunds, grouped by account. Amounts are in their original currency.

Balance Due

The balance due section shows the total outstanding balance for the primary account as of the statement generation date.

Key Behaviors and Considerations

The statement period determines which transactions appear in transaction history. The account summary and balance due reflect the current balance as of the statement generation date, not a historical balance as of the statement end date. The system includes only posted transactions.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_account_statement_pdf_details.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
