---
page_id: data_processing_engine_dev_overview.htm
title: Data Processing Engine
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/data_processing_engine_dev_overview.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch.htm
fetched_at: 2026-06-25
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
| Available in: Data Processing Engine is available with Enterprise, Unlimited, and Performance Editions with the Financial Services Cloud, Loyalty Management, Manufacturing Cloud, Rebate Management, Accounting Subledger, or Provider Search in Health Cloud. |

- **[Data Processing Engine Tooling API Objects](./data_processing_engine_setup_object.htm.md)**  
  Data Processing Engine consists of one Tooling API object, BatchCalcJobDefinition. Use this object to create and edit a Data Processing Engine definition.
- **[Data Processing Engine Standard Object](./data_processing_engine_standard_object.htm.md)**  
  Data Processing Engine contains one standard object, BatchCalcJobDefinitionView. Use this object to view all the Data Processing Engine definitions available in your Salesforce org, including file-based definitions.
- **[Data Processing Engine Metadata API](./dpe_metadata.htm.md)**  
  Use a Metadata API to create, update, and activate Data Processing Engine definitions.
- **[Data Processing Engine Invocable Actions](./dpe_actions_parent.htm.md)**  
  Run an active Data Processing Engine definition. For more information on custom invocable actions, see **[REST API Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_rest.meta/api_rest/resources_actions_invocable.htm)** and **[Actions Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_action.meta/api_action/actions_intro.htm)**.
