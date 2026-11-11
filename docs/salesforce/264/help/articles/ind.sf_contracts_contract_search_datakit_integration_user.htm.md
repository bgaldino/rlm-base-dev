---
article_id: ind.sf_contracts_contract_search_datakit_integration_user.htm
title: Set Up a Contract Search Integration User for Data Kit Deployment
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_contract_search_datakit_integration_user.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_search_datakit_overview.htm
fetched_at: 2026-10-13
---

# Set Up a Contract Search Integration User for Data Kit Deployment

Create and configure an integration user to control access to contract data in Data Cloud. This user is essential for supporting secure contract search operations.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To configure an integration user:	

Data Cloud Architect [Home Org]

OR

Data Cloud One [Companion Org]

AND

CLM Admin User

AND

Contracts AI User

Create an integration user in the Home org.
In Setup, find and select Users.
Click New User.
Set the user license to Salesforce Integration.
Set the profile to Minimum Access – API Only Integrations.
Update the required fields, and save your changes.
In the Permission Set Assignments section, click Edit Assignments.
Move Data Cloud User from Available Permission Sets to Enabled Permission Sets.
Save your changes.
Configure the integration user for contract search in the Home org.
In Setup, find and select Contract Search.
Select Enable Contract Search with AI.
Set the Search Index to Contract Document Search.
For contract search integration user, select the integration user you created.
Save your changes.
[Optional] Create an integration user in the Companion org.
In Setup, find and select Users.
Click New User.
Set the user license to Salesforce Integration.
Set the profile to Minimum Access – API Only Integrations.
Update the required fields, and save your changes.
In the Permission Set Assignments section, click Edit Assignments.
Move Data Cloud One from Available Permission Sets to Enabled Permission Sets.
Save your changes.
[Optional] Configure the integration user for contract search in the Companion org.
In Setup, find and select Contract Search.
Select Enable Contract Search with AI.
Set the Search Index to Contract Document Search.
For contract search integration user, select the integration user you created.
Save your changes.

After you set up a contract search integration user for data kit deployment, you can also optionally Set Up Data Governance for Contract Search For Manual and Data Kit Setup.
