---
article_id: ind.sf_contracts_configure_an_auth_provider.htm
title: Configure an Auth Provider for Salesforce Contracts Using Guided Setup
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_configure_an_auth_provider.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_set_up_microsoft_365_and_azure_integration_using_guided_setup.htm
fetched_at: 2026-10-13
---

# Configure an Auth Provider for Salesforce Contracts Using Guided Setup

Set up an Auth Provider in Salesforce to establish a secure connection with Microsoft 365 and Azure. This process includes creating or selecting an auth provider, configuring the callback URL, managing email notificatinos, and testing the connection to ensure successful integration.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To access the Microsoft 365 and Azure Integration Guided Setup	CLM Admin User
NOTE Avoid refreshing your browser during the guided setup, as doing so may disrupt the Auth Provider configuration.
In the guided setup, access the Auth Provider Setup by expanding Set Up the Auth Provider.
Create or select an Auth Provided:
To create a New Auth Provider:
Click New Auth Provider.
In the Authentication Provider Details, enter:
Name: Enter an auth provider name.
Consumer Key: Enter your Azure App’s Application (client) ID.
Consumer Secret: Enter your Azure App’s Client Secret Value.
Execute Registration As: Select your system admin account.
To select an existing auth provider:
If you select an existing auth provider, only auth providers previously created for the Microsoft 365 integration are available.
Click Existing Auth Provider.
In the Name, select an auth provider name.
Configure the callback URL:
In the Guided Setup, click the copy icon to copy the callback URL.
Open your Microsoft Azure account, and click Overview.
Click Add a Redirect URL next to Redirect URLs.
Select Add a platform > Web.
Paste the callback URL in Redirect URIs.
Select Access tokens (used for implicit flows) and ID tokens (used for implicit and hybrid flows)
Click Configure.
If you have set up a partner community, go to the Auth Provider in Salesforce org.
From the Experience Cloud Sites section, copy the callback URL.
Open your Microsoft Azure account, and click Authentication.
Go to Web > Redirect URLs, and click Add URL.
Enter the Experience Cloud Site callback URL (copied previously), and save your changes.
Test the Connection:
When testing the connection, you'll be prompted to provide a business justification and must request consent from a Global Administrator. The Global Administrator will receive an email with the request details and can grant the required consent. If you continue to set up a Named Credential without obtaining consent, you'll see the same consent prompt again during the Named Credential authentication step, where you'll need to provide the business justification once more.
Click Test Connection to verify the configuration.
Confirm that all details, such as name, provider, and ID, are correctly populated. If the details that appear are similar to the following image, select Yes.
If you encounter an error, select No. Check the error messages and follow the steps mentioned in the Guided Setup to resolve each issue.
To test the connection after you fix the errors, click Test Connection. To reset Auth Provider details, click Start Over.
Test the connection and, when the connection is successful, click Mark as Done.
Disable Automatic Synchronization of Username and Email Address Using Guided Setup
By default, when you link Salesforce to Microsoft Azure, Salesforce automatically updates your Salesforce username and email address with your Microsoft Azure account details. You can turn off this automatic update to retain the username and email address that you have used in Salesforce.
