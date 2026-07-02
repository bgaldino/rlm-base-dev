---
page_id: sforce_api_objects_voidinvoiceprocessedevent.htm
title: VoidInvoiceProcessedEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_voidinvoiceprocessedevent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_pfrm_evnt_parent.htm
fetched_at: 2026-06-09
---

# VoidInvoiceProcessedEvent

Represents the notification to the customers after the process
started by the `/commerce/invoicing/invoices/{invoiceId}/actions/void` request is complete. The
request attempts to void an invoice by crediting an invoice and changing its status to
`Voided`, which prevents further changes. This
object is available in API version 62.0 and later.

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

`/event/VoidInvoiceProcessedEvent`

## Event Delivery Allocation Enforced

No

## Special Access Rules

This object is available when Billing is enabled.

## Fields

| Field | Details |
| --- | --- |
| CorrelationIdentifier | Type  string  Properties  Nillable  Description  Reserved for future use. |
| CrMemoProcessErrDtlEvents | Type  [CrMemoProcessErrDtlEvent](./sforce_api_objects_crmemoprocesserrdtlevent.htm.md "Represents the information about errors that occurred while creating or applying a credit memo as part of a request. This object is included in a CreditInvoiceProcessedEvent, CreditMemoProcessedEvent, NegInvcLineProcessedEvent, or VoidInvoiceProcessedEvent platform event message. You can't subscribe to CrMemoProcessErrDtlEvent platform event directly. This object is available in API version 62.0 and later.")[]  Properties  Nillable  Description  A compilation of error messages and error codes for a failed request. See the ErrorDetails field for error messages and error codes. |
| CreditMemoId | Type  reference  Properties  Nillable  Description  The ID of the credit memo created to void the invoice as the result of a successful request.  This field is a relationship field.  Relationship Name  CreditMemo  Refers To  CreditMemo |
| ErrorDetails | Type  string  Properties  Nillable  Description  If the request fails, this field shows error messages, error codes, and the ID of the record on which the errors occurred. |
| EventUuid | Type  string  Properties  Nillable  Description  A universally unique identifier (UUID) that identifies a platform event message. |
| InvoiceId | Type  reference  Properties  Nillable  Description  The invoice that was voided as the result of a successful request.  This field is a relationship field.  Relationship Name  Invoice  Refers To  Invoice |
| IsSuccess | Type  boolean  Properties  Defaulted on create  Description  Required. Indicates whether the request was successful (`true`) or not (`false`).  The default value is `false`. |
| ReplayId | Type  string  Properties  Nillable  Description  Represents an ID value that’s populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window. |
| RequestIdentifier | Type  string  Properties  Nillable  Description  The unique ID returned in the `/commerce/billing/invoices/{invoiceId}/actions/void` response. Use this ID to identify the event for a specific request. |
