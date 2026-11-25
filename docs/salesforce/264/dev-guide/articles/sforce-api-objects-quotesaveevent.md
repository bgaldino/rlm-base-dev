---
page_id: sforce-api-objects-quotesaveevent
title: QuoteSaveEvent
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-quotesaveevent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: quote-and-order-capture-platform-event
legacy_page_id: sforce_api_objects_quotesaveevent.htm
fetched_at: 2026-11-25
---

# QuoteSaveEvent

Notifies subscribers that the process started by the Place Quote or Place Sales Transaction API request is complete. If the process is successful, use this event to learn about the updated quote. If the request isn’t successful, use this event to learn about the errors and how to fix them. This object is available in API version 60.0 and later.

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

`/event/QuoteSaveEvent`

## Special Access Rules

This object is available in orgs with Subscription Management or Revenue Management.

## Fields

### CorrelationIdentifier

- **Type**: string

- **Properties**: Nillable

- **Description**: Reserved for future use.

### EventUuid

- **Type**: string

- **Properties**: Nillable

- **Description**: A universally unique identifier (UUID) that identifies a platform event message.

### HasErrors

- **Type**: boolean

- **Properties**: Defaulted on create

- **Description**: The default value is `false`. Possible values are `false` or `true`.

### QuoteId

- **Type**: reference

- **Properties**: Nillable

- **Description**: The ID of the quote associated with this event. This field is a relationship field.

### ReplayId

- **Type**: string

- **Properties**: Nillable

- **Description**: Represents an ID value that is populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window.

### RequestIdentifier

- **Type**: string

- **Properties**: Nillable

- **Description**: ID of the request that triggered the event.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-quotesaveevent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
