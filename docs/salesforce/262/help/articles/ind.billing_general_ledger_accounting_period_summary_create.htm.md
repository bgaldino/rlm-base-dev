---
article_id: ind.billing_general_ledger_accounting_period_summary_create.htm
title: Create General Ledger Accounting Period Summary Manually
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_general_ledger_accounting_period_summary_create.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Create General Ledger Accounting Period Summary Manually

General Ledger Accounting Period Summary records are automatically created when the Create General Ledger Accounting Period Summary Records for Multiple Currencies or the Create General Ledger Accounting Period Summary Records data processing engine runs during legal entity accounting period closure. You can create them manually as well. General ledger accounting period summaries are created to capture the opening balance and closing balance for general ledger accounts of a legal entity accounting period.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To create general ledger accounting period summary:	Accounts Receivables Admin permission set

You can manually create a General Ledger Accounting Period Summary records only when the status of the legal entity accounting period is Open. You can create a general ledger accounting period summary for every combination of general ledger account and legal entity accounting period.

IMPORTANT

For Salesforce orgs that are created in Winter ’26, the General Ledger Accounting Period Summaries tab is available by default. For Salesforce orgs that are created before Winter ’26, change the tab settings for this object to Default On.

From the App Launcher, find and select General Ledger Accounting Period Summaries.
Click New.
Select a legal entity accounting period.
Select the general ledger account that you want to calculate the balances for.
Enter the total debit amount.
Enter the total credit amount.
Enter the opening balance amount.
Save your work.

The closing balance amount for the general ledger accounting period summary is automatically derived based on the type of the general ledger account. You can edit the general ledger accounting period summary when the status of the related legal entity accounting period is Pending Closure, Opened, or Reopened.

NOTE The Total Debit Amount, Total Credit Amount, Opening Balance Amount, and Closing Balance Amount fields of manually created General Ledger Accounting Period records are updated automatically when their related legal entity accounting period is closed.
SEE ALSO
DPE: Create General Ledger Accounting Period Summary Records for Multiple Currencies
