---
page_id: sforce-api-objects-contextpersistenceevent
title: ContextPersistenceEvent
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-contextpersistenceevent.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: contextpersistenceevent-platform-event
legacy_page_id: sforce_api_objects_contextpersistenceevent.htm
fetched_at: 2026-11-25
---

# ContextPersistenceEvent

Notifies subscribers when the Context Persistence event, initiated by the Context Persistence API has completed its execution. This event is designed to inform customers/clients about the success or failure of their Context Persistence request. This object is available in API version 59.0 and later.

## Supported Calls

`describeSObjects()`

## Supported Subscribers

| Subscriber | Supported? |
| --- | --- |
| Apex Triggers | Yes |
| Flows | Yes |
| Processes | Yes |
| Streaming API (CometD) | Yes |

## Streaming API Subscription Channel

`/event/ContextPersistenceEvent`

## Special Access Rules

The ContextPersistenceEvent is available when IndustriesContextService Org permission is enabled.

## Fields

### Correlation Id

- **Type**: string

- **Properties**: Nillable

- **Description**: The unique identifier of the parent request that this request belongs to.

### EventUuid

- **Type**: string

- **Properties**: Create

- **Description**: Required. A universally unique identifier (UUID) that identifies a platform event message.

### HasErrors

- **Type**: boolean

- **Properties**: Nillable

- **Description**: Indicates whether the context persistence service is a failure (`true`) or a success (`false`).

### ReplayId

- **Type**: string

- **Properties**: Nillable

- **Description**: Represents an ID value that is populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window.

### Request Identifier

- **Type**: string

- **Properties**: Nillable

- **Description**: The identifier of asynchronous or synchronous request associated with the event.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-contextpersistenceevent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
