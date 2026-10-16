---
article_id: ind.sf_contracts_contract_search_datakit_manual_overview.htm
title: Manually Configure Contract Search
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_contract_search_datakit_manual_overview.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_set_up_contract_search_for_contract_ai.htm
fetched_at: 2026-10-13
---

# Manually Configure Contract Search

Set up Contract Search manually to get fast, reliable answers across thousands of contracts. Use natural language to ask questions and receive relevant results along with AI-generated summaries.

REQUIRED EDITIONS
IMPORTANT Starting Winter ’26, Salesforce recommends setting up Contract Search by deploying the Contract Document data kit. See Set Up Contract Search By Using Prebuilt Data Kit. Manual setup steps apply only to customers who configured Contract Search in Summer ’25.
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
Sequence to Complete Contract Search Setup Manually

To set up Contract Search, perform these tasks:

Prepare Your Org for Contract Search
Grant Dataspace, File, and Contract Object Access
Set Up Salesforce Contract Document Indexing in Data Cloud for Manual Contract Search Set Up
Create a Vector Search Index for Contract Documents for Manual Contract Search Set Up
Configure an Integration User for Manual Contract Search Set Up
Set Up Data Governance for Contract Search
Set Up Salesforce Contract Document Indexing in Data Cloud for Manual Contract Search Set Up
Configure Salesforce CRM connector to stream contract documents and metadata into Data Cloud. This configuration enables AI-powered semantic search through vector embeddings that interpret natural language queries and return relevant results.
Create a Vector Search Index for Contract Documents for Manual Contract Search Set Up
Use the Search Index Builder to create a vector search index on Contract Document Version. This index powers AI-driven contract search using semantic matching and document filtering.
Configure an Integration User for Manual Contract Search Set Up
Create and configure an integration user to control access to contract data in Data Cloud. This user is required to support secure contract search operations.
