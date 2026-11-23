---
page_id: data_processing_engine_dev_overview.htm
title: Data Processing Engine
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/data_processing_engine_dev_overview.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch.htm
fetched_at: 2026-11-23
---

# Data Processing Engine

Transform data that's available in your Salesforce org and write back the transformation
results as new or updated records. You can transform the data for standard and custom objects.
Data Processing Engine consists of a Tooling API object, a standard object, a Metadata API, and an
invocable action. You can use these to view, create, edit, and run Data Processing Engine
definitions.

|  |
| --- |
| Available in: Lightning Experience |
| Available in: [View product and edition availability.](https://help.salesforce.com/s/articleView?id=ind.dpe_editions.htm&language=en_US) |

- **[Data Processing Engine Tooling API Objects](./data_processing_engine_setup_object.htm.md)**  
  Data Processing Engine consists of one Tooling API object, BatchCalcJobDefinition. Use this object to create and edit a Data Processing Engine definition.
- **[Data Processing Engine Standard Object](./data_processing_engine_standard_object.htm.md)**  
  Data Processing Engine contains one standard object, BatchCalcJobDefinitionView. Use this object to view all the Data Processing Engine definitions available in your Salesforce org, including file-based definitions.
- **[Data Processing Engine Metadata API](./dpe_metadata.htm.md)**  
  Use a Metadata API to create, update, and activate Data Processing Engine definitions.
- **[Data Processing Engine Invocable Actions](./dpe_actions_parent.htm.md)**  
  Run an active Data Processing Engine definition. For more information on custom invocable actions, see **[REST API Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_rest.meta/api_rest/resources_actions_invocable.htm)** and **[Actions Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_action.meta/api_action/actions_intro.htm)**.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/data_processing_engine_dev_overview.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
