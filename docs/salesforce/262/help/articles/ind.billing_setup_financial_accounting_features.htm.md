---
article_id: ind.billing_setup_financial_accounting_features.htm
title: Set Up Financial Accounting Features
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_financial_accounting_features.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
parent_article: ind.billing_setup_additional_features.htm
fetched_at: 2026-05-11
---

# Set Up Financial Accounting Features

Make sure that every billing transaction is compliant with double-entry accounting principles by automatically generating dual transaction journals, each containing both a credit and a debit entry to maintain balanced records. Select a default Data Processing Engine definition that's run to close legal entity accounting periods when your Billing operations user initiates their closure. Set up Billing to show transaction amounts in both the transactional currency and your corporate currency.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Agentforce Revenue Management


The Store Transaction Amounts in Corporate Currency and Legal Entity Accounting Periods features are available:

For the Invoice and Credit Memo records, and their related records with the Agentforce Revenue Management Advanced license or the Agentforce Revenue Management Billing license.
For the Payment, Refund, and Debit Memos records, and their related records only with the Agentforce Revenue Management Billing license. Contact your Salesforce account executive for more information.

The Create Transaction Journals for Transactions feature and Create Transaction Journals for Foreign Exchange Gains or Losses feature are available with the Agentforce Revenue Management Billing license. Contact your Salesforce account executive for more information.

USER PERMISSIONS
NEEDED
To enable and configure financial accounting features:	Billing Admin permission set

From Setup, in the Quick Find box, enter Billing, and then select Billing Settings. Follow these steps to configure the required financial accounting features based on your business needs.

Create Transaction Journals

To automatically create Transaction Journal records for your transactions, turn on Create Transaction Journals for Transactions.

After turning on Create Transaction Journals for Transactions, make sure that your Accounts Receivables admin creates general ledger accounts and general ledger account assignment rules, and defines the criteria for billing transactions.

Create Foreign Exchange Gain and Loss Transaction Journals

To automatically create foreign exchange gain and loss transaction journals for your billing transactions, turn on Create Transaction Journals for Foreign Exchange Gains or Losses.

To use this feature, consider these key requirements.

The Create Transaction Journals for Foreign Exchange Gains or Losses toggle appears only when Create Transaction Journals for Transactions is turned on.
This feature is applicable only when advanced currency management is enabled and dated conversion rates are set in your Salesforce org.
Use only these general ledger accounts to create realized and unrealized gains and losses transaction journals. Don't set up general ledger account assignment rules for these accounts:
Select the unrealized gain and unrealized loss general ledger accounts.
Select the realized gain and realized loss general ledger accounts.
Select the account receivable general ledger account.

See Foreign Exchange Realized Gains and Losses.

Select Default Data Processing Engine Definition to Close Legal Entity Accounting Periods

In the Billing Defaults section, select a default Data Processing Engine (DPE) definition to close legal entity accounting periods.

Use the Close Legal Entity Accounting Period Data Processing Engine definition, or clone and customize it to suit your requirements.

If you don't select a default DPE definition, the system automatically selects either the Close Legal Entity Accounting Period DPE definition or the Close Legal Entity Accounting Period (Advanced) DPE definition based on your license.

See Close Legal Entity Accounting Periods and Data Processing Engine.

View Transaction Amounts in Corporate and Functional Currencies

To view transaction amounts in corporate and functional currency, turn on Store Transaction Amounts in Corporate and Functional Currencies.

This feature is applicable only when multiple currencies is enabled for your Salesforce organization.

See Close Legal Entity Accounting Periods.

After you set up financial accounting features, your Accounts Receivables admins can manage financial accounting.
