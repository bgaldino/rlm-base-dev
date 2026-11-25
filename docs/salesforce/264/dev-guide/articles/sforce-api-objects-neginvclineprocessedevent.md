---
page_id: sforce-api-objects-neginvclineprocessedevent
title: NegInvcLineProcessedEvent
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-neginvclineprocessedevent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-pfrm-evnt-parent
legacy_page_id: sforce_api_objects_neginvclineprocessedevent.htm
fetched_at: 2026-11-25
---

# NegInvcLineProcessedEvent

Represents the notification to the customers when a negative invoice line is converted to a credit memo This object is available in API version 62.0 and later.

## Supported Calls

`describeSObjects()`

## Supported Subscribers

| Subscriber | Supported? |
| --- | --- |
| Apex Triggers | Yes |
| Flows | Yes |
| Processes | Yes |
| Pub/Sub API | Yes |
| Streaming API (CometD) | Yes |

## Subscription Channel

`/event/NegInvcLineProcessedEvent`.

## Event Delivery Allocation Enforced

No

## Special Access Rules

This object is available when Billing is enabled.

## Fields

### CorrelationIdentifier

- **Type**: string

- **Properties**: Nillable

- **Description**: Reserved for future use.

### CrMemoProcessErrDtlEvents

- **Type**: [CrMemoProcessErrDtlEvent](./sforce-api-objects-crmemoprocesserrdtlevent.md)

- **Properties**: Nillable

- **Description**: A compilation of error messages and error codes for a failed request. See the `ErrorDetails` field for error messages and error codes.

### CreditMemoId

- **Type**: reference

- **Properties**: Nillable

- **Description**: The ID of the credit memo created as a result of the successful conversion of a negative invoice line.

This field is a relationship field.

- **Relationship Name**: CreditMemo

- **Refers To**: CreditMemo

### ErrorDetails

- **Type**: string

- **Properties**: Nillable

- **Description**: If the request fails, this field shows error messages, error codes, and the ID of the record on which the errors occurred.

### EventUuid

- **Type**: string

- **Properties**: Nillable

- **Description**: A universally unique identifier (UUID) that identifies a platform event message.

### InvoiceId

- **Type**: reference

- **Properties**: Nillable

- **Description**: The ID of the invoice that this event is in reference to.

This field is a relationship field.

- **Relationship Name**: Invoice

- **Refers To**: Invoice

### IsAutomatedNegativeInvoiceLineConversion

- **Type**: boolean

- **Properties**: Defaulted on create

- **Description**: Indicates whether this event is generated either by an automated process to convert negative invoice lines to credit memos (`true`) or by a manual process (`false`).

The default value is `false`.

### IsSuccess

- **Type**: boolean

- **Properties**: Defaulted on create

- **Description**: Required. Indicates whether the negative invoice lines were converted successfully to credit memos (`true`) or not (`false`).

The default value is `false`.

### ReplayId

- **Type**: string

- **Properties**: Nillable

- **Description**: Represents an ID value that’s populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window.

### RequestIdentifier

- **Type**: string

- **Properties**: Nillable

- **Description**: The unique identifier of the request. This field is always empty.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-neginvclineprocessedevent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
