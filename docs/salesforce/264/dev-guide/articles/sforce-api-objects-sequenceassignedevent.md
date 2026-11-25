---
page_id: sforce-api-objects-sequenceassignedevent
title: SequenceAssignedEvent
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-sequenceassignedevent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-pfrm-evnt-parent
legacy_page_id: sforce_api_objects_sequenceassignedevent.htm
fetched_at: 2026-11-25
---

# SequenceAssignedEvent

Represents the notification to customers about the assignment of a sequence to a target record. This process is initiated by the `/sequences/actions/assign` request. This object is available in API version 65.0 and later.

## Supported Calls

`describeSObjects()`

## Supported Subscribers

| Subscriber | Supported? |
| --- | --- |
| Apex Triggers | Yes |
| Flows | Yes |
| Processes |  |
| Pub/Sub API |  |
| Streaming API (CometD) |  |

## Subscription Channel

`/event/SequenceAssignedEvent`.

## Event Delivery Allocation Enforced

No

## Special Access Rules

This object is available when Billing and Sequential Numbering is enabled.

## Fields

### EventUuid

- **Type**: string

- **Properties**: Nillable

- **Description**: A universally unique identifier (UUID) that identifies a platform event message.

### ReplayId

- **Type**: string

- **Properties**: Nillable

- **Description**: Represents an ID value that’s populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window.

### SequenceAssignmentDateTime

- **Type**: dateTime

- **Properties**: Nillable

- **Description**: The date and time when the sequence pattern value was assigned to the target record.

### SequencePatternValue

- **Type**: string

- **Properties**: Nillable

- **Description**: The complete sequence value that’s assigned to the target record.

### SequencePolicyIdentifier

- **Type**: string

- **Properties**: Nillable

- **Description**: The ID of the sequence policy that’s related to the event.

### SequenceValue

- **Type**: string

- **Properties**: Nillable

- **Description**: The sequence value that’s assigned to the target record.

### TargetObjectName

- **Type**: string

- **Properties**: Nillable

- **Description**: The name of the object to which the sequence policy is applicable.

### TargetRecordIdentifier

- **Type**: string

- **Properties**: Nillable

- **Description**: The ID of the target record to which the sequence policy is applied.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-sequenceassignedevent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
