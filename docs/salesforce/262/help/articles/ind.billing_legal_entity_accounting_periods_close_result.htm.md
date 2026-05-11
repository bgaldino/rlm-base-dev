---
article_id: ind.billing_legal_entity_accounting_periods_close_result.htm
title: Legal Entity Accounting Period Closure Procedure
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_legal_entity_accounting_periods_close_result.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Legal Entity Accounting Period Closure Procedure

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Legal Entity Accounting Period Closure Procedure

When you close legal entity accounting period, the system runs three Data Processing Engine (DPE) definitions in a sequence.

This feature is available for the Invoice and Credit Memo records, and their related records with the Agentforce Revenue Management Advanced license or the Agentforce Revenue Management Billing license.

This feature is available for the Payment, Refund, and Debit Memo records, and their related records with the Agentforce Revenue Management Billing license. Contact your Salesforce account executive for more information.

The Create Transaction Journals for Unrealized Foreign Exchange Gains or Losses and Create General Ledger Accounting Period Summary Records for Multiple Currencies data processing engines are available only with the Agentforce Revenue Management Billing license.

DPE Execution Sequence

These Data Processing Engine definitions are executed in this sequence based on the licenses and currency settings in your Salesforce org.

DATA PROCESSING ENGINE	AGENTFORCE REVENUE MANAGEMENT ADVANCED LICENSE	AGENTFORCE REVENUE MANAGEMENT BILLING LICENSE WITH SINGLE CURRENCY	AGENTFORCE REVENUE MANAGEMENT BILLING LICENSE WITH MULTIPLE CURRENCIES	AGENTFORCE REVENUE MANAGEMENT BILLING LICENSE WITH ADVANCED CURRENCY MANAGEMENT


Close Legal Entity Accounting Period (Basic)

Or

Close Legal Entity Accounting Period (Advanced)

	Close Legal Entity Accounting Period (Basic) DPE runs and closes the legal entity accounting period.	Close Legal Entity Accounting Period (Advanced) DPE runs and closes the legal entity accounting period.	Close Legal Entity Accounting Period (Advanced) DPE runs and closes the legal entity accounting period.	Close Legal Entity Accounting Period (Advanced) DPE runs and closes the legal entity accounting period.
Create Transaction Journals for Unrealized Foreign Exchange Gains or Losses	Not Available	Not Available	Create Transaction Journals for Unrealized Foreign Exchange Gains or Losses DPE runs and creates transaction journals.	

Create Transaction Journals for Unrealized Foreign Exchange Gains or Losses DPE runs and creates transaction journals.




Create General Ledger Accounting Period Summary Records for Multiple Currencies

Or

Create General Ledger Accounting Period Summary Records

	Not Available	Create General Ledger Accounting Period Summary Records DPE runs and creates summary records.	Create General Ledger Accounting Period Summary Records for Multiple Currencies DPE runs and creates summary records.	

Create General Ledger Accounting Period Summaries Using Dated Conversion Rates DPE runs and creates summary records.

DPE: Close Legal Entity Accounting Period

The Close Legal Entity Accounting Period DPE starts a batch calculation job that sets the legal entity accounting period's status to Pending Closure and closure stage to Closing Legal Entity Accounting Period. It then evaluates all the billing transactions related to the legal entity accounting period with these field values.

BILLING TRANSACTION RECORD	FIELD VALUE
Invoice	The status is Posted.
Invoice Line	The status of the parent invoice is Posted.
Invoice Line Tax	The tax processing status is Posted.
Credit Memo	The status is Posted.
Credit Memo Line	The status is Posted.
Credit Memo Line Tax	The calculation status is Complete.
Credit Memo Line Invoice Line	All the records related to the legal entity accounting period are evaluated.
Payment	The status is Processed.
Payment Line Invoice	All the records related to the legal entity accounting period are evaluated.
Payment Line Invoice Line	All the records related to the legal entity accounting period are evaluated.
Refund	The status is Processed.
Refund Line Payment	All the records related to the legal entity accounting period are evaluated.
Debit Memo Line	The status of the related debit memo is Posted.

The DPE definition evaluates the related billing transactions with these statuses. If any of the billing transactions don't have a legal entity accounting period, the batch calculation job assigns a legal entity accounting period to those transactions.

DPE: Create Transaction Journals for Unrealized Foreign Exchange Gains or Losses

The Create Transaction Journals for Unrealized Foreign Exchange Gains or Losses data processing engine starts a batch calculation job to calculate unrealized foreign exchange gains and losses and create dual transaction journals and dual reversal transaction journals.

