---
page_id: sforce_api_objects_neginvclineprocessedevent.htm
title: NegInvcLineProcessedEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_neginvclineprocessedevent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_pfrm_evnt_parent.htm
fetched_at: 2026-06-09
---

# NegInvcLineProcessedEvent

Represents the notification to the customers when a negative invoice
line is converted to a credit memo This object is available in API version 62.0 and
later.

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

`/event/NegInvcLineProcessedEvent`

## Event Delivery Allocation Enforced

No

## Special Access Rules

This object is available when Billing is enabled.

## Fields

| Field | Details |
| --- | --- |
| CorrelationIdentifier | Type  string  Properties  Nillable  Description  Reserved for future use. |
| CrMemoProcessErrDtlEvents | Type  [CrMemoProcessErrDtlEvent](./sforce_api_objects_crmemoprocesserrdtlevent.htm.md "Represents the information about errors that occurred while creating or applying a credit memo as part of a request. This object is included in a CreditInvoiceProcessedEvent, CreditMemoProcessedEvent, NegInvcLineProcessedEvent, or VoidInvoiceProcessedEvent platform event message. You can't subscribe to CrMemoProcessErrDtlEvent platform event directly. This object is available in API version 62.0 and later.")  Properties  Nillable  Description  A compilation of error messages and error codes for a failed request. See the ErrorDetails field for error messages and error codes. |
| CreditMemoId | Type  reference  Properties  Nillable  Description  The ID of the credit memo created as a result of the successful conversion of a negative invoice line.  This field is a relationship field.  Relationship Name  CreditMemo  Refers To  CreditMemo |
| ErrorDetails | Type  string  Properties  Nillable  Description  If the request fails, this field shows error messages, error codes, and the ID of the record on which the errors occurred. |
| EventUuid | Type  string  Properties  Nillable  Description  A universally unique identifier (UUID) that identifies a platform event message. |
| InvoiceId | Type  reference  Properties  Nillable  Description  The ID of the invoice that this event is in reference to.  This field is a relationship field.  Relationship Name  Invoice  Refers To  Invoice |
| IsAutomatedNegativeInvoiceLineConversion | Type  boolean  Properties  Defaulted on create  Description  Indicates whether this event is generated either by an automated process to convert negative invoice lines to credit memos (`true`) or by a manual process (`false`).  The default value is `false`. |
| IsSuccess | Type  boolean  Properties  Defaulted on create  Description  Required. Indicates whether the negative invoice lines were converted successfully to credit memos (`true`) or not (`false`).  The default value is `false`. |
| ReplayId | Type  string  Properties  Nillable  Description  Represents an ID value that’s populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window. |
| RequestIdentifier | Type  string  Properties  Nillable  Description  The unique identifier of the request. This field is always empty. |
