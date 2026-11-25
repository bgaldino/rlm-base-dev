---
page_id: deployment-global-uid-setup
title: Global Unique ID Setup
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-global-uid-setup.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Revenue Management Deployment
parent_page: deployment-overview
legacy_page_id: deployment_global_UID_setup.htm
fetched_at: 2026-11-25
---

# Global Unique ID Setup

The establishment of a Global Unique ID (GUID) column on all objects during day-one initialization is a recommended practice for Salesforce DevOps.

Salesforce uses its own internal ID for records, but this ID isn’t portable. The same record in a testing, sandbox, or production org has different Salesforce IDs. This makes tracking a single piece of data across environments nearly impossible. By introducing your own custom, externally set GUID, you have a single, immutable, and universally consistent identifier.

**Note:**

You can also choose your preferred method to maintain the mapping of records IDs across orgs.

Before performing any deployment work, establish your GUID across all database objects, and across all Salesforce orgs involved in your deployment plan.

**Note:**

Add a GUID field to all objects used during your deployment. Since you can’t add fields to metadata types (such as a Flow), use the API name for each metadata type as the unique identifier.

- 

**[Create a GUID Field](./deployment-create-guid-field.md)**

Add a GUID field to all objects used during your deployment to ensure unique identification of records across environments.

- 

**[GUID Design and Usage](./deployment-guid-design-concept.md)**

The format and values of the Global Unique ID (GUID) are up to you. Here’s some guidance on what makes a good versus poor GUID for deployment tracking.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-global-uid-setup.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
