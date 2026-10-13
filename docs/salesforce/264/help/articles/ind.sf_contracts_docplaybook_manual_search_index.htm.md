---
article_id: ind.sf_contracts_docplaybook_manual_search_index.htm
title: Manually Create a Document Playbook Search Index
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_docplaybook_manual_search_index.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_docplaybook_manual_index.htm
fetched_at: 2026-10-13
---

# Manually Create a Document Playbook Search Index

Create the hybrid search index that Salesforce uses to match contract sections against document playbook content during risk analysis. Complete this task after you configure the Document Playbook data streams.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To manually create a Document Playbook search index:	

Data Cloud Architect [Home Org]

OR

Data Cloud One [Companion Org]

AND

Document Playbook Designer, CLM Admin User, and Contracts AI User

Before you begin, configure the Document Playbook data streams. See Manually Configure Document Playbook Data Streams.

TIP If you need custom chunking, embedding, or preprocessing behavior, clone the data kit's index and modify it instead of creating an index from scratch. Cloning preserves the field mappings that the Document Playbook data streams depend on.
Create the search index.
From the App Launcher, find and select Data Cloud.
On the Search Indexes tab, click New, and select Advanced Setup.
Search Index Builder opens in a new tab.
For Search Type, select Hybrid Search.
Select the data space that contains Document Playbook data.
For data model object label, select Document Playbook Version.
Click Include File Attachments, and select Content Document Version.
In the File Extension list, delete all extensions except pdf, docx, and xlsx, and then click Next.
For parsing and pre-processing, keep the default sections, and click Next.
Click Manage Fields, and select Status.
Save your changes.
For Embedding Model, select E5 Large V2 Embedding Model, and then click Next.
Under filtering, expand the Direct Fields and Related Fields sections, and then drag the corresponding fields into Selected fields.
Modify the field API name for Document Playbook to make it unique.
RELATED FIELD SECTION	RELATED DMO LABEL	RELATED DMO FIELD LABEL	RELATIONSHIP PATH	FIELD API NAME
Direct Fields	Document Playbook	Document Playbook Id	Document Playbook.Document Playbook Id > Document Playbook Version.Document Playbook	DocumentPlaybookId__c
 	Document Playbook Version	Document Playbook Version Id	NA	Id__c
 	Document Playbook Version	Status	NA	Status__c
Related Fields	Content Document Relationship	Content Document	Content Document Relationship.Related Item > Document Playbook Version.Document Playbook Version Id	ssot__ContentDocumentId__c
 	Content Document Relationship	Data Source	NA	DataSource__c
Click Next.
Review the configuration, and then save and build the search index.
Return to Document Playbook Settings. In Document Playbook Indexing, select the new search index from the Search Index list.
Save your changes.
TIP Before you use a manually configured index in production, test it with playbooks and contract documents that have tracked changes, and verify risk analysis results.
NOTE After the index is built, Document Playbook Version chunk and Document Playbook Version index DLOs are created. Segmented content is stored in the chunk object, and numeric relevance scores are stored in the index object.
