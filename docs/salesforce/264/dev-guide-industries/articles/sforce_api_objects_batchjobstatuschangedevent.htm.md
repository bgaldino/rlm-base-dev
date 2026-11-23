---
page_id: sforce_api_objects_batchjobstatuschangedevent.htm
title: BatchJobStatusChangedEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_batchjobstatuschangedevent.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch_management_platform_event.htm
fetched_at: 2026-11-23
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

## Special Access Rules

To know the permissions needed to access this event, See [User Permissions for Data Processing
Engine](https://help.salesforce.com/s/articleView?id=ind.dpe_setup.htm&language=en_US) or [User Permissions for Batch Management](https://help.salesforce.com/s/articleView?id=ind.concept_batch_management_editions.htm&language=en_US).

## Fields

### BatchJob

- **Type**: string
- **Description**: The unique identifier of the batch job.

### BatchJobDefinition

- **Type**: string
- **Properties**: Nillable
- **Description**: The unique identifier of the batch job's
  definition.

### EndDateTime

- **Type**: dateTime
- **Properties**: Nillable
- **Description**: The timestamp for when the batch job execution is
  complete.

### EventUuid

- **Type**: string
- **Properties**: Nillable
- **Description**: A universally unique identifier (UUID) that identifies a
  platform event message. This field is available in API
  version 52.0 and later.

### ReplayId

- **Type**: string
- **Properties**: Nillable
- **Description**: Represents an ID value that is populated by the system
  and refers to the position of the event in the event
  stream. Replay ID values aren’t guaranteed to be
  contiguous for consecutive events. A subscriber can
  store a replay ID value and use it on resubscription to
  retrieve missed events that are within the retention
  window.

### StartDateTime

- **Type**: dateTime
- **Properties**: Nillable
- **Description**: The timestamp for when the batch job execution is
  started.

### Status

- **Type**: picklist
- **Properties**: Restricted picklist
- **Description**: The status of the batch job.
- **Possible values**:
  - `Canceled`—Canceled
  - `Failure`
  - `Success`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_batchjobstatuschangedevent.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
