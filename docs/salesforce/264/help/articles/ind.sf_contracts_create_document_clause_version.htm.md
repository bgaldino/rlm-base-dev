---
article_id: ind.sf_contracts_create_document_clause_version.htm
title: Create a Version of a Document Clause
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_document_clause_version.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_document_clause.htm
fetched_at: 2026-10-13
---

# Create a Version of a Document Clause

You can have multiple versions of a document clause to track changes over time. A draft version is created each time a change is made to an active clause . When you activate the draft version, the previous version is archived, and the changes made in the new version apply only to new contracts.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 
To create, edit, and search document clause sets and document clauses:	

ClauseUser

OR

ClauseDesignerUser

OR

ClauseDigitalExperienceUser

From the App Launcher, find and select Document Clause Sets.
Select the clause that you want to change.
Click Create New Version.
If a document clause isn't active, the Create New Version button isn't available.
Enter the appropriate information, for example, description, format, and content.
In Tokens, create, insert, edit, or delete tokens for the clause content.
Save your changes.

A draft version of the document clause is created. If you activate the new version, the previous version is archived.

NOTE After you save the clause, Salesforce populates two read-only fields. Copy the value that you need into the document template during template creation. Templates that reference a clause with Latest Clause Template Identifier automatically pick up the new active version. Templates that reference a specific version with a Clause Template Version Identifier resolve to that version, even after it’s archived. See Tokens for Document Clauses and Document Templates.
