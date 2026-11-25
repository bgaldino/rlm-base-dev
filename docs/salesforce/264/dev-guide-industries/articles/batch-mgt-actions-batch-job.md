---
page_id: batch-mgt-actions-batch-job
title: Batch Job Actions
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/batch-mgt-actions-batch-job.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch-mgt-actions-parent
legacy_page_id: batch_mgt_actions_batch_job.htm
fetched_at: 2026-11-25
---

# Batch Job Actions

Run an active Batch Management job definition. This action executes a defined Batch Management job asynchronously.

A Batch Management job processes a flow in manageable parts. For more information about running an active Batch Management jobs, see [Schedule a Batch Job](https://help.salesforce.com/articleView?id=task_schedule_batch_flow.htm) in Salesforce Help.

This object is available in API version 51.0 and later.

## Special Access Rules

To know the products and user permissions needed to access this action, See [Supported Editions and Permissions for Batch Management](https://help.salesforce.com/s/articleView?id=ind.concept_batch_management_editions.htm).

## Supported REST HTTP Methods

**URI:** `/services/data/vXX.X/actions/custom/batchJobAction`

Where `XX.X` is the latest API version.

**Formats:** JSON

**HTTP Methods:** GET, POST

**Authentication:** `Authorization: Bearer TOKEN`

Where `TOKEN` is a variable.

## Inputs

The batch job action uses the batch job definition ID and input variables to execute the job and generate a batch job ID. The input values vary according to the input variables in that flow.

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `batchJobId` | string | ID of the batch job generated after the request is successful. This batch job ID is used to track the progress of the batch job in Monitor Workflow Services. |

## Usage

A request body is always required. The input values vary according to the input variables in that flow. If your batch job doesn’t require any input variables, you still must send an empty JSON body.

```
{
  "inputs": [{}]
}
```

**JSON Sample Request**

```
{
   "noOfEmployees" : 900,
   "accountIndustry" : "Technology"
}
```

**JSON Sample Response**

```
{
   "batchJobId": "0lMxx0000A000001EAA"
   "accepted": "true"
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/batch-mgt-actions-batch-job.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
