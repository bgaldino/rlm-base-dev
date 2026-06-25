---
page_id: connect_resources_batch_job_cancel.htm
title: Batch Job Cancel
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_batch_job_cancel.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch_management_apis_resources.htm
fetched_at: 2026-06-25
---

# Batch Job Cancel

Cancel a batch job of type data processing engine (calc job) and batch
management. A batch job with only the status Submitted or In Progress can be
canceled.

Special Access Rules
:   To use this resource, the following permissions are required:

    - Your org must have the Batch Management and Data Processing Engine licenses
    - Users in your org require System Administration profile

Resource
:   ```
    /connect/batch-job/batchJobId/cancel-job
    ```

Resource example
:   ```
    /connect/batch-job/0mdxx00000000fxAAA/cancel-job
    ```

Available version
:   52.0

Requires Chatter
:   No

HTTP methods
:   POST

    ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

    #### Note

    POST doesn’t take
    request
    parameters or a request body.

Response body for POST
:   Returns HTTP 201 on success.
:   See [Batch Job Cancel Output](./connect_responses_batch_job_cancel.htm.md "Output representation of the batch job cancel request.") for HTTP code descriptions that are
    unique to this resource in case of failure of the batch job cancel request.
