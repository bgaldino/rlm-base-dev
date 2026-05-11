---
article_id: ind.billing_general_ledger_account_assignment_rules_criteria.htm
title: Define Criteria for Transaction Types
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_general_ledger_account_assignment_rules_criteria.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Define Criteria for Transaction Types

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Define Criteria for Transaction Types

Edit, delete, or define the filter criteria for the transaction type on the general ledger account assignment rule you created.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS
NEEDED
To create general ledger account assignment rules and related records:	Accounts Receivables Admin permission set
NOTE Use the Edit button or the Define Criteria button on the General Ledger Account Assignment Rule record to add, edit, or delete filter criteria. When you use the Define Criteria button, you must deactivate the related general ledger account assignment rule to save your changes.
From the App Launcher, find and select General Ledger Account Assignment Rules.
Open the General Ledger Account Assignment Rule record that you want to define the criteria for.
Click Define Criteria.
Select a transaction amount field.

The Transaction Amount Field shows the standard and custom currency fields of the transaction type of the general ledger account assignment rule. The value of the selected currency field is used for the credit or debit amounts when the transaction journals are generated.

For General Ledger Account Assignment Rule records created before Summer ’25, the Transaction Amount Field value wasn't preselected. From Summer ’25, you can select a Transaction Amount Field value for the existing General Ledger Account Assignment Rule records.

Specify the filter criteria.
To filter records that meet all the filter conditions, select All (AND).
To filter records that meet any of the filter conditions, select Any (OR).
To define custom filter criteria, select Custom and enter your custom filter logic. For example, enter (1 AND 2) OR 3).
Define the filter conditions based on the fields from the transaction type of the general ledger account assignment rule.
You can define up to 10 conditions and select both custom and standard fields of the data types: currency, date, percent, picklist, number, lookup, and text.
Save your work.

For each filter criteria, a billing batch filter criteria record is created. When billing transactions that meet the general ledger account assignment rule and filter criteria are created, then dual transaction journals are created.
