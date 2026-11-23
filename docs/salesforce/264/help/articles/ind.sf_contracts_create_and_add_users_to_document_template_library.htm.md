---
article_id: ind.sf_contracts_create_and_add_users_to_document_template_library.htm
title: Create a Document Template Library for Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_and_add_users_to_document_template_library.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_post-install_steps_for_salesforce_contracts_winter_23.htm
fetched_at: 2026-11-23
---

# Create a Document Template Library for Salesforce Contracts

Create the Docgen Document Template Library that stores the Document Templates you create and share them between users.

The admin user who completes this procedure must have Salesforce CRM Content User selected on their User Detail page in Setup. The Salesforce CRM Content User checkbox is present if Salesforce CRM Content is enabled in Setup.To enable users to access the files in the Document Template Library, you must add them as members. Or, you can create a group, grant access to the group, and add users to that group.

In the upper-right corner, click your profile name and select Switch to Salesforce Classic.
NOTE If you create the library in Lightning Experience, the uploaded document template isn't linked to the library, and document generation returns an error.
Click the plus icon to open a list of all tabs, then click Libraries.
NOTE You can also reach the Libraries page with a URL. For example, if your org domain is acme, go to this URL in your browser:
https://acme.my.salesforce.com/sfc/#workspaces
Click New.
In the Name field, enter Docgen Document Template Library.
In the Unique Name field, enter DocgenDocumentTemplateLibrary.
Click Save and Add Members.
To generate documents using Omniscripts, Contracts, or any sObjects like Opportunity, Quote, Order, etc., users need to be added to the library.
Select each of the users that you created in the previous set, and click add to move it to the other column.
If you don't see your username, it means you're already added.
Click Next.
Optional: Change the library permissions for the user.
The administrator level has read, write, and edit permissions, and the Author level has read and write permissions.
Save your changes.
Click Switch to Lightning Experience.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_and_add_users_to_document_template_library.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
