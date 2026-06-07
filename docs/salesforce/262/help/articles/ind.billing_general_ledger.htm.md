---
article_id: ind.billing_general_ledger.htm
title: Manage Chart of Accounts and Transaction Journals in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_general_ledger.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Manage Chart of Accounts and Transaction Journals in Agentforce Revenue Management

Set up a chart of accounts for your legal entities by creating general ledger accounts. Assign appropriate general ledger accounts to transaction journals by setting up general ledger account assignment rules. Automatically generate dual transaction journals based on the configuration for the billing transaction type and criteria in the general ledger account assignment rule.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
What are Chart of Accounts and Dual Journal Entries?
Financial accounting provides a structured framework for recording, summarizing, and reporting an organization's financial transactions. The chart of accounts and the principle of dual journal entries are two fundamental concepts of this framework.
Create General Ledger Accounts
Set up a chart of accounts for your organization's legal entities by creating general ledger accounts. Use these accounts to categorize your billing transactions by accounting type and report them in your company’s financial statements.
General Ledger Account Assignment Rules and Related Records
Define rules to assign accurate general ledger accounts to transaction journals and establish criteria for which these rules must apply to. Define multiple journal entry rules for a billing transaction with a specified criteria from a single user interface.
Automatic Creation of Dual Transaction Journals
Automatically generate dual transaction journals, that represent a credit entry and a debit entry, based on the configuration for the transaction type in the General Ledger Account Assignment Rule record. Integrate these transaction journals with any accounting system of your choice to prepare your financial statements such as balance sheets, and profit and loss statements.
Example: Chart of Accounts and Dual Journal Entries
Explore an example to understand how chart of accounts are set up and how dual transaction journals are created based on the configured general ledger accounts and account assignment rules.
Create General Ledger Accounting Period Summary Manually
General Ledger Accounting Period Summary records are automatically created when the Create General Ledger Accounting Period Summary Records for Multiple Currencies or the Create General Ledger Accounting Period Summary Records data processing engine runs during legal entity accounting period closure. You can create them manually as well. General ledger accounting period summaries are created to capture the opening balance and closing balance for general ledger accounts of a legal entity accounting period.
