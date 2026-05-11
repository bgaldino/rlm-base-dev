---
article_id: ind.billing_payments_apis.htm
title: Process Payments and Issue Refunds by Using APIs
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payments_apis.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Process Payments and Issue Refunds by Using APIs

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Process Payments and Issue Refunds by Using APIs

Use a suite of APIs to process payments and issue refunds. Authorize and capture payments by using native payment gateways, reverse payment authorizations, tokenize payment methods, and save card details for processing recurring payments. Create and update payment schedulers, and allocate or unallocate payments. You can also process ad hoc payments, and refund your customers if they change or cancel products or services that they paid for.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with Revenue Cloud
The Salesforce Payments feature is available with the Revenue Cloud Billing license, with a cost per transaction model for both native and Bring Your Own payment gateways. Contact your Salesforce account executive for more information.
If you purchased the Revenue Cloud Billing license on or before July 2025, contact your Salesforce account executive to add the Salesforce Payments feature to your existing license.
USER PERMISSIONS NEEDED
To process payments and issue refunds by using APIs:	Payment Operations User permission set
GOAL	API
Process ad hoc payments	

Payment Sale API

To automate the processing of ad hoc payments, build a custom flow and use the Payment Sale action.


Authorize payments	Payment Authorization API
Reverse the authorization of payments	Authorization Reversal API
Capture authorized payments	Payment Capture API
Tokenize payment methods	Tokenize Payment Method API
Create payment schedulers	Create Payment Scheduler API
Activate or deactivate payment schedulers	Update Payment Scheduler API
Apply a payment to an invoice or invoice line	

Payment Line Apply API

To automate this step, build a custom flow and use the Apply Payment action.


Unapply a payment from an invoice or invoice line	

Payment Line Unapply API

To automate this step, build a custom flow and use the Unapply Payment action.


Create refunds for processed payments	Create a Payment Refund API
Apply refunds to the processed payments	Apply Refunds to Payments API