Field update: The DPE batch calculation job sets the Closure Stage field of the legal entity accounting period to Creating Unrealized Gain or Loss Transaction Journals.
Records considered: All the unsettled and partially settled posted invoices that aren't in corporate currency related to the legal entity accounting period are considered.
Unrealized foreign exchange gains and losses calculation: The difference between the dated conversion rate value on the invoice date and on the end date of the accounting period of the legal entity is calculated.
Transaction journals:
The calculated unrealized gain or loss amount is captured as debit and credit entry of transaction journals for the unrealized gains, unrealized loss, and account receivable general ledger accounts selected on the Billing Settings page.
Two reversal transaction journals are also created on the start date of the next legal entity accounting period. Reversal transaction journals record the same debit and credit amounts as the unrealized transaction journals, but for the opposite general ledger accounts.

See Use Case: Automatically Capture Unrealized Foreign Exchange Unrealized Gains or Losses.

NOTE If multiple currencies aren't enabled in your Salesforce org, then the Create Transaction Journals for Unrealized Foreign Exchange Gains or Losses DPE definition isn't executed.
DPE: Create General Ledger Accounting Period Summary Records for Multiple Currencies

The Create General Ledger Accounting Period Summary for Multiple Currencies DPE definition starts a batch calculation job to calculate the total credit amount, total debit amount, opening balance amount, and closing balance amount for a general ledger account that has transaction journals related to the legal entity accounting period.

Field update: The DPE batch calculation job sets the Closure Stage field of the legal entity accounting period to Creating General Ledger Accounting Period Summaries.
DPE calculation: The DPE definition calculates the amount fields based on the dated conversion rate on the end date of the accounting period related to the legal entity accounting period.
DPE execution logic: There are three DPE definitions. The currency settings configured in your Salesforce org determine which DPE definition runs.
ORG CURRENCY SETTINGS	EXECUTED DPE	FILTERED RECORDS


Both multiple currency and Advanced currency management are disabled

	

Create General Ledger Accounting Period Summary Records DPE runs.

	

The transaction journals are filtered for the legal entity accounting period and opening balance and closing balance are calculated.


Multiple currency is enabled	Create General Ledger Accounting Period Summary Records for Multiple Currencies DPE definition runs.	

All transaction journals for the legal entity accounting period are filtered. The debit and credit amounts of transaction journals that are in a currency other than the legal entity currency are converted into the currency of the legal entity using conversion rates, and then the opening and closing balances are calculated.


Advanced currency management is enabled	

Create General Ledger Accounting Period Summaries Using Dated Conversion Rates DPE runs.

	

All transaction journals for the legal entity accounting period are filtered. The debit and credit amounts of transaction journals that are in a currency other than the legal entity currency are converted into the currency of the legal entity using dated conversion rates, and then the opening and closing balances are calculated.

Result: After the successful execution of the DPE definition, two General Ledger Accounting Period Summary records are created for each general ledger account.
A summary record is created for the legal entity accounting period that's being closed.
A summary record is created for the next legal entity accounting period where the closing balance amount from the current period's record becomes the opening balance for the next period's record.
Go to the related list of the legal entity accounting period to view all the related general ledger accounting period summaries.
Considerations and Limitations
You can manually create a General Ledger Accounting Period Summary record only when the legal entity accounting period status is Open.
Only one General Ledger Accounting Period Summary record can exist for a unique combination of a general ledger account and a legal entity accounting period.
The DPE definition updates any existing General Ledger Accounting Period Summary record with the calculations.
You can manually update the general ledger accounting period summaries only when the status of the related legal entity accounting period is set to Open, Pending Closure, or Reopened.
If the Type field isn't selected on the general ledger accounts, the data processing engine fails and a revenue transaction error log is created.
Result and Error Logs

The fields on the Legal Entity Accounting Period record are updated based on the execution of the DPE definitions.

DPE OUTCOME	RECORD STATUS	RECORD UPDATES	NOTES
Success	The Closure Stage field is set to Completed and Status field is set to Closed.	

The Total Assets Amounts, Total Liabilities Amounts, Total Equities Amount, Total Revenue Amounts, and Total Expenses Amount fields on the legal entity accounting period are automatically updated.

In a Salesforce org with multiple currencies enabled, these fields show values in the legal entity accounting period's currency.

	The calculation of total assets, liabilities, equity, revenue, and expenses for a legal entity accounting period doesn't consider the general ledger accounting period summaries created for the foreign exchange realized and unrealized gain and loss general ledger accounts that are selected on the Billing Settings page.
Error	The Closure Stage field shows the specific DPE definition that encountered the error, and Status is set to Error.	A revenue transaction error log is created.	The revenue transaction error log is found on the related list of the legal entity accounting period.
Monitor Batch Calculation Job

Go to Monitor Workflow Services in Setup to check the status of the batch calculation job.

SEE ALSO
Set Up Financial Accounting Features
Example: Automatically Capture Unrealized Foreign Exchange Unrealized Gains or Losses
