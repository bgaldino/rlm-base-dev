---
article_id: ind.sf_contracts_contract_search_datakit_deploy.htm
title: Deploy the Contract Document Data Kit for Contract Search
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_contract_search_datakit_deploy.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_search_datakit_overview.htm
fetched_at: 2026-11-23
---

# Deploy the Contract Document Data Kit for Contract Search

Automate contract search setup by deploying the prebuilt Contract Document data kit. With a single click, the data kit provisions Data Cloud components and a hybrid search index, requiring only a few manual access steps.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To deploy the Contract Document data kit to your org:	

Data Cloud Architect [Home Org]

OR

Data Cloud One [Companion Org]

AND

CLM Admin User

AND

Contracts AI User

Before you begin

Verify that the required Salesforce and Data Cloud licenses are available.
Provide access to the data space, files, and the Contract object.
Provide users with the necessary permissions to ingest, index, and search contract files in Data Cloud for Contract Search.
From Setup, in the Quick Find box, enter Contract Search, and select Contract Search.
Turn on Contract Search with AI.
Click Deploy the Contract Document Data Kit to your org.
Select a data space in the org where you want to deploy the contract document data.
Click Deploy.
The deployment status changes to Started. The platform automatically creates:
Data streams to ingest contract data from your org
Data lake objects and data model objects to store and model data
A hybrid search index to enable fast and accurate contract search
The Contract Document data kit is deployed to your org. Data Cloud components and mappings are provisioned automatically, and Contract Search is ready to use without any additional configuration. In the Deployment History section, the deployment status changes to Successful.

After you deploy the data kit, you need to Set up a Contract Search integration user for data kit deployment.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_contract_search_datakit_deploy.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
