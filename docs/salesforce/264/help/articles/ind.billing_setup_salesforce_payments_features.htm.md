---
article_id: ind.billing_setup_salesforce_payments_features.htm
title: Set Up Payment Features for Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_salesforce_payments_features.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_setup_additional_features.htm
fetched_at: 2026-09-04
---

# Set Up Payment Features for Revenue Management

Set up Payments to streamline the management of the entire payment lifecycle. By establishing a secure connection with native and third-party payment providers, you can directly process payments for customer transactions within your Salesforce environment.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Cloud
The Salesforce Payments feature is available with the Revenue Cloud Billing license, with a cost per transaction model for both native and Bring Your Own payment gateways. Contact your Salesforce account executive for more information.
If you purchased the Revenue Cloud Billing license on or before July 2025, contact your Salesforce account executive to add the Salesforce Payments feature to your existing license.

This flowchart shows how a user with the Payment Admin permission set can set up Payments in Revenue Management.

Configure Salesforce Payments
To use Salesforce Payments for financial transactions, set up an Experience Cloud site and enable Payments for your org. Then, use a guided setup to create a merchant account and payment methods.
Set Up Native Payment Gateways by Using Salesforce Payments
Accept electronic payments from your customers on Stripe and Adyen payment gateways by using the Salesforce Payments native payment service. Create new Stripe merchant accounts or connect your existing Adyen merchant accounts by using Salesforce Payments.
Set Up Third-Party Payment Gateways
Bring your own third-party payment gateways to process payments and issue refunds. Set up and add external payment gateways, and then connect them to Billing.
Set Up Payment Features in Billing
Set up Billing to automatically create payment schedules and payment schedule items for posted invoices, share payment accounts, retry failed payments, pass payment metadata via payment gateways, issue refunds, apply credits and payments to settle the balances of invoices or invoice lines, and automate dunning orchestration.
Generate Pay Now Links for Business Accounts
Collect invoice payments against the correct business account by generating Pay Now links. Your customers pay as a guest with their preferred payment method and can save it for future use.
