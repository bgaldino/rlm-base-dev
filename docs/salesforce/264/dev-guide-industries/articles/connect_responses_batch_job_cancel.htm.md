---
page_id: connect_responses_batch_job_cancel.htm
title: Batch Job Cancel Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_batch_job_cancel.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch_management_apis_responses.htm
fetched_at: 2026-11-23
---

# Batch Job Cancel Output

Output representation of the batch job cancel
request.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `message` | String | Details about why the batch job cancel request failed. | Small, 52.0 | 52.0 |

This table lists HTTP response code descriptions that are unique to this resource.

| HTTP Response Code | Error Code | Description |
| --- | --- | --- |
| 400 | `INVALID_STATUS` | We can't cancel the batch job that doesn't have an active run. Specify the ID of a batch job with an active run and try again. |
| 400 | `INVALID_STATUS` | We can't cancel the batch job that is already canceled or completed. Specify the ID of a valid batch job with the status InProgress or Submitted and try again. |
| 400 | `DELETE_FAILED` | We can’t cancel the batch job of which the results are already being written back. |
| 400 | `DELETE_FAILED` | We can’t cancel the batch job because of an error in processing your org’s data. Run the Data Processing Engine definition and try again. |
| 403 | `FORBIDDEN` | You don’t have the permission to cancel a batch job. Ask your Salesforce admin for help. |
| 404 | `RESOURCE_NOT_FOUND` | Specify the ID of a valid batch job and try again. |
| 500 | `INTERNAL_SERVER_ERROR` | Something went wrong when we tried to cancel the batch job. Try again or ask your Salesforce admin for help. |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_batch_job_cancel.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
