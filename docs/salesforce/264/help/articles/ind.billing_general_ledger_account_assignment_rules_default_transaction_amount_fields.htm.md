---
article_id: ind.billing_general_ledger_account_assignment_rules_default_transaction_amount_fields.htm
title: Default Transaction Amount Fields
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_general_ledger_account_assignment_rules_default_transaction_amount_fields.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_general_ledger_account_assignment_rules_create.htm
fetched_at: 2026-09-04
---

# Default Transaction Amount Fields

If you don't select a transaction amount field when defining the criteria, the default transaction amount field is populated as the credit or debit amount in transaction journals.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.

These fields are considered as the default transaction amount fields:

TRANSACTION TYPE	TRANSACTION AMOUNT FIELD LABEL
Invoice	Total with Tax
Invoice Line	Charge Amount
Invoice Line Tax	Tax Amount
Credit Memo	Total with Tax
Credit Memo Line	Charge Amount
Credit Memo Line Tax	Tax Amount
Credit Memo Line Invoice Line	Amount
Credit Memo Invoice Application	Amount
Payment	Amount
Payment Line Invoice	Amount
Payment Line Invoice Line	Amount
Refund	Amount
Refund Line Payment	Amount
Debit Memo Line	Charge Amount
