---
article_id: ind.billing_invoice_run_sync_process.htm
title: Convert Automations to Asynchronous for Invoice Batch Runs
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_run_sync_process.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_automate_invoice_generation.htm
fetched_at: 2026-09-04
---

# Convert Automations to Asynchronous for Invoice Batch Runs

Identify active flows and Apex triggers on Billing objects and convert them to asynchronous processes before you schedule an invoice batch run. Synchronous automations can stop a run or leave invoices in Draft In Progress, Posting In Progress, or Error.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To review and convert record-triggered flows:	Manage Flow
To view Apex triggers:	View Setup and Configuration
To convert Apex triggers:	Author Apex
To recover stuck invoices:	

Billing Admin permission set

OR

Billing Operations User permission set

A record-triggered flow or Apex trigger is tied to an object, such as Invoice or Invoice Line. You define and activate the flow on that object in Flow Builder. A person who has the Author Apex permission defines the Apex trigger on that object and sets it to active. These automations are custom. Billing doesn't create them. See Activate or Deactivate a Flow and Define Apex Triggers.

When an invoice batch run generates invoices, the run creates or updates records on Billing objects. Those objects include invoices, invoice lines, tax lines, debit and credit memos, billing schedules, and billing period items. Any active flow or trigger on a Billing object then runs for every record the invoice batch run saves.

A synchronous automation runs as part of saving the record. The invoice batch run doesn't finish saving the invoice until that flow or trigger is done. If the automation queries related records for every invoice, the run can hit processing limits or time out. Invoices can remain in Draft In Progress, Posting In Progress, or Error.

An asynchronous automation waits until the invoice records are saved, then runs. The batch run can finish generating invoices. The flow or trigger still runs, just not while the invoice is being saved.

From Setup, in the Quick Find box, enter Flows, and then select Flows.
Review active record-triggered flows on these Billing objects.
Invoice
Invoice Line
Invoice Line Tax
Debit Memo
Debit Memo Line
Debit Memo Line Tax
Credit Memo
Credit Memo Line
Credit Memo Line Tax
Billing Schedule
Billing Period Item
From Setup, in the Quick Find box, enter Apex Triggers, and then select Apex Triggers.
Review active triggers on the same objects.
To list the automations with SOQL, open the Developer Console Query Editor.

Sample scripts:

For the flow query, select Use Tooling API. For the Apex trigger query, leave Use Tooling API cleared.

Flows:

SELECT Id, IsActive, Label, ProcessType, ManageableState, TriggerObjectOrEventId, TriggerObjectOrEventLabel, TriggerType FROM FlowDefinitionView WHERE TriggerObjectOrEventId IN ('Invoice','InvoiceLine','DebitMemo','DebitMemoLine','CreditMemo','CreditMemoLine','InvoiceLineTax','DebitMemoLineTax','CreditMemoLineTax','BillingSchedule','BillingPeriodItem') AND IsActive = TRUE

Apex triggers:

SELECT Id, TableEnumOrId, Name, Status FROM ApexTrigger WHERE TableEnumOrId IN ('Invoice','InvoiceLine','DebitMemo','DebitMemoLine','CreditMemo','CreditMemoLine','InvoiceLineTax','DebitMemoLineTax','CreditMemoLineTax','BillingSchedule','BillingPeriodItem') AND Status = 'Active'
For each after-save record-triggered flow, move the logic to a Run Asynchronously path so it runs after the invoice save commits. See Triggered Flows.
For each Apex trigger, work with a person who has the Author Apex permission to move the logic out of the record save. Use queueable Apex or an Apex trigger on a change event, which runs after the save is complete. See Queueable Apex and Subscribe with Apex Triggers.

After you convert the automations, schedule the next invoice batch run. See Generate Invoices Automatically Based on Billing Schedules.

If invoices from an earlier run are stuck in Draft In Progress, Posting In Progress, or Error, click Recover on the invoice batch run. Then generate invoices again.
