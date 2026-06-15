---
page_id: sforce_api_objects_invoiceprocessedevent.htm
title: InvoiceProcessedEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_invoiceprocessedevent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_pfrm_evnt_parent.htm
fetched_at: 2026-06-09
---

# InvoiceProcessedEvent

Represents the notification to the customers after the process
started by the `/commerce/billing/invoices` request is
complete. The process groups billing schedules by grouping keys and creates one invoice per
grouping key. The `InvoiceProcessedEvent` platform event
is a top-level object that contains a list of `InvoiceProcessedDetailEvents` platform events, where each detail event
represents an attempt to create one invoice. This object is available in API version
62.0 and later.

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

`/event/InvoiceProcessedEvent`

## Event Delivery Allocation Enforced

No

## Special Access Rules

This object is available when Billing is enabled.

## Fields

| Field | Details |
| --- | --- |
| CorrelationIdentifier | Type  string  Properties  Nillable  Description  Reserved for future use. |
| EventUuid | Type  string  Properties  Nillable  Description  A universally unique identifier (UUID) that identifies a platform event message. |
| InvoiceErrorDetailEvent | Type  [InvoiceErrorDetailEvent[]](./sforce_api_objects_invoiceerrordetailevent.htm.md "Represents information about the errors that occurred during the processing of a /commerce/billing/invoices request. This object is included in an InvoiceProcessedEvent platform event message. You can't subscribe to InvoiceProcessedEvent platform event directly. This object is available in API version 62.0 and later.")  Properties  Nillable  Description  Information about errors that occurred during processing. |
| InvoiceProcessedDetailEvents | Type  [InvoiceProcessedDetailEvent[]](./sforce_api_objects_invoiceprocesseddetailevent.htm.md "Represents the notification to customers regarding the results of an attempt to create an invoice from billing schedules as part of /commerce/billing/invoices request. The InvoiceProcessedDetailEvent platform event contains the results of an attempt to create an invoice from one or more billing schedules that share a grouping key. Each InvoiceProcessedDetailEventplatform event for an action is grouped within the parent InvoiceProcessedDetailEvent platform event. This object is available in API version 62.0 and later.")  Properties  Nillable  Description  A list of `InvoiceProcessedDetailEvent` records. Each record contains information about an attempt to create an invoice from one or more billing schedules that share a grouping key. |
| IsSuccess | Type  boolean  Properties  Defaulted on create  Description  Required. Indicates whether the Create Order from Invoice action was successful (`true`) or not (`false`).  The default value is `false`. |
| ReplayId | Type  string  Properties  Nillable  Description  An identification (ID) value that’s populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A user can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window. |
| RequestIdentifier | Type  string  Properties  Nillable  Description  A unique ID returned in the `/commerce/billing/invoices` response. Use this ID to identify the event for a specific request. |

- **[InvoiceErrorDetailEvent](./sforce_api_objects_invoiceerrordetailevent.htm.md)**  
  Represents information about the errors that occurred during the processing of a `/commerce/billing/invoices` request. This object is included in an `InvoiceProcessedEvent` platform event message. You can't subscribe to `InvoiceProcessedEvent` platform event directly. This object is available in API version 62.0 and later.
- **[InvoiceProcessedDetailEvent](./sforce_api_objects_invoiceprocesseddetailevent.htm.md)**  
  Represents the notification to customers regarding the results of an attempt to create an invoice from billing schedules as part of `/commerce/billing/invoices` request. The `InvoiceProcessedDetailEvent` platform event contains the results of an attempt to create an invoice from one or more billing schedules that share a grouping key. Each `InvoiceProcessedDetailEvent`platform event for an action is grouped within the parent `InvoiceProcessedDetailEvent` platform event. This object is available in API version 62.0 and later.
