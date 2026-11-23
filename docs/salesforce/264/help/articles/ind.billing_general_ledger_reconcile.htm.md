---
article_id: ind.billing_general_ledger_reconcile.htm
title: Reconcile Failed Transaction Journals
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_general_ledger_reconcile.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_general_ledger.htm
fetched_at: 2026-11-23
---

# Reconcile Failed Transaction Journals

When Billing fails to create transaction journals, generate them from the details saved in Revenue Transaction Error Log (RTEL) records by running a custom Apex class.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions withthe Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To reconcile transaction journals by using Apex class:	

Accounts Receivables Admin permission set

And

Author Apex

If the transaction journals generation fails for the billing transactions based on the general ledger account assignment rule, it creates RTEL records for each failed transaction journal. Billing captures the entire failed transaction journal's details, including all the field values needed to rebuild the transaction journal, as a serialized JSON payload in the RTEL's Request field.

To reconcile the failed transaction journals, run the sample TransactionJournalReconciler and TransactionJournalBatchReconciler Apex classes with the RTEL IDs for the debit entry and the credit entry as input parameters. After successful execution of the Apex class, the system creates the transaction journals.

TransactionJournalReconciler Apex Class
TransactionJournalReconciler Apex class is used to generate failed transaction journals from the payloads saved in Request field on the Revenue Transaction Error Log records.
TransactionJournalBatchReconciler Apex Class
Runs TransactionJournalReconciler in batches so you can reconcile large numbers of RTELs across batches.
SEE ALSO
Executing Anonymous Apex Code
Implementation Steps
Save the TransactionJournalReconciler Apex class. See Define Apex Classes.
This Apex class reconciles failed transaction journals by using the RTELs.
Save the TransactionJournalBatchReconciler Apex class. See Define Apex Classes and Use Batch Apex.
This Apex class implements the batchable interface and processes RTELs in batches. Make sure to save TransactionJournalReconciler before you save TransactionJournalBatchReconciler Apex class.
In the Developer Console, run the sample Apex code.
The code automatically selects RTEL IDs from the Transaction Journal Generation category and have a non-empty Request field.
View the generated transaction journals.
Run the Apex Code in Developer Console
From the Setup menu, select Developer Console.
From the Debug tab, select Open Execute Anonymous Window.
In the Enter Apex Code dialog box, enter this code.
Set<Id> ids = new Set<Id>();
  for (RevenueTransactionErrorLog r : [
          SELECT Id, Request FROM RevenueTransactionErrorLog
          WHERE Category = 'Transaction Journal Generation'
          ORDER BY CreatedDate DESC]) {
      if (String.isNotBlank(r.Request)) ids.add(r.Id);
  }         
  System.debug('RTELs to reconcile: ' + ids.size());
  Id jobId = Database.executeBatch(new TransactionJournalBatchReconciler(ids), batchSize);

The Apex class is idempotent, so reprocessing the same SOQL doesn't create duplicate transaction journals. Because each journal has a unique identifier, the Apex class skips previously reconciled journals and they're reported as failed in the execution log. RTELs remain unchanged after transaction journal reconciliation. The code orders RTEL IDs by latest created date, and the batch class skips RTELs without a request payload and any credit or debit transaction journals that don’t form a pair.
Replace batchSize with the number of revenue transaction error logs to process in each batch. For example, enter 10 to process 10 revenue transaction error logs per batch.
Specifying the batchSize parameter is optional.
Click Execute.
To check the status of execution, click the Logs tab.
Select Debug Only.
Double-click the most recent log.

The execution log details show the number of RTELs considered, the number of transaction journals parsed, created, and failed, and the number of unpaired transaction journals skipped. For failed transaction journals, the log shows error messages. When the Apex class runs successfully, it creates the transaction journals by using the Transaction Journal payload on the RTELs.

View Transaction Journals
From App Launcher, find and select Transaction Journals.
Refresh the page.

The list shows the newly created transaction journal records.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_general_ledger_reconcile.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
