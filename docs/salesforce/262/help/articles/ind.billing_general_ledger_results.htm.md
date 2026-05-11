---
article_id: ind.billing_general_ledger_results.htm
title: Automatic Creation of Dual Transaction Journals
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_general_ledger_results.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Automatic Creation of Dual Transaction Journals

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Automatic Creation of Dual Transaction Journals

Automatically generate dual transaction journals, that represent a credit entry and a debit entry, based on the configuration for the transaction type in the General Ledger Account Assignment Rule record. Integrate these transaction journals with any accounting system of your choice to prepare your financial statements such as balance sheets, and profit and loss statements.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.

After your Accounts Receivables admin creates general ledger accounts and assignment rules, and your Billing admin enables the Create Transaction Journals for Transactions feature, the system automatically creates transaction journals in these scenarios:

BILLING TRANSACTION	TRANSACTION JOURNALS CREATED WHEN
Invoice, Invoice Line, and Invoice Line Tax	A Invoice record's status changes to Posted, Voided, or Canceled
Credit Memo, Credit Memo Line, and Credit Memo Line Tax	A Credit Memo record's status changes to Posted, Voided, or Canceled
Credit Memo Invoice Application and Credit Memo Line Invoice Line	After these records are created
Payment	A Payment record's status changes to Processed
Payment Line Invoice and Payment Line Invoice Line	After these records are created
Refund	A Refund record's status changes to Processed
Refund Line Payment	After these records are created
Debit Memo Line	After these records are created
NOTE Your Accounts Receivable Admin can create General Ledger Account and General Ledger Account Assignment Rule records even when the Create Transaction Journals for Transactions toggle is disabled.
