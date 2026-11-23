---
article_id: ind.billing_configure_salesforce_payments.htm
title: Configure Salesforce Payments
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_configure_salesforce_payments.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_setup_salesforce_payments_features.htm
fetched_at: 2026-11-23
---

# Configure Salesforce Payments

To use Salesforce Payments for financial transactions, set up an Experience Cloud site and enable Payments for your org. Then, use a guided setup to create a merchant account and payment methods.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Cloud
To integrate a native payment gateway, you have two options. Use Salesforce Payments, which runs on Stripe and is available with the the Revenue Cloud Billing license on a cost-per-transaction basis. Or, connect your own Adyen account, contracted directly with Adyen.
 
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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_configure_salesforce_payments.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
