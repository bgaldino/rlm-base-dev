---
page_id: actions_obj_submit_failed_records_batchjob.htm
title: Submit Failed Records Batch Job
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/actions_obj_submit_failed_records_batchjob.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch_mgt_actions_parent.htm
fetched_at: 2026-11-23
---

# Submit Failed Records Batch Job

Run to resubmit an existing batch job with failed records for
processing. This action executes the batch job asynchronously.

This object is available in API version 52.0 and later.

## Special Access Rules

To know the products and user permissions needed to
access this action, See [Supported Editions and Permissions for Batch
Management](https://help.salesforce.com/s/articleView?id=ind.concept_batch_management_editions.htm&language=en_US).

## Supported REST HTTP Methods

**URI:**
`/services/data/vXX.X/actions/standard/submitFailedRecordsBatchJob`

Where `XX.X` is the latest API version.

**Formats:**
JSON

**HTTP Methods:** GET, POST

**Authentication:**
`Authorization: Bearer TOKEN`

Where `TOKEN` is a variable.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| failedRecordIds | array | The IDs of failed records in a batch job. |
| parentBatchJobId | string | Required. The ID of a batch job with failed records. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| batchJobId | string | The ID of a batch job generated after the request is successful. This batch job ID is used to track the progress of the batch job in Monitor Workflow Services in the org. |
| status | string | Indicates whether a batch job succeeded or failed. |

## Usage

**JSON Sample Request**

```
{
   "inputs": [{
      "parentBatchJobId": "0mdRM0000004DXrYAM",
      "failedRecordIds": [
         "001RM000005AG0bYAG", "001RM000005AERZYA4", "001RM000005AG0WYAW"
      ]
   }]
}
```

**JSON Sample Response**

```
[ {
   "actionName" : "submitFailedRecordsBatchJob",
   "errors" : null,
   "isSuccess" : true,
   "outputValues" : {
      "batchJobId" : "0mdRM0000004DZ9YAM"
   }
} ]
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/actions_obj_submit_failed_records_batchjob.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
