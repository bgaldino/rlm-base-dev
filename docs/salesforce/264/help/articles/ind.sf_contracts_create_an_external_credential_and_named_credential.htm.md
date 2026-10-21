---
article_id: ind.sf_contracts_create_an_external_credential_and_named_credential.htm
title: Create an External Credential and Named Credential
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_an_external_credential_and_named_credential.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configure_a_named_credential_and_external_credential_for_contracts_ai.htm
fetched_at: 2026-10-13
---

# Create an External Credential and Named Credential

To use Contracts AI for the extraction of contract details, create an external credential.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 
To enable Einstein and Contracts AI settings	

Contracts AI Clause Designer

AND

Prompt Template Manager

AND

NLP Service

AND

Scoring Framework Admin

From Setup, in the Quick Find box, enter Named Credentials, and then select Named Credentials.
Click the External Credentials tab.
To create an external credential, click New.
Complete these fields.
Label: A user-friendly name for the external credential that’s shown in Salesforce, such as in list views.
Name: A unique identifier that refers to this external credential from callout definitions and through the API.
Authentication Protocol: AWS Signature Version 4
Service: texttract
Region: us-west-2
AWS Account Id: Account ID you copied from the Dashboard | AWS Account section.
Save your changes.
Configure principals for the external credential.
Open the external credential that you created.
In the Principals section, click New.
Complete these fields.

Parameter Name: A unique identifier that’s used to refer to this principal.

Access Key: Paste the access key you copied from the user you created.

Access Secret: Paste the access secret you copied from the user you created.

IAM Role ARN: Paste the access secret you copied from the role you created.

Save your changes.
Create a named credential for your external credential.
From Setup, in the Quick Find box, enter Named Credentials, and then select Named Credentials.
To create a named credential, click New.
Complete these fields.

Label: A user-friendly name for the named credential that’s shown in Salesforce, such as in list views.

Name: A unique identifier that refers to this named credential from callout definitions and through the API.

URL: Enter the root URL of the callout endpoint. The URL must begin with https:// and can include a path, but not a query string. For example, enter a URL such as https://www.salesforce.com.

External Credential: Select the external credential you created.

Save your changes.

See Also

Create and Edit an AWS Signature v4 External Credential

Create and Edit a Named Credential
