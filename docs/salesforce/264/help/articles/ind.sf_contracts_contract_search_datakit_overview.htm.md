---
article_id: ind.sf_contracts_contract_search_datakit_overview.htm
title: Set Up Contract Search By Using Prebuilt Data Kit
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_contract_search_datakit_overview.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_set_up_contract_search_for_contract_ai.htm
fetched_at: 2026-10-13
---

# Set Up Contract Search By Using Prebuilt Data Kit

Use a home or companion org architecture for centralized search, and deploy all required components in a single click with the prebuilt Contract Document data kit.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
Scalable Multi-Org Contract Search

Contract Search supports the home-companion org architecture that centralizes indexing, with each org managing its own data ingestion. Contract Search setup is automated with Data Cloud One (DC1) and DC Singularity.

The home org hosts the search index (SI) and manages centralized Data Cloud configuration.
The companion orgs connect via DC1 and deploy the Contract Search data kit in their own orgs.
The data kit creates:
Data streams for ingesting contract data
Data lake objects (DLOs) and data model objects (DMOs) for modeling and storing data
After the data is ingested, it flows to the home org’s shared SI, where it becomes centrally searchable.

These are the benefits of scalable multi-org contract search.

Centralized indexing and search logic in the home org and companion orgs
Faster setup with consistent search across orgs
Scalable, governed approach to cross-org contract search
One-Click Contract Search Setup

DC1 Singularity introduces a one-click deployment experience for Contract Search automates the setup of all necessary Data Cloud components, eliminating the need for multiple manual steps.

These are the benefits of one-click contract search setup.

Eliminates the need for manual setup of each component
Ensures consistent and correct configuration across orgs
Reduces time-to-value for enabling Contract Search
What It Does

When you deploy the Contract Search data kit after completing the prerequisites tasks, such as preparing your org, granting data space and object access, and configuring an integration user, the data kit provisions:

Data streams to bring contract data into Data Cloud
DLOs to store raw ingested data
DMOs to model contract records
A hybrid SI for searching across records and documents simultaneously.
Sequence to Complete Contract Search Setup Via Prebuilt Data Kit Deployment

To set up Contract Search through prebuilt data kit deployment, perform these tasks.

Prepare Your Org for Contract Search
Grant Dataspace, File, and Contract Object Access
Deploy the Contract Document Data Kit for Contract Search
Set Up a Contract Search Integration User for Data Kit Deployment
Set Up Data Governance for Contract Search
Prepare Your Org for Contract Search
To prepare your org, enable Data Cloud, assign the required permission sets, and turn on Einstein Generative AI.
Grant Dataspace, File, and Contract Object Access
Update permission sets to allow users to access contract data in the default dataspace, query non-vetoed contract documents using Fileforce, and read CLM contract entities. These permissions are required to ingest, index, and search contract files in Data Cloud for contract search.
Deploy the Contract Document Data Kit for Contract Search
Automate contract search setup by deploying the prebuilt Contract Document data kit. With a single click, the data kit provisions Data Cloud components and a hybrid search index, requiring only a few manual access steps.
Set Up a Contract Search Integration User for Data Kit Deployment
Create and configure an integration user to control access to contract data in Data Cloud. This user is essential for supporting secure contract search operations.
Set Up Data Governance for Contract Search
Use Data Governance in Data Cloud to secure access to contract document chunks used in vector search. Configure a custom permission to make sure that only authorized access is granted to contract-related data. This setup is optional and required only if you want to replicate your object-level security configurations from the core to Data Cloud.
