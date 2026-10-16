---
article_id: ind.sf_contracts_create_a_named_credential_for_sf_connector_for_word_add-in_app.htm
title: Create a Named Credential for Salesforce Contracts Connector for Word Add-in Manually
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_a_named_credential_for_sf_connector_for_word_add-in_app.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_integrate_microsoft_365_azure_with_salesforce.htm
fetched_at: 2026-10-13
---

# Create a Named Credential for Salesforce Contracts Connector for Word Add-in Manually

Create a named credential to connect Salesforce Contracts to External Document Storage. The authenticating user is required to be the same user who created the Microsoft Azure app and to have User Administrator permissions in Azure.

NOTE This step is part of manually integrating Microsoft 365 Azure with Salesforce. To refer to guided setup, see Set Up Microsoft 365 and Azure Integration Using Guided Setup.
REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 
To create Named Credential:	System Administrator with Azure Tenant Administrator access
From Setup, in the Quick Find box, enter Named Credentials, and then select Named Credentials.
Click the dropdown next to New, and select New Legacy.
Don’t click New.
Enter MicrosoftApp as the label.
The Name field automatically gets filled with MicrosoftApp.
Enter https://graph.microsoft.com/v1.0 as the URL.
Select Named Principal as the identity type.
Select OAuth 2.0 as the authentication protocol.
Select MicrosoftApp as the authentication provider.
Select the Auth.Provider you created while configuring the Auth Provider for Microsoft App..
Select Start Authentication Flow on Save.
Make sure that the Generate Authorization Header is selected.
Save your changes.

The named credential's authentication status changes to Authenticated after the successful authentication of Microsoft Azure.

NOTE If your Microsoft account is already authenticated in your current browser session, you can successfully authenticate your Named Credential. If not, authenticate your Named Credential by using your Microsoft account credentials.

See Also

Configure an Auth Provider for Salesforce Contracts Microsoft Integration

Create or Edit a Named Credential

Verify that the named credential is authenticated correctly before proceeding further.
