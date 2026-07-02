---
page_id: monitor_workflow_services_dev_overview.htm
title: Monitor Workflow Services
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/monitor_workflow_services_dev_overview.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch.htm
fetched_at: 2026-06-25
---

# Monitor Workflow Services

The Montior Workflow Services standard objects can be used to track the run of Data
Processing Engine definitons and Batch Management jobs. During a run, you can view details about
each part that the run is broken down into. After the run is complete, you can view its status and
the records which weren't processed during the run.

|  |
| --- |
| Available in: Lightning Experience |
| Available in: Monitor Workflow Services is available with Enterprise, Unlimited, and Performance Editions where Data Processing Engine or Batch Management is avaiable |

The objects of Monitor Workflow Services aren't available in Object Manager of your Salesforce
org.

- **[BatchJob](./sforce_api_objects_batchjob.htm.md)**  
  Represents an instance of a batch job that is either running and has been run. This object is available in API version 51.0 and later.
- **[BatchJobPart](./sforce_api_objects_batchjobpart.htm.md)**  
  Represents one part of a batch job. This object is available in API version 51.0 and later.
- **[BatchJobPartFailedRecord](./sforce_api_objects_batchjobpartfailedrecord.htm.md)**  
  Represents records that a batch job part couldn't successfully process. This object is available in API version 51.0 and later.
