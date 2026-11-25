---
page_id: sforce-api-objects-voidinvoiceprocessedevent
title: VoidInvoiceProcessedEvent
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-voidinvoiceprocessedevent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-pfrm-evnt-parent
legacy_page_id: sforce_api_objects_voidinvoiceprocessedevent.htm
fetched_at: 2026-11-25
---

# VoidInvoiceProcessedEvent

Represents the notification to the customers after the process started by the `/commerce/invoicing/invoices/{invoiceId}/actions/void` request is complete. The request attempts to void an invoice by crediting an invoice and changing its status to `Voided`, which prevents further changes. This object is available in API version 62.0 and later.

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

`/event/VoidInvoiceProcessedEvent`.

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

- **Type**: [CrMemoProcessErrDtlEvent](./sforce-api-objects-crmemoprocesserrdtlevent.md)[]

- **Properties**: Nillable

- **Description**: A compilation of error messages and error codes for a failed request. See the `ErrorDetails` field for error messages and error codes.

### CreditMemoId

- **Type**: reference

- **Properties**: Nillable

- **Description**: The ID of the credit memo created to void the invoice as the result of a successful request.

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

- **Description**: The invoice that was voided as the result of a successful request.

This field is a relationship field.

- **Relationship Name**: Invoice

- **Refers To**: Invoice

### IsSuccess

- **Type**: boolean

- **Properties**: Defaulted on create

- **Description**: Required. Indicates whether the request was successful (`true`) or not (`false`).

The default value is `false`.

### ReplayId

- **Type**: string

- **Properties**: Nillable

- **Description**: Represents an ID value that’s populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window.

### RequestIdentifier

- **Type**: string

- **Properties**: Nillable

- **Description**: The unique ID returned in the `/commerce/billing/invoices/{invoiceId}/actions/void` response. Use this ID to identify the event for a specific request.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-voidinvoiceprocessedevent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
