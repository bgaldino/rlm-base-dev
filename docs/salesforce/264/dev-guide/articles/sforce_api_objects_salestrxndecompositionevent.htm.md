---
page_id: sforce_api_objects_salestrxndecompositionevent.htm
title: SalesTrxnDecompositionEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_salestrxndecompositionevent.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_events_parent.htm
fetched_at: 2026-11-23
---

# SalesTrxnDecompositionEvent

Notifies when the decomposition process status changes. This object is available in API version 66.0 and later.

## Supported Calls

`describeSObjects()`

## Supported Subscribers

| Subscriber | Supported? |
| --- | --- |
| Apex Triggers | Yes |
| Flows | Yes |
| Processes | No |
| Pub/Sub API | Yes |
| Streaming API (CometD) | Yes |

## Streaming API Subscription Channel

`/event/SalesTrxnDecompositionEvent`.

## Special Access Rules

This object is available in orgs with Revenue Management.

## Event Delivery Allocation Enforced

Yes

## Fields

### ErrorCode

- **Type**: string
- **Properties**: Create, Nillable
- **Description**: The error code returned for a decomposition process failure.

### EventUuid

- **Type**: string
- **Properties**: Nillable
- **Description**: A universally unique identifier (UUID) that identifies a platform event message.

### ReplayId

- **Type**: string
- **Properties**: Nillable
- **Description**: Represents an ID value that is populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window.

### SalesTransactionIdentifier

- **Type**: string
- **Properties**: Create, Nillable
- **Description**: The sales transaction being decomposed.

### Status

- **Type**: string
- **Properties**: Create, Nillable
- **Description**: The status of the decomposition process.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_salestrxndecompositionevent.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
