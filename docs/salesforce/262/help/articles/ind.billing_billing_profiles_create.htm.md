---
article_id: ind.billing_billing_profiles_create.htm
title: Create Billing Profiles
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_billing_profiles_create.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Create Billing Profiles

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Create Billing Profiles

Cater to your customers' billing preferences and business needs by creating billing profiles for their accounts. Define multiple billing profiles for an account to manage diverse billing needs, each with its own billing details, payment terms, and contacts. Set a default billing profile for accounts to easily access your customers' preferred billing day of the month, billing address, billing contact, and other details. With billing profiles, sales representatives no longer need to enter this information for each transaction, saving time and effort.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create billing profiles:	

You must have ONE of these permission sets:

Billing Admin
Billing Operations User
Payment Admin
Payment Operations User
Credit Memo Operations User
NOTE

On Account record pages in the Billing app, the Billing Profile related list on the Billing Profile tab has been updated in Winter ’26. It now displays Billing Accounts records, replacing the Account Billing Accounts records shown in Summer ’25. If you have customized the Account record pages, this change is not automatically applied during the upgrade. You will consequently encounter an error and the related list will be missing. To fix this issue, edit the customized Account record page to remove the old Account Billing Accounts related list and add the new Billing Accounts related list instead.

Each billing profile corresponds to a billing account record.

From the App Launcher, find and select Billing.
From the navigation bar, click Accounts and open the account for which you want to create a billing profile.
In the Billing Profile section, click New.
In the Information section, enter these details.
Enter a name for the billing account.
The account is autopopulated. You can select a different account for the billing account.
To set the billing account as the default billing profile for the account, select Default Billing Profile.
You can set only one default billing profile for an account.
In the Address section, enter the primary billing address and shipping address.
In the Billing Information section, enter these details.
Enter a bill day of the month and select a contact for billing.
When a billing schedule is generated from any transaction, the bill day of month comes from the billing profile. When a billing schedule is generated from an order, the bill day of month is determined by the period boundary set on the order item.
Select the payment terms.
Select Skip Automatic Payment to disable the automatic processing of payments.
You can also view the saved payment methods associated with the selected account.
In the Email Information section, enter these details.
Select an email template.
Use Default Invoice Email Template or clone and customize the email template based on your business needs.
To send an invoice PDF document with the email, select Attach Invoice Document to Email.
Save your changes.

When processing a transaction, Billing follows the behavior mentioned in this table to determine which values to use.

SCENARIO	BEHAVIOR
Transaction record has the required values.	The values of the transaction are used.
Transaction record doesn't have the required values but is associated with a billing profile.	The values of the associated billing account are used.
Transaction record doesn't have the required values and isn't associated with a billing profile.	The values of the account's default billing profile are used.
Transaction record doesn't have the required values, isn't associated with a billing profile, and the account doesn't have a default billing profile.	The org default values are used.
NOTE Updating an account’s billing profile doesn’t affect the existing billing schedules.

Optionally, to pass the billing profile field to a transaction, complete these steps.

Create a custom lookup relationship field on the order object, and associate it to the billing account object.
In the extended BillingContext context definition, map the out-of-the-box billing profile context tag to this custom lookup field.
