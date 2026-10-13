---
article_id: ind.sf_contracts_create_a_named_credential_for_docusign.htm
title: Create a Named Credential for DocuSign
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_a_named_credential_for_docusign.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_workflow_to_setup_esignature_for_contract_object.htm
fetched_at: 2026-10-13
---

# Create a Named Credential for DocuSign

Add a Named Credential using auth provider information to create a secure connection. Omniscripts and Integration Procedures use these credentials to connect with DocuSign.

You must add an Auth Provider for DocuSign. For more information, see Create an Auth Provider for Docusign.

From Setup, in the Quick Find box, enter Named Credentials, and then select Named Credentials.
Click the dropdown next to New, and select New Legacy.
For Label and Name, enter DocuSignAuthProvider.

Make a note of this name, you need to add it in the Create Electronic Signature Configurations > Callout Named Credential Config Type.

For URL, enter https://demo.docusign.net for UAT or https://{server}.docusign.net for production.
To find the server name in your DocuSign account, go to Settings > Apps and Keys. The BaseURI includes the site information.
For Identity Type, select Named Principal.
For Authentication Protocol, select OAuth 2.0.
For Authentication Provider, select DocuSign.
For Scope, enter refresh_token full.

Enter the two values separated by a space. These must match the scopes you configured in the auth provider: refresh_token enables automatic token renewal and full grants full DocuSign API access.

Select Start Authentication Flow on Save.
If Generate Authorization Header is not selected, select it.
Click Save. A DocuSign login page launches in a new tab.
From the DocuSign login page, log in to DocuSign.
NOTE If the session is already authenticated with DocuSign Account, then you might not need to log in.

This changes the Named Credential's Authentication Status to Authenticated.
