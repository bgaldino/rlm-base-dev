---
page_id: batch
title: Data Processing Engine, Batch Management, and Monitor Workflow Services
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/batch.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
legacy_page_id: batch.htm
fetched_at: 2026-11-25
---

# Data Processing Engine, Batch Management, and Monitor Workflow Services

Data Processing Engine and Batch Management help automate your business processes. Use objects, APIs, Platform Events, and invocable actions to define, run, and review Data Processing Engine definitions and Batch Management jobs.

| Required Editions |
| --- |
| Available in: Lightning Experience |
| Available in: [View product and edition availability for Data Processing Engine.](https://help.salesforce.com/s/articleView?id=ind.dpe_editions.htm) |
| Available in: [View product and edition availability for Batch Management.](https://help.salesforce.com/s/articleView?id=ind.concept_batch_management_editions.htm) |

Here’s how both these features can automate your business processes:

- Data Processing Engine: Transform data that’s available in your Salesforce org and write back the transformation results as new or updated records. You can transform the data for standard and custom objects.

- Batch Management: Automate the processing of records in scheduled flows. You can process a high volume of standard and custom object records.

Once a Data Processing Engine definition is run or a Batch Management job is run, you can view the progress of the run and the results of the run using Monitor Workflow Services.

- 

**[Data Model](./batch-data-model.md)**

Data Processing Engine, Batch Management, and Monitor Workflow Servics share a data model. Let’s learn about the objects and relationships in this shared data model.

- 

**[Common Tooling API Object](./batch-common-setup-objects.md)**

BatchJobDefinition is a common Tooling API object that is shared between Data Processing Engine and Batch Management.

- 

**[Common Platform Event](./batch-management-platform-event.md)**

Batch Management jobs and Data Processing Engine definitions are run using invocable actions in Flows. Use the BatchJobStatusChanged event to notify subscribers after a Batch Management job or a Data Processing Engine definition is processed in a flow.

- 

**[Common Business APIs](./batch-management-apis.md)**

Common Business APIs are RESTful APIs that are sometimes available as Apex classes and methods.

- 

**[Data Processing Engine](./data-processing-engine-dev-overview.md)**

Transform data that’s available in your Salesforce org and write back the transformation results as new or updated records. You can transform the data for standard and custom objects. Data Processing Engine consists of a Tooling API object, a standard object, a Metadata API, and an invocable action. You can use these to view, create, edit, and run Data Processing Engine definitions.

- 

**[Batch Management](./batch-management-dev-overview.md)**

Automate the processing of records in scheduled flows. You can process a high volume of standard and custom object records. Batch Management consists of three Tooling API objects, a standard object, a Metadata API, and an invocable action. You can use these resources to view, create, edit, and run Batch Management jobs.

- 

**[Monitor Workflow Services](./monitor-workflow-services-dev-overview.md)**

The Monitor Workflow Services standard objects can be used to track the run of Data Processing Engine definitions and Batch Management jobs. During a run, you can view details about each part that the run is broken down into. After the run is complete, you can view its status and the records which weren’t processed during the run.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/batch.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
