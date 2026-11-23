---
article_id: ind.billing_payments_apis.htm
title: Process Payments and Issue Refunds by Using APIs
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payments_apis.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payments.htm
fetched_at: 2026-11-23
---

# Process Payments and Issue Refunds by Using APIs

Use a suite of APIs to process payments and issue refunds. Authorize and capture payments by using native payment gateways, reverse payment authorizations, tokenize payment methods, and save card details for processing recurring payments. Create and update payment schedulers, and allocate or unallocate payments. You can process ad hoc payments, and refund your customers if they change or cancel products or services that they paid for.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Cloud
To integrate a native payment gateway, you have two options. Use Salesforce Payments, which runs on Stripe and is available with the the Revenue Cloud Billing license on a cost-per-transaction basis. Or, connect your own Adyen account, contracted directly with Adyen.
 
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
Issue refunds against original payments	

Refund Line Apply API

To automate this step, build a custom flow and use the Automate Refund action.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_payments_apis.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
