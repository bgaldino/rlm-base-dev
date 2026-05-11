---
article_id: ind.billing_saved_payment_methods.htm
title: Configure Saved Payment Methods for Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_saved_payment_methods.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Configure Saved Payment Methods for Agentforce Revenue Management

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Configure Saved Payment Methods for Agentforce Revenue Management

Collect one-time or scheduled recurring payments by securely saving the payment methods of your customers, rather than manually entering payment method details each time a payment is processed. Save various payment methods from native or third-party payment gateways, and set a default saved payment method for each account.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with Revenue Cloud
The Salesforce Payments feature is available with the Revenue Cloud Billing license, with a cost per transaction model for both native and Bring Your Own payment gateways. Contact your Salesforce account executive for more information.
If you purchased the Revenue Cloud Billing license on or before July 2025, contact your Salesforce account executive to add the Salesforce Payments feature to your existing license.
USER PERMISSIONS NEEDED
To create saved payment methods:	Payment Operations User permission set
Prerequisites

Before saving payment methods for accounts, complete these steps.

Complete the setup steps.
To enable standard users to create saved payment methods by using the Merchant Account records created by your Payment admins, select the default internal access of the Merchant Account object to Public Read Only.
Add the Dynamic Related List–Single component to the Saved Payment Method tab of Account records, and select Saved Payment Methods as the related list.
Create Saved Payment Methods

You can save multiple payment methods for a single account or save the same payment method for different customer accounts. You can also choose to set a default payment method for an account.

From the App Launcher, find and select Billing, and then click Accounts.
Open the Account record for which you want to create a saved payment method.
On the Saved Payment Methods tab, select the merchant account that you want to use for receiving payments from the account.
You can save payment methods for different customer accounts with the same merchant account.
Select the payment method that you want to add such as a credit card, bank account, or any other third-party payment method, and then enter the required details.
The combination of merchant account and payment method for an account must be unique.
Optionally, set a payment method on your native payment gateway as the default payment method for the account.
Save your work.

The saved payment method appears in the Saved Payment Methods related list of the Saved Payment Methods tab.

If the saved payment method you’re creating has the same merchant account and payment method details as an existing record, but contains changes to other details, such as the name on the card, the details of the existing Saved Payment Method record is updated.

NOTE You can create saved payment methods for MOTO payments in native payment gateways only.
