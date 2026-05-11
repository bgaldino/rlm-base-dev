---
article_id: ind.billing_configure_salesforce_payments.htm
title: Configure Salesforce Payments
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_configure_salesforce_payments.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Configure Salesforce Payments

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Configure Salesforce Payments

To use Salesforce Payments for financial transactions, set up an Experience Cloud site and enable Payments for your org. Then, use a guided setup to create a merchant account and payment methods.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with Revenue Cloud
The Salesforce Payments feature is available with the Revenue Cloud Billing license, with a cost per transaction model for both native and Bring Your Own payment gateways. Contact your Salesforce account executive for more information.
If you purchased the Revenue Cloud Billing license on or before July 2025, contact your Salesforce account executive to add the Salesforce Payments feature to your existing license.
USER PERMISSIONS NEEDED
To enable and configure Payments features:	Payment Admin permission set
Turn On Salesforce Payments

Set up an Experience Cloud site that's used as a data channel between the payment provider and the Salesforce Payments feature.

After you set up an Experience Cloud site, make sure that Salesforce Payments is enabled.

NOTE

You can automate the process of setting up an Experience Cloud site and enabling Salesforce Payments by using the Commerce Setup Assistant.

Configure Account-Based Sharing for Payments and Refunds Objects

To make sure that only users working with a specific account have access to its payments and refunds details, turn on Share Payment Accounts on the Billing Settings page. This feature grants users access to payment and refund details related to the corresponding Account record. For example, if a user has Read access to the Account record object, they also get Read access to the related Payments and Refunds records.

See PaymentsSharingSettings Metadata API.

SEE ALSO
Trailhead: Set Up Salesforce Payments
Assign Permissions to Access Billing Features
Set Up Merchant Accounts
Automatic Creation of Payment Schedules and Payment Schedule Items
Payment Batch Run Overview
