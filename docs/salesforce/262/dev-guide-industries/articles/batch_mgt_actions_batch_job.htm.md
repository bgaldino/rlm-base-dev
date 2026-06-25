---
page_id: batch_mgt_actions_batch_job.htm
title: Batch Job Actions
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/batch_mgt_actions_batch_job.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch_mgt_actions_parent.htm
fetched_at: 2026-06-25
---

# Batch Job Actions

Run an active Batch Management job definition. This action executes a
defined Batch Management job asynchronously.

A Batch Management job processes a flow in manageable parts. For more information about
running an active Batch Management jobs, see [Schedule a Batch Job](https://help.salesforce.com/articleView?id=task_schedule_batch_flow.htm&language=en_US) in Salesforce Help.

This object is available in API version 51.0 and later.

## Supported REST HTTP Methods

URI
:   `/services/data/vXX.X/actions/custom/batchJobAction`

Formats
:   JSON

HTTP Methods
:   GET, POST

Authentication
:   `Authorization: Bearer
    token`

## Inputs

The batch job action uses the batch job definition ID and input variables to execute the job
and generate a batch job ID. The input values vary according to the input variables in that
flow.

## Outputs

| Output | Details |
| --- | --- |
| batchJobId | Type  string  Description  ID of the batch job generated after the request is successful. This batch job ID is used to track the progress of the batch job in Monitor Workflow Services. |

## Usage

A request body is always required. The input values vary according
to the input variables in that flow. If your batch job doesn't require any input variables, you
still must send an empty JSON body.

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
