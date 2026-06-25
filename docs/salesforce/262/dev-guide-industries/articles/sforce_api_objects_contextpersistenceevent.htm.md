---
page_id: sforce_api_objects_contextpersistenceevent.htm
title: ContextPersistenceEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_contextpersistenceevent.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: contextpersistenceevent_platform_event.htm
fetched_at: 2026-06-25
---

# ContextPersistenceEvent

Notifies subscribers when the Context Persistence event, initiated by the Context
Persistence API has completed its execution. This event is designed to inform
customers/clients about the success or failure of their Context Persistence request. This
object is available in API version 59.0 and later.

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

The ContextPersistenceEvent is available when IndustriesContextService Org permission is
enabled.

## Fields

| Field | Details |
| --- | --- |
| Correlation Id | Type  string  Properties  Nillable  Description  The unique identifier of the parent request that this request belongs to. |
| EventUuid | Type  string  Properties  Create  Description  Required. A universally unique identifier (UUID) that identifies a platform event message. |
| HasErrors | Type  boolean  Properties  Nillable  Description  Indicates whether the context persistence service is a failure (`true`) or a success (`false`). |
| ReplayId | Type  string  Properties  Nillable  Description  Represents an ID value that is populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window. |
| Request Identifier | Type  string  Properties  Nillable  Description  The identifier of asynchronous or synchronous request associated with the event. |
