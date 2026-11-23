---
article_id: ind.sf_contracts_attach_a_role_to_a_user.htm
title: Attach a Role to a User
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_attach_a_role_to_a_user.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configure_a_named_credential_and_external_credential_for_contracts_ai.htm
fetched_at: 2026-11-23
---

# Attach a Role to a User

After you create a role and a user, attach the role to the user.

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
Open the role you created.
In the Trust relationships tab, click Edit trust policy.
Click Add next to Add a principal.
Select IAM users as the Principal type.
Paste the user ARN value as the ARN.
Click Add principal.
Copy and save the role ARN value from the role window.
You need this ARN value to create the external named credential.
Click Update policy.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_attach_a_role_to_a_user.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
