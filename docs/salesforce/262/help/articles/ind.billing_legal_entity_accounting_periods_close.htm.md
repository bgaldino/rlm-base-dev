---
article_id: ind.billing_legal_entity_accounting_periods_close.htm
title: Close Legal Entity Accounting Periods
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_legal_entity_accounting_periods_close.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Close Legal Entity Accounting Periods

Maintain financial data integrity and accurate reporting by finalizing all transactions and closing the legal entity accounting periods at the end of their related accounting periods.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with Revenue Cloud


The feature is available for the Invoice and Credit memo records, and their related records with the Revenue Cloud Advanced license or the Revenue Cloud Billing license.

This feature is available for the Payment, Refund, and Debit Memo records, and their related records with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.

USER PERMISSIONS
NEEDED
To close legal entity accounting periods:	

Accounts Receivables Admin permission set

AND

Data Pipelines Base User permission set

Before closing the legal entity accounting period, make sure these settings are configured in your Salesforce org.

Enable Data Pipelines
Turn on Create Transaction Journals for Transactions feature
Turn on Create Transaction Journals for Foreign Exchange Gains or Losses feature, and select the required general ledger accounts
Select a default DPE definition to close legal entity accounting period
If required, enable Multiple currencies and set the dated exchange rates
NOTE If your Billing Admin deletes a dated exchange rate entry, Salesforce recommends running data sync manually before closing the legal entity accounting period.

See Set Up Financial Accounting Features.

Open the record of the legal entity accounting period that you want to close.
Click Close Legal Entity Accounting Period and confirm that you want to close it.

After clicking Close Legal Entity Accounting Period, three data processing engine jobs run in a sequence. See Understand the Legal Entity Accounting period Closure Procedure.

Legal Entity Accounting Period Closure Procedure
When you close legal entity accounting period, the system runs three Data Processing Engine (DPE) definitions in a sequence.
Example: Automatically Capture Unrealized Foreign Exchange Unrealized Gains or Losses
Explore an example to understand how to a set up general ledger accounts on the Salesforce org's default general ledger accounts and create dual transaction journals and reversal transaction journals to capture unrealized gains or losses amount of the invoices during legal entity accounting period closure.
