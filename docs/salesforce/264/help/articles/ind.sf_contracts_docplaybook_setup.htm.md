---
article_id: ind.sf_contracts_docplaybook_setup.htm
title: Set Up Document Playbook
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_docplaybook_setup.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_system_administration_for_salesforce_contracts.htm
fetched_at: 2026-10-13
---

# Set Up Document Playbook

Document Playbook gives your legal and contract teams a single reusable source of negotiation guidelines that Salesforce Contracts uses during risk analysis. When a contract author runs risk analysis, Salesforce matches each modified clause against the active playbook version and flags deviations, nonstandard language, fallback positions, and escalation paths so that reviews align with company policy. Set up licenses, Data 360 indexing, and sharing so that designers can create document playbooks and contract authors can use playbook guidance during risk analysis.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.

Document Playbook is part of the Salesforce Contracts feature set. When you turn it on, playbook content is stored and indexed in Data 360 (formerly Data Cloud), so risk analysis can retrieve the most relevant guidance for the record type of the contract under review.

Setup spans these areas.

Document Playbook Management: A single setup toggle enables the feature for your org.
Document Playbook Data Kit: The data kit creates data streams that ingest playbook content into Data 360 and creates the hybrid search index that risk analysis uses to find relevant guidance.
Document Playbook Indexing: The indexing configuration specifies which search index Document Playbook uses. The data kit deploys a default index that you can clone to customize chunking, embedding, or preprocessing behavior.
Sharing: Playbooks are private by default. A sharing rule makes each playbook visible to other designers and to runtime users during risk analysis.
Completion notification: When the run completes, the author receives an in-app notification indicating whether the analysis succeeded, was skipped, or failed.
Assign Document Playbook Licenses and Permission Sets
Assign the permission set license and permission sets that match each user persona. Designers create and manage playbooks. Contract authors consult playbook guidance during risk analysis.
Turn On Document Playbook Management
When you turn on Document Playbook, playbook content is stored and indexed in Data 360 (formerly Data Cloud), so risk analysis can retrieve the most relevant guidance for the record type of the contract under review. Document Playbook requires a Data 360 license.
Deploy the Document Playbook Data Kit
Use the Document Playbook Data Kit to create the data streams and hybrid search index that ingest and index playbook content in Data 360. The data kit is a single deployable bundle and is the recommended setup path.
Configure Document Playbook Indexing
Indexing controls how the playbook content is grouped into segments in Data 360 (Data Cloud). During risk analysis, Salesforce matches each contract section against the most relevant segment. Use the index deployed by the data kit, or create a custom index.
Create a Document Playbook Sharing Rule
Only the owner can access a document playbook’s records. To give other users access to a playbook, create sharing rules to provide the appropriate access.
Manually Configure Document Playbook Data Streams and Search Index
If you don't want to use the index that the Document Playbook Data Kit creates, manually set up the data streams and search index that ingest and index playbook content in Data 360. Start here to give the Data Cloud Salesforce Connector the required permissions, and then complete the data streams and search index child tasks. The Document Playbook Data Kit deployment remains the recommended configuration.
