---
page_id: connect_resources_batch_job_cancel.htm
title: Batch Job Cancel
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_batch_job_cancel.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch_management_apis_resources.htm
fetched_at: 2026-11-23
---

# Batch Job Cancel

Cancel a batch job of type data processing engine (calc job) and batch
management. A batch job with only the status Submitted or In Progress can be
canceled.

## Special Access Rules

To know the permissions needed to access this resource, See [User Permissions for Data Processing Engine](https://help.salesforce.com/s/articleView?id=ind.dpe_setup.htm&language=en_US) or [User Permissions for Batch Management](https://help.salesforce.com/s/articleView?id=ind.concept_batch_management_editions.htm&language=en_US).

## Resource

```
/connect/batch-job/batchJobId/cancel-job
```

## Resource Example

```
/connect/batch-job/0mdxx00000000fxAAA/cancel-job
```

## Available Version

52.0

## Requires Chatter

No

## HTTP Methods

POST

![Note](/docs/resources/img/en-us/264.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

POST doesn’t take
request
parameters or a request body.

## Response Body for POST

Returns HTTP 201 on success.

See [Batch Job Cancel Output](./connect_responses_batch_job_cancel.htm.md "Output representation of the batch job cancel request.") for HTTP code descriptions that are
unique to this resource in case of failure of the batch job cancel request.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_batch_job_cancel.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
