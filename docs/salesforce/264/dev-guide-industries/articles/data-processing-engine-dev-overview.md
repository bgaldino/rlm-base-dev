---
page_id: data-processing-engine-dev-overview
title: Data Processing Engine
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/data-processing-engine-dev-overview.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch
legacy_page_id: data_processing_engine_dev_overview.htm
fetched_at: 2026-11-25
---

# Data Processing Engine

Transform data that’s available in your Salesforce org and write back the transformation results as new or updated records. You can transform the data for standard and custom objects. Data Processing Engine consists of a Tooling API object, a standard object, a Metadata API, and an invocable action. You can use these to view, create, edit, and run Data Processing Engine definitions.

| Required Editions |
| --- |
| Available in: Lightning Experience |
| Available in: [View product and edition availability.](https://help.salesforce.com/s/articleView?id=ind.dpe_editions.htm) |

- 

**[Data Processing Engine Tooling API Objects](./data-processing-engine-setup-object.md)**

Data Processing Engine consists of one Tooling API object, BatchCalcJobDefinition. Use this object to create and edit a Data Processing Engine definition.

- 

**[Data Processing Engine Standard Object](./data-processing-engine-standard-object.md)**

Data Processing Engine contains one standard object, BatchCalcJobDefinitionView. Use this object to view all the Data Processing Engine definitions available in your Salesforce org, including file-based definitions.

- 

**[Data Processing Engine Metadata API](./dpe-metadata.md)**

Use a Metadata API to create, update, and activate Data Processing Engine definitions.

- 

**[Data Processing Engine Invocable Actions](./dpe-actions-parent.md)**

Run an active Data Processing Engine definition. For more information on custom invocable actions, see **[REST API Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_actions_invocable.htm)** and **[Actions Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.api_action.meta/api_action/actions_intro.htm)**.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/data-processing-engine-dev-overview.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
