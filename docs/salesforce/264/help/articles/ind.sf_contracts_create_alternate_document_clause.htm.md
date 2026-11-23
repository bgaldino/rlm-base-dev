---
article_id: ind.sf_contracts_create_alternate_document_clause.htm
title: Create an Alternate Document Clause
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_alternate_document_clause.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_document_clause.htm
fetched_at: 2026-11-23
---

# Create an Alternate Document Clause

Alternate clause provide flexible for specific circumstances and can be used to replace a main clause or an another alternate clause. You can create multiple alternate clauses.

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

From the App Launcher, find and select the Document Clause Sets tab.
Select the document clause set that you want to create the clause for.
For the clause that you want to create an alternate for, click Add Alternate Clause .
Enter a name for the clause. By default, the name is the same as the document clause set name.
(Optional) Enter a clause description.
Select the content format.
Enter the clause content.
In Tokens, click +. In the New Token window, select Placeholder Token or Merge Token, enter the remaining details, and click Add.
To put the token in the clause content, click Insert.
Save your changes.
NOTE After you save the clause, Salesforce populates two read-only fields. Copy the value that you need into the document template during template creation. Templates that reference a clause with Latest Clause Template Identifier automatically pick up the new active version. Templates that reference a specific version with a Clause Template Version Identifier resolve to that version, even after it’s archived. See Tokens for Document Clauses and Document Templates.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_alternate_document_clause.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
