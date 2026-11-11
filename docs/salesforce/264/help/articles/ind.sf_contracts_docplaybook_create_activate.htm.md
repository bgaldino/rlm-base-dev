---
article_id: ind.sf_contracts_docplaybook_create_activate.htm
title: Create a Document Playbook and Activate a Version
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_docplaybook_create_activate.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_docplaybook_work_with.htm
fetched_at: 2026-10-13
---

# Create a Document Playbook and Activate a Version

To iterate on a playbook document before making it live, create the playbook shell first, then add and activate a version, and assign the playbook to a Contract record type. Each action is a separate step, so you can pause between them to review or update the document.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To create and activate document playbooks:	Document Playbook Designer

Before you begin:

Make sure your Salesforce admin has completed document playbook setup and sharing. See Set Up Document Playbook.
Make sure you have a PDF, DOCX, or XLSX guidelines file no larger than 100 MB.
Make sure your guidelines are organized into clear sections for rules, preferred positions, fallback clauses, and approval guidance.
NOTE To create the playbook, version, and assignment in a single action, see Create a Document Playbook by Uploading a File.
From the App Launcher, find and select Document Playbooks.
The Document Playbooks home page lists every playbook that you have access to.
Click New Playbook.
Enter a name and description.
Save your changes.
The playbook is created in Draft status. Target Object and Record Type show as Unassigned.
Return to the Document Playbooks list view, and click New Version next to the playbook you created.
Enter the version details.
Enter a description.
In Playbook Document, attach a PDF, DOCX, or XLSX file up to 100 MB.
Click Done.
Save your changes.
From the version's Actions menu, click Activate.
The version status changes to Active, and Salesforce sets the parent playbook to Active.
From the playbook's Actions menu, click Assignment, and select the target object and target record type.
Risk analysis uses the assignment to identify the playbook for a contract's object and record type.
Save your changes.
The record page for the new assignment opens.

To retire a playbook, archive it. Archiving the playbook archives all of its active and archived versions. Draft versions remain in draft.
