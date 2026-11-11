---
article_id: ind.sf_contracts_configure_an_integration_user_for_contract_search.htm
title: Configure an Integration User for Manual Contract Search Set Up
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_configure_an_integration_user_for_contract_search.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_search_datakit_manual_overview.htm
fetched_at: 2026-10-13
---

# Configure an Integration User for Manual Contract Search Set Up

Create and configure an integration user to control access to contract data in Data Cloud. This user is required to support secure contract search operations.

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

Create an integration user in Home org.
In Setup, find and select Users.
Click New User.
Set User License as Salesforce Integration.
Make sure Profile is set to Minimum Access – API Only Integrations.
Update the required fields and save your changes.
In the Permission Set Assignments section, click Edit Assignments.
Move Data Cloud User from Available Permission Sets to Enabled Permission Sets.
Save your changes.
Configure the integration user for contract search in Home org.
In Setup, find and select Contract Search.
Select Enable Contract Search with AI.
Set Search Index as Contract Document Version.
For Contract Search Integration User, select the integration user you created.
Save your changes.
