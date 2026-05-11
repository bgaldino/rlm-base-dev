---
article_id: ind.billing_payment_batch_run_overview.htm
title: Payment Batch Run Overview
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_batch_run_overview.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Payment Batch Run Overview

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Payment Batch Run Overview

At the start time of the payment scheduler, payment batch runs start processing payment schedule items based on the defined criteria.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with Revenue Cloud
The Salesforce Payments feature is available with the Revenue Cloud Billing license, with a cost per transaction model for both native and Bring Your Own payment gateways. Contact your Salesforce account executive for more information.
If you purchased the Revenue Cloud Billing license on or before July 2025, contact your Salesforce account executive to add the Salesforce Payments feature to your existing license.
Process Overview

Understand the steps involved in processing payment schedule items and applying the corresponding payments.

Payment batch runs process Payment Schedule Item records that are in the Ready for Processing status and are related to Payment Schedule records that are in the Open status.
A Payment record is created for each payment schedule item that’s successfully processed.
The payment batch run then applies the Payment record to the corresponding Invoice or Invoice Line record based on the payment application level.

Billing applies payments based on the descending order of invoice line balances, that is, a payment is first applied to an invoice line with the highest balance.

NOTE Payments can only be applied to invoices of the same currency.
Payment Methods

For automatically created payment schedules and payment schedule items, the payment gateway collects payments by using the default saved payment method.

For manually created payment schedules and payment schedule items, the payment gateway collects payments by using the most recently created saved payment method for the account that’s related to the invoice.

Statuses of Payment Schedules and Payment Schedule Items

The status of the payment schedule item is updated at various stages of the payment batch run.

PAYMENT BATCH RUN STAGE	PAYMENT SCHEDULE ITEM STATUS
A payment batch run picks up the payment schedule item for processing.	Processing
A payment batch run completes collecting the amount of the payment schedule by using the merchant account.	Processed
A payment batch run applies the payment schedule item to an invoice or invoice line.	Applied
A payment batch run fails to process the payment schedule.	Failed
A payment batch run fails to apply the payment schedule item to an invoice or invoice line.	Apply Failed
A payment batch run successfully processes a payment schedule.	Completed
The balance of the corresponding invoice is less than that of the payment schedule line.	Canceled
Results of Payment Application

After payments are collected and applied, Billing automatically creates and updates these fields and records.

PAYMENT APPLICATION LEVEL	UPDATED PAYMENT SCHEDULE AND PAYMENT SCHEDULE ITEM FIELDS	UPDATED INVOICE FIELDS	NEW RECORDS
Invoice	

Payment Schedule fields:

Status changes to Completed
Total Processed Amount
Remaining Amount To Be Processed
Total Applied Amount

Payment Schedule Item fields:

Status changes to Applied
Processed Amount
Payment Source
Last Payment Gateway Log
Payment Gateway Log Number
	
Balance
Net Payments Applied if the Settlement Status is Settled
Settlement Status changes to Partially Settled or Settled based on the applied payment amount
Full Settlement Date if the Settlement Status is Settled
Settlement Level changes to Invoice
Saved Payment Method
	
A Payment record is created after payment is collected using the merchant account.
A Payment Line Invoice record is created after the payment is applied to an invoice.

Invoice Line	

Payment Schedule fields:

Status changes to Completed
Total Processed Amount
Remaining Amount To Be Processed
Total Applied Amount

Payment Schedule Item fields:

Status changes to Applied
Processed Amount
Payment Source
Last Payment Gateway Log
Payment Gateway Log Number
	
Balance
Net Payments Applied if the Settlement Status is Settled
Settlement Status changes to Partially Settled or Settled based on the applied payment amount
Full Settlement Date if the Settlement Status is Settled
Settlement Level changes to Invoice Line
Saved Payment Method
	
A Payment record is created after payment is collected using the merchant account.
A Payment Line Invoice Line record is created after the payment is applied to an invoice line.
Payment Batch Run Failures

To troubleshoot failed payment schedule items, check the Revenue Transaction Error Logs related list on the Payment Batch Run and Payment Schedule records.

To automatically retry failed payments, set up payment retry rules, define a default payment retry rule set, and then enable the retry failed payments feature on the Billing Settings page.

To manually retry processing of failed payments, change the status of the failed payment schedule items to Canceled. Then, create new payment schedule items with the same details and schedule a payment batch run.
