---
page_id: monitor-workflow-services-dev-overview
title: Monitor Workflow Services
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/monitor-workflow-services-dev-overview.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch
legacy_page_id: monitor_workflow_services_dev_overview.htm
fetched_at: 2026-11-25
---

# Monitor Workflow Services

The Monitor Workflow Services standard objects can be used to track the run of Data Processing Engine definitions and Batch Management jobs. During a run, you can view details about each part that the run is broken down into. After the run is complete, you can view its status and the records which weren’t processed during the run.

| Required Editions |
| --- |
| Available in: Lightning Experience |
| Available in: Monitor Workflow Services is available with Enterprise, Unlimited, and Performance Editions where Data Processing Engine or Batch Management is available |

The objects of Monitor Workflow Services aren’t available in Object Manager of your Salesforce org.

- 

**[BatchJob](./sforce-api-objects-batchjob.md)**

Represents an instance of a batch job that is either running and has been run. This object is available in API version 51.0 and later.

- 

**[BatchJobPart](./sforce-api-objects-batchjobpart.md)**

Represents one part of a batch job. This object is available in API version 51.0 and later.

- 

**[BatchJobPartFailedRecord](./sforce-api-objects-batchjobpartfailedrecord.md)**

Represents records that a batch job part couldn’t successfully process. This object is available in API version 51.0 and later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/monitor-workflow-services-dev-overview.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
