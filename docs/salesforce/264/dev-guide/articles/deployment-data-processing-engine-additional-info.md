---
page_id: deployment-data-processing-engine-additional-info
title: Data Processing Engine Additional Information
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-data-processing-engine-additional-info.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Revenue Management Deployment
parent_page: deployment-appendix-c
legacy_page_id: deployment_data_processing_engine_additional_info.htm
fetched_at: 2026-11-25
---

# Data Processing Engine Additional Information

Get to know additional deployment information for Data Processing Engine in Revenue Cloud.

## Deployment Considerations

- Data Processing Engine objects have `Draft` and `Active` states.

- The objects must be created in `Draft` state and activated later. The activation is done through API.

- Configuration can’t be changed after an object is updated to `Active` state.

- Set the state of the object to `Inactive` for any modifications, and then set the state to `Active`.

## Other Information

- 

Data Processing Engine has dependencies on these components.

  - CRM Analytics or Data Cloud

  - Bulk API

- 

You can deploy Data Processing Engine definitions from one organization to another. Both organizations must be on the same Salesforce release version.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-data-processing-engine-additional-info.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
