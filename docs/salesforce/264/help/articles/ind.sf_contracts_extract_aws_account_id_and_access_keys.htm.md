---
article_id: ind.sf_contracts_extract_aws_account_id_and_access_keys.htm
title: Extract the AWS Account ID and Access Keys
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_extract_aws_account_id_and_access_keys.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configure_a_named_credential_and_external_credential_for_contracts_ai.htm
fetched_at: 2026-10-13
---

# Extract the AWS Account ID and Access Keys

The 12-digit number known as the AWS account ID is a unique identifier for your AWS account. The AWS access keys are specific to a user. Create a user, and then use the access keys to create the external credential.

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

Log in to your AWS account.
In the Dashboard, copy and save the Account ID from the AWS Account section.
Click Access management | Users, and then click Create user.
Enter a user name, and then click Next.
Select Attach policies directly.
Type texttract in the search field, and then select the AmazonTextractFullAccess policy name.
Click Next.
Click Create user.
Click the user name you created.
Click Create access key.
Select the Command Line interface (CLI) use case.
Select I understand the above recommendation and want to proceed to create an access key confirmation. Click Next.
Click Create access key.
Copy and save the Access key.
You can’t retrieve the access key later.
Click Show.
Copy and save the secret access key.
Click Done.
