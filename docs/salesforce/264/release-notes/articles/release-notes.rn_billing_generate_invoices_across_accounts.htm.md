---
article_id: release-notes.rn_billing_generate_invoices_across_accounts.htm
title: Generate Invoices Across Accounts for Owned and Billed Charges
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_billing_generate_invoices_across_accounts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_billing_invoices.htm
fetched_at: 2026-09-30
---

# Generate Invoices Across Accounts for Owned and Billed Charges

At the account level, run Generate Invoices, Preview Invoices, and Invoice Scheduler for all billing schedule groups that list the account as a billing account in a billing arrangement. Billing includes both owned and billed groups by default. Accounts are invoiced for every billing schedule group they owe, including split invoices for charges owned by other accounts. This change eliminates manual reconciliation across split billing scenarios. Previously, account-level operations processed only billing schedule groups the account owned.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Billing license.

Who: To generate and preview invoices for an account, you need the Billing Admin or the Billing Operations User permission set.

SEE ALSO
Salesforce Help: Generate Invoices for Accounts or Orders
Salesforce Help: Manage Billing Arrangements
