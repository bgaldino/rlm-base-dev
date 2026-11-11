---
article_id: ind.sf_contracts_create_an_auth_provider_for_docusign.htm
title: Create an Auth Provider for DocuSign
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_an_auth_provider_for_docusign.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_workflow_to_setup_esignature_for_contract_object.htm
fetched_at: 2026-10-13
---

# Create an Auth Provider for DocuSign

Add an Auth Provider credential for DocuSign in Salesforce to create a secure connection. Omnistudio uses these credentials to fetch document templates from DocuSign.

Before you begin, complete these steps in your DocuSign account. You need the Integration Key and Secret Key values to configure the auth provider in Salesforce.

Create a DocuSign developer account if you don't have one. See DocuSign Developer Quickstart.
From your DocuSign account, go to Settings > Apps and Keys and create an application that uses Authorization Code Grant as the authentication type. See Apps and Keys.
Copy the Integration Key for your application. You enter this value as the Consumer Key in Salesforce.
Add a Secret Key for your application and copy it. You enter this value as the Consumer Secret in Salesforce.

After completing those prerequisites, follow these instructions to complete the auth providers set up for DocuSign:

In your Salesforce org, from Setup, enter Auth. Providers in the Quick Find box, then select Auth. Providers.
Click New, and select Open ID Connect.
Name the Auth Provider DocuSign, and enter DocuSign in the URL Suffix field.
In the Consumer Key field, enter your DocuSign App's Integration Key.
For Consumer Secret, enter your DocuSign App's Secret Key.
For Authorize Endpoint URL, enter https://account-d.docusign.com/oauth/auth for developer account, and https://account.docusign.com/oauth/auth for production account.
For the Token Endpoint URL, enter https://account-d.docusign.com/oauth/token for developer account, and https://account.docusign.com/oauth/token for production account.
For Default Scopes, enter refresh_token full.

Enter the two values separated by a space. The refresh_token scope allows the connection to renew automatically without re-authentication. The full scope grants full API access to DocuSign.

Select Send access token in the header.
Select Include Consumer Secret in API Responses.
Click Save. This saves your auth provider and generates Salesforce Configuration URLs.
Copy the Callback URL.
From your DocuSign account, in the App Details panel, click Edit.
For Redirect URIs, paste the Callback URL.
Click Save.
