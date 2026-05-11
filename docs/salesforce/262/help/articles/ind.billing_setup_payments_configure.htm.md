---
article_id: ind.billing_setup_payments_configure.htm
title: Set Up Payment Features in Billing
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_payments_configure.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Set Up Payment Features in Billing

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Set Up Payment Features in Billing

Set up Billing to automatically create payment schedules and payment schedule items for posted invoices, share payment accounts, retry failed payments, pass payment metadata, issue refunds, apply credits and payments to settle the balances of invoices or invoice lines, and automate dunning orchestration.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with Revenue Cloud
The Salesforce Payments feature is available with the Revenue Cloud Billing license, with a cost per transaction model for both native and Bring Your Own payment gateways. Contact your Salesforce account executive for more information.
If you purchased the Revenue Cloud Billing license on or before July 2025, contact your Salesforce account executive to add the Salesforce Payments feature to your existing license.
USER PERMISSIONS NEEDED
To enable and configure Payments features:	Payment Admin permission set
From Setup, in the Quick Find box, enter Billing, and then select Billing Settings.
To automatically create payment schedules and payment schedule items for posted invoices, turn on Create Payment Schedules and Payment Schedule Items.
To view billing details related to payments, payment authorizations, refunds, and saved payment methods, turn on Share Payment Accounts.
To automatically retry failed payments for specific error categories at various time intervals, add at least one default payment retry rule, and then turn on Retry Failed Payments.
To enhance your payment transactions with enhanced payment metadata, turn on Level 2 and Level 3 Data Support.
To automatically apply standalone processed payments to posted invoices during invoice run, turn on Application of Payments to Posted Invoices.
To automate the issue of refunds when a fully settled invoice is amended or canceled, turn on Issue Refunds and Settle Balances.
Select the payment application level. The label of this setting is Credit and Payment Application Level.
To apply payments to settle the balances of invoice lines of posted invoices, select Invoice Line.
To apply payments to settle the balances of posted invoices that have invoice line amounts rolled-up, select Invoice.

The default payment application level is Invoice Line.

Select the credit memo and payment application rules.
See Define Rules and Order to Apply Credit Memo and Payments.

After you configure Salesforce Payments and turn on the Payment features of Billing, your Payment Operations users can process payments and issue refunds.
