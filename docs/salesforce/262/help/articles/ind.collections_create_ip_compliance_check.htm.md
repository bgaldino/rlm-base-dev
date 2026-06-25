---
article_id: ind.collections_create_ip_compliance_check.htm
title: Create and Configure Integration Definitions and Named Credentials
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_create_ip_compliance_check.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_compliance_setup.htm
fetched_at: 2026-06-21
---

# Create and Configure Integration Definitions and Named Credentials

To connect Salesforce with an external system, create integration definitions. APIs work with the integration definitions to perform operations in both Salesforce and the external system. Link the prebuilt APEX class to the integration definition.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To create Apex Defined integration definitions:	Customize Application
Create an integration definition with these details, save the changes, and activate the integration definition.
Type	Apex Defined
Name	PostComplianceDetails
Apex Class	fsc_collection_apex.RequestComplianceIntegrationProvider
Plain Client Id Attribute	Copy the consumer key from the local external client application that you created earlier.
If you plan to change the integration definition name, make sure that you update the changed name in the remote action that's called by the integration procedure, Collections_CheckOutboundCallComplianceForBorrowerContacts.
Create an external credential with these details, and save the changes. Make sure that you create a Principal.
Authentication Protocol	OAuth 2.0
Name	PostComplianceDetail
Authentication Flow Type	Client Credentials with Client Secret Flow
Identity Provider URL	Copy the Callback URL from the external auth identity provider that you created earlier and paste it here.
Create a named credential with these details, and save the changes.
FIELD	DESCRIPTION
Label	postComplianceNC
Name	postComplianceNC
URL	

Provide the API end point of the compliance application. Append the compliance query string and a specific path in the callout definition’s reference to the named credential as shown in this example.

https://orgfeature.cumuluscapital.com/services/data/v64.0/connect/compliance/procedure/CollectionsAndRecovery/evaluate

Enabled for Callouts	Turn on this setting
External Credential	Select the external credential that you created earlier
To link the new external credential principal to permission sets or user profiles so that users can make callouts by using the named credential, create a permission set and add the external credential principal.
To enable any user performing an authenticated callout, in the new permission set, provide View All Fields and Modify All Records object permissions to the User External Credentials object.
Assign the new permission set to the user performing an authenticated callout.
