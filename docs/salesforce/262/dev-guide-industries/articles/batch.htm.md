---
page_id: batch.htm
title: Data Processing Engine, Batch Management, and Monitor Workflow Services
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/batch.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: salesforce_industries_dev_guide.htm
fetched_at: 2026-06-25
---

# Data Processing Engine, Batch Management, and Monitor Workflow Services

Data Processing Engine and Batch Management help automate your business processes. Use
objects, APIs, Platform Events, and invocable actions to define, run, and review Data Processing
Engine definitions and Batch Management jobs.

|  |
| --- |
| Available in: Lightning Experience |
| Available in: Data Processing Engine is available with Enterprise, Unlimited, and Performance Editions with the Financial Services Cloud, Loyalty Management, Manufacturing Cloud, Rebate Management, Accounting Subledger, or Provider Search in Health Cloud. |
| Available in: Batch Management is available with Enterprise, Unlimited, and Performance Editions with the Loyalty Management, Manufacturing Cloud, Rebate Management, or Accounting Subledger |

Here's how both these features can automate your business processes:

- Data Processing Engine: Transform data that's available in your Salesforce org and write back
  the transformation results as new or updated records. You can transform the data for standard
  and custom objects.
- Batch Management: Automate the processing of records in scheduled flows. You can process a
  high volume of standard and custom object records.

Once a Data Processing Engine definition is run or a Batch Management job is run, you can view
the progress of the run and the results of the run using Monitor Workflow Services.

- **[Data Model](./batch_data_model.htm.md)**  
  Data Processing Engine, Batch Management, and Monitor Workflow Servics share a data model. Let's learn about the objects and relationships in this shared data model.
- **[Common Tooling API Object](./batch_common_setup_objects.htm.md)**  
  BatchJobDefinition is a common Tooling API object that is shared between Data Processing Engine and Batch Management.
- **[Common Platform Event](./batch_management_platform_event.htm.md)**  
  Batch Management jobs and Data Processing Engine definitions are run using invocable actions in Flows. Use the BatchJobStatusChanged event to notify subscribers after a Batch Management job or a Data Processing Engine definition is processed in a flow.
- **[Common Business APIs](./batch_management_apis.htm.md)**  
  Common Business APIs are RESTful APIs that are sometimes available as Apex classes and methods.
- **[Data Processing Engine](./data_processing_engine_dev_overview.htm.md)**  
  Transform data that's available in your Salesforce org and write back the transformation results as new or updated records. You can transform the data for standard and custom objects. Data Processing Engine consists of a Tooling API object, a standard object, a Metadata API, and an invocable action. You can use these to view, create, edit, and run Data Processing Engine definitions.
- **[Batch Management](./batch_management_dev_overview.htm.md)**  
  Automate the processing of records in scheduled flows. You can process a high volume of standard and custom object records. Batch Management consists of three Tooling API objects, a standard object, a Metadata API, and an invocable action. You can use these resources to view, create, edit, and run Batch Management jobs.
- **[Monitor Workflow Services](./monitor_workflow_services_dev_overview.htm.md)**  
  The Montior Workflow Services standard objects can be used to track the run of Data Processing Engine definitons and Batch Management jobs. During a run, you can view details about each part that the run is broken down into. After the run is complete, you can view its status and the records which weren't processed during the run.
