---
article_id: ind.sf_contracts_ms365_minimum_pri_named_credential.htm
title: Create a Named Credential for Salesforce Contracts Connector for Word Add-in Manually Through Minimum Privilege Setup
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_ms365_minimum_pri_named_credential.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_ms365_minimum_pri_overview.htm
fetched_at: 2026-10-13
---

# Create a Named Credential for Salesforce Contracts Connector for Word Add-in Manually Through Minimum Privilege Setup

Use a Named Credential with External Document Storage Configuration to ensure all generated contract documents and templates are stored in a single, centralized Microsoft OneDrive location without requiring elevated privileges. Only an Office 365 license needs to be assigned to the integration user.

REQUIRED EDITIONS
NOTE To use a guided setup to integrate Microsoft 365 and Azure, see Set Up Microsoft 365 and Azure Integration Using Guided Setup.
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To create Named Credential:	CLM Admin User
From Setup, in the Quick Find box, enter Named Credentials, and then select Named Credentials.
Click the dropdown next to New, and select New Legacy.
Enter MicrosoftApp as the label.
The Name field is automatically filled with MicrosoftApp.
Enter https://graph.microsoft.com/v1.0 as the URL.
Select Named Principal as the identity type.
Select OAuth 2.0 as the authentication protocol.
Select MicrosoftApp as the authentication provider.
Select the Auth.Provider you created while configuring the Auth Provider for Microsoft App.
Select Start Authentication Flow on Save.
Make sure that Generate Authorization Header is selected.
Save your changes.

After the successful authentication of Microsoft Azure, the named credential's authentication status changes to Authenticated.

NOTE If your Microsoft account is already authenticated in your current browser session, you can successfully authenticate your named credential. If it isn't, authenticate your named credential by using your Microsoft account credentials.

Verify that the named credential is authenticated correctly before proceeding further.

SEE ALSO
Create or Edit a Named Credential
