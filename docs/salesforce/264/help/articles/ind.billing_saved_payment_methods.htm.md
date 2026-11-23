---
article_id: ind.billing_saved_payment_methods.htm
title: Configure Saved Payment Methods for Revenue Cloud
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_saved_payment_methods.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payments.htm
fetched_at: 2026-11-23
---

# Configure Saved Payment Methods for Revenue Cloud

Collect one-time or scheduled recurring payments by securely saving the payment methods of your customers, rather than manually entering payment method details each time a payment is processed. Save various payment methods from native or third-party payment gateways, and set a default saved payment method for each account.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Cloud
To integrate a native payment gateway, you have two options. Use Salesforce Payments, which runs on Stripe and is available with the the Revenue Cloud Billing license on a cost-per-transaction basis. Or, connect your own Adyen account, contracted directly with Adyen.
 
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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_saved_payment_methods.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
