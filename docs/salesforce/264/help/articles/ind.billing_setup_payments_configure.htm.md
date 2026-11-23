---
article_id: ind.billing_setup_payments_configure.htm
title: Configure Payment Features in Billing
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_payments_configure.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_setup_salesforce_payments_features.htm
fetched_at: 2026-11-23
---

# Configure Payment Features in Billing

Set up Billing to automatically create payment schedules and payment schedule items for posted invoices, share payment accounts, retry failed payments, pass payment metadata via payment gateways, issue refunds, apply credits and payments to settle the balances of invoices or invoice lines, and automate dunning orchestration.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Cloud
To integrate a native payment gateway, you have two options. Use Salesforce Payments, which runs on Stripe and is available with the the Revenue Cloud Billing license on a cost-per-transaction basis. Or, connect your own Adyen account, contracted directly with Adyen.
 
USER PERMISSIONS NEEDED
To enable and configure Payments features:	Payment Admin permission set
From Setup, in the Quick Find box, enter Billing, and then select Billing Settings.
To automatically create payment schedules and payment schedule items for posted invoices, turn on Create Payment Schedules and Payment Schedule Items.
To view billing details related to payments, payment authorizations, refunds, and saved payment methods, turn on Share Payment Accounts.
To automatically retry failed payments for specific error categories at various time intervals, add at least one default payment retry rule, and then turn on Retry Failed Payments.
To automatically send Level 2 and Level 3 payment details, turn on Level 2 and Level 3 Data Support.
To automatically apply standalone processed payments to posted invoices during invoice run, turn on Application of Payments to Posted Invoices.
To automate the issue of refunds when a fully settled invoice is amended or canceled, turn on Issue Refunds and Settle Balances.
Select the payment application level. The label of this setting is Credit, Refund, and Payment Application Level.
To apply payments to settle the balances of invoice lines of posted invoices, select Line Level.
To apply payments to settle the balances of posted invoices that have invoice line amounts rolled-up, select Header Level.

The default payment application level is Line Level.

Select the credit memo and payment application rules.
See Define Rules and Order to Apply Credit Memo and Payments.

After you configure payment features of Billing, your Payment Operations users can process payments and issue refunds.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_setup_payments_configure.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
