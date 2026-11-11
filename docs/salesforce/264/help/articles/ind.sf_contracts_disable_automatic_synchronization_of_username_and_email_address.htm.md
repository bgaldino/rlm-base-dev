---
article_id: ind.sf_contracts_disable_automatic_synchronization_of_username_and_email_address.htm
title: Disable Automatic Synchronization of Username and Email Address Using Guided Setup
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_disable_automatic_synchronization_of_username_and_email_address.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configure_an_auth_provider.htm
fetched_at: 2026-10-13
---

# Disable Automatic Synchronization of Username and Email Address Using Guided Setup

By default, when you link Salesforce to Microsoft Azure, Salesforce automatically updates your Salesforce username and email address with your Microsoft Azure account details. You can turn off this automatic update to retain the username and email address that you have used in Salesforce.

REQUIRED EDITIONS
REQUIRED
EDITIONS
Available in:	Lightning Experience
Available in:	Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To access the Microsoft 365 and Azure Integration Guided Setup	CLM Admin User
In Setup, find and select Auth. Providers.
Select the auth provider that you've configured.
Click the Registration Handler value and click Edit.
Search for the updateUser method and remove it or comment out this code.
//u.email = data.email;
//u.lastName = data.lastName;
//u.firstName = data.firstName;

Save your changes.
