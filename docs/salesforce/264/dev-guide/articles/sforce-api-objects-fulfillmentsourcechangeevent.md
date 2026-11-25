---
page_id: sforce-api-objects-fulfillmentsourcechangeevent
title: FulfillmentSourceChangeEvent
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentsourcechangeevent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-events-parent
legacy_page_id: sforce_api_objects_fulfillmentsourcechangeevent.htm
fetched_at: 2026-11-25
---

# FulfillmentSourceChangeEvent

Notifies updates to the sources orchestrated by Dynamic Revenue Orchestrator like order product or fulfillment order product. This object is available in API version 66.0 and later.

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

### EventUuid

- **Type**: string

- **Properties**: Nillable

- **Description**: A universally unique identifier (UUID) that identifies a platform event message.

### RecordIdentifier

- **Type**: string

- **Properties**: Create, Nillable

- **Description**: The identifier of the source record that has been updated.

### ReplayId

- **Type**: string

- **Properties**: Nillable

- **Description**: Represents an ID value that is populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentsourcechangeevent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
