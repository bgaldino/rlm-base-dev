---
article_id: ind.sf_contracts_reviewer_type_and_access_mode.htm
title: Reviewer Type and Access Mode in Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_reviewer_type_and_access_mode.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_review.htm
fetched_at: 2026-11-23
---

# Reviewer Type and Access Mode in Salesforce Contracts

Salesforce Contracts enables different types of reviewers to collaborate on the documents with varying access permissions.

The reviewer types are:

Linked reviewer - Reviewers with corresponding Salesforce credentials. They can work with the clauses and sections within the documents, perform actions such as insert, delete, and update clauses and sections, and also modify the content of the document.

Non-linked reviewer - Reviewers without corresponding Salesforce credentials. They can update the content of the document, and delete and update clauses. They can add, delete and update the sections. However, they can’t add clauses.

Depending on their access type, a reviewer can perform various actions on the document.

PERMISSIONS	READ-ONLY(CAN VIEW)	FULL ACCESS(CAN EDIT)
View document	Yes	Yes
Modify document content	No	Yes
Edit/Delete/Resolve comments	No	Yes
Add new comments	No	Yes
Reply to comments	No	Yes
Add/Update document content	No	Yes
Add/Update clauses	No	Yes
Add/Edit/Delete Sections	No	Yes

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_reviewer_type_and_access_mode.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
