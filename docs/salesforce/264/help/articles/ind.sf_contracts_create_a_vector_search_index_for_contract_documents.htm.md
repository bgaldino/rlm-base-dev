---
article_id: ind.sf_contracts_create_a_vector_search_index_for_contract_documents.htm
title: Create a Vector Search Index for Contract Documents for Manual Contract Search Set Up
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_a_vector_search_index_for_contract_documents.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_search_datakit_manual_overview.htm
fetched_at: 2026-11-23
---

# Create a Vector Search Index for Contract Documents for Manual Contract Search Set Up

Use the Search Index Builder to create a vector search index on Contract Document Version. This index powers AI-driven contract search using semantic matching and document filtering.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To create vector search index:	

Data Cloud Architect [Home Org]

OR

Data Cloud One [Companion Org]

AND

CLM Admin User

AND

Contracts AI User

Prerequisite:Configure Security for PDF Previews

In Data Cloud, click the Search Index tab, and click New.
Click New, then select Advanced Setup.
Search Index Builder opens in a new tab.
Make sure the search type is set to Vector Search.
Under Data Model Object Label, select Contract Document Version, then click Next.
Click Manage Fields, and then select Contract Document Version Status.
Save your changes.
Click Include File Attachments, and then select Content Document Version.
Save your changes.
In the File Extension list, click the Delete icon for all extensions except pdf.
Click Next.
Make sure E5 Large V2 Embedding Model is selected for Embedding Model.
Click Next.
Under Direct Fields, expand Contract Document Version.
Drag Contract, Contract Document Version Id, and Contract Document Version Status into the Selected fields section.
Click Next.
Save your changes.
NOTE Contract Document Version chunk and Contract Document Version index data lake objects are created automatically. Segmented content is stored in the chunk object, and numeric relevance scores are stored in the index object.
SEE ALSO
Search Index Reference

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_a_vector_search_index_for_contract_documents.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
