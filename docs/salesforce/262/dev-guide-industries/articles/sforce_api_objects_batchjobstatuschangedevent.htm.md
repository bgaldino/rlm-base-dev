---
page_id: sforce_api_objects_batchjobstatuschangedevent.htm
title: BatchJobStatusChangedEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_batchjobstatuschangedevent.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch_management_platform_event.htm
fetched_at: 2026-06-25
---

# BatchJobStatusChangedEvent

Notifies subscribers of when a batch job is completed in a
flow. This object is available in API version 51.0 and later.

## Supported Calls

`describeSObjects()`

## Supported Subscribers

| Subscriber | Supported? |
| --- | --- |
| Flows | Yes |

## Fields

| Field | Details |
| --- | --- |
| BatchJob | Type  string  Description  The unique identifier of the batch job. |
| BatchJobDefinition | Type  string  Properties  Nillable  Description  The unique identifier of the batch job's definition. |
| EndDateTime | Type  dateTime  Properties  Nillable  Description  The timestamp for when the batch job execution is complete. |
| EventUuid | Type  string  Properties  Nillable  Description  A universally unique identifier (UUID) that identifies a platform event message. This field is available in API version 52.0 and later. |
| ReplayId | Type  string  Properties  Nillable  Description  Represents an ID value that is populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window. |
| StartDateTime | Type  dateTime  Properties  Nillable  Description  The timestamp for when the batch job execution is started. |
| Status | Type  picklist  Properties  Restricted picklist  Description  The status of the batch job.  Possible values are:  - `Canceled`—Canceled - `Failure` - `Success` |
