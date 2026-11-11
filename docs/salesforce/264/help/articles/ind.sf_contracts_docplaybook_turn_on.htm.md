---
article_id: ind.sf_contracts_docplaybook_turn_on.htm
title: Turn On Document Playbook Management
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_docplaybook_turn_on.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_docplaybook_setup.htm
fetched_at: 2026-10-13
---

# Turn On Document Playbook Management

When you turn on Document Playbook, playbook content is stored and indexed in Data 360 (formerly Data Cloud), so risk analysis can retrieve the most relevant guidance for the record type of the contract under review. Document Playbook requires a Data 360 license.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To turn on Document Playbook:	CLM Admin User

Complete these prerequisites before you set up Document Playbook.

Set up Salesforce Contracts: Turn on Salesforce Contracts and make sure that your org has the required Contracts AI or Document Playbook licenses. See Enable Salesforce Contracts.
Set up Data 360 (Data Cloud): Turn on Data 360 to ingest and index Document Playbook content. Make sure that the required Data 360 licenses are provisioned before you continue. See Turn On Data Cloud. A Data 360 license is required to turn on Document Playbook.
Assign the required permissions: Assign permissions based on the user persona. See Assign Document Playbook Licenses and Permission Sets.
Set up Einstein Generative AI: Turn on Einstein Generative AI to support natural language search. See Set Up Einstein Generative AI.
From Setup, in the Quick Find box, enter Document Playbook, and then select Document Playbook Settings.
If the setting is unavailable, your org isn't licensed for Data 360, which is required.
Turn on Document Playbook Management.

Salesforce creates or reactivates the Document Playbook integration user and assigns the Data Cloud User permission set to that user if the permission set is available. The Document Playbooks, Document Playbook Versions, and Document Playbook Assignments objects become available in the App Launcher to users with Document Playbook Designer access.

You can now ingest playbook content into Data 360. See Deploy the Document Playbook Data Kit.
