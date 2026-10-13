---
article_id: ind.sf_contracts_docplaybook_configure_indexing.htm
title: Configure Document Playbook Indexing
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_docplaybook_configure_indexing.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_docplaybook_setup.htm
fetched_at: 2026-10-13
---

# Configure Document Playbook Indexing

Indexing controls how the playbook content is grouped into segments in Data 360 (Data Cloud). During risk analysis, Salesforce matches each contract section against the most relevant segment. Use the index deployed by the data kit, or create a custom index.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To configure Document Playbook indexing:	

Document Playbook Designer

AND

Data Cloud Architect

On the Document Playbook Settings page, go to the Document Playbook Indexing section.
From Search Index, select the document playbook index deployed by the Document Playbook Data Kit.
The Search Index list shows every hybrid search index in your org, including indexes deployed for other Salesforce Contracts features such as Contract Search. If you're unsure which index to select, check the deployment record in Data Kit Deployment History.
NOTE To create a custom index, see Manually Configure a Document Playbook Search Index.
Save your changes.

To grant designers and runtime users access to playbook records, complete Create a Document Playbook Sharing Rule.
