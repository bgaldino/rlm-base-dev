---
article_id: ind.sf_contracts_extract_the_arn_value_for_a_user.htm
title: Extract the ARN Value for a User
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_extract_the_arn_value_for_a_user.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configure_a_named_credential_and_external_credential_for_contracts_ai.htm
fetched_at: 2026-10-13
---

# Extract the ARN Value for a User

To extract the ARN value, use the same user you created to extract the access keys.

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
Click Access management | Users, and then click the user name you created.
Copy and save the ARN of the user from the Summary section.
Click Access management | Roles, and then click Create role.
Type texttract in the Service or use case search field, and then select Texttract.
Click Next, and then click Next.
In the Role details section, enter a role name.
Click Create role.
Click Access management | Roles, and then click the role you created.
To attach texttract service to this role, click the Permission tab | Add permissions, and then select Attach policies.
Type texttract in the search field, and then select the AmazonTextractFullAccess policy name.
Click Add Permissions.
