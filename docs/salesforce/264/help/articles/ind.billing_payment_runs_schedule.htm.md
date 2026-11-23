---
article_id: ind.billing_payment_runs_schedule.htm
title: Schedule Payment Batch Runs to Process Payments
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_runs_schedule.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payments.htm
fetched_at: 2026-11-23
---

# Schedule Payment Batch Runs to Process Payments

Set up a payment scheduler with specific filters to automatically process payments for your transactions. Payment batch runs process existing payment schedules and payment schedule items to collect the corresponding payments, and then apply them to invoices based on the payment application level.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Cloud
To integrate a native payment gateway, you have two options. Use Salesforce Payments, which runs on Stripe and is available with the the Revenue Cloud Billing license on a cost-per-transaction basis. Or, connect your own Adyen account, contracted directly with Adyen.
 
USER PERMISSIONS NEEDED
To schedule payment batch runs:	Payment Operations User permission set
From the App Launcher, find and select Billing Batch Schedulers.
Click New Payment Scheduler.
Enter a name for the payment scheduler.
To activate the payment scheduler, select Active.
Payments are collected and applied only when the scheduler is active. You can create payment schedulers in inactive state, and modify and activate them later.
Select the frequency at which you want the payment batch runs to process payments.
If you select Once, select a start date and a start time for the scheduler.
If you select Daily, select a start date and a start time, and an end date for the scheduler.
If you select Monthly, select a start date and a start time, and an end date for the scheduler. Additionally, select the number of days after which you want the monthly payment batch run to recur.
Click Next.
To configure matching criteria for the payment scheduler, select Match Any, select Payment Schedule Item as the Type, Payment Run Matching Value as the Column, and select the payment run matching value that you want to filter payment schedule items by.
By default, no matching criteria is selected. If you don't specify a matching criteria, the default matching criteria is used to determine the payment schedule items that the payment batch run must process. With the default matching criteria, all the payment schedule items with a target payment date that's less than or equal to the job run date are processed by the payment batch runs.
Click Create.

A Billing Batch Scheduler record with Payment as the Job Type is created. At the start time of the scheduler, a Payment Batch Run record is created.

To understand how payment batch runs process payment schedules and payment schedule items, see Payment Batch Run Overview.

SEE ALSO
Revenue Cloud Developer Guide: PaymentLineInvoiceLine
Revenue Cloud Developer Guide: Billing Fields on PaymentLineInvoice

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_payment_runs_schedule.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
