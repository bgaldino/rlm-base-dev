---
article_id: ind.sf_contracts_configure_a_named_credential_and_external_credential_for_contracts_ai.htm
title: Configure a Named Credential and External Credential for Industries Einstein AI Extraction
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_configure_a_named_credential_and_external_credential_for_contracts_ai.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_enable_einstein_and_contracts_ai_settings.htm
fetched_at: 2026-10-13
---

# Configure a Named Credential and External Credential for Industries Einstein AI Extraction

A named credential stores your AWS account information. You can create a named credential in Setup. To extract contract details using Contracts AI, you must first extract values such as access keys, account ID, ARN, and IAM role from your AWS account. Use these AWS values to create an external credential and named credential. Additionally, create and assign a permission set to users.

Prerequisite: An active AWS account.

See Also

Named Credentials

Extract the AWS Account ID and Access Keys
The 12-digit number known as the AWS account ID is a unique identifier for your AWS account. The AWS access keys are specific to a user. Create a user, and then use the access keys to create the external credential.
Extract the ARN Value for a User
To extract the ARN value, use the same user you created to extract the access keys.
Attach a Role to a User
After you create a role and a user, attach the role to the user.
Create an External Credential and Named Credential
To use Contracts AI for the extraction of contract details, create an external credential.
Create a Permission Set for External Credential Principal Access
Create a permission set for the external credential principal access and assign the permission set to the autoproc user and the admin users responsible for initiating the contract extraction.
