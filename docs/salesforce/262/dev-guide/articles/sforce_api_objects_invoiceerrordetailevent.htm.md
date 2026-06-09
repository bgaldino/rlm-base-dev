---
page_id: sforce_api_objects_invoiceerrordetailevent.htm
title: InvoiceErrorDetailEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_invoiceerrordetailevent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: sforce_api_objects_invoiceprocessedevent.htm
fetched_at: 2026-06-09
---

# InvoiceErrorDetailEvent

Represents information about the errors that occurred during the
processing of a `/commerce/billing/invoices` request.
This object is included in an `InvoiceProcessedEvent` platform event message. You can't subscribe to `InvoiceProcessedEvent` platform event directly. This
object is available in API version 62.0 and later.

## Supported Calls

`describeSObjects()`

## Special Access Rules

This object is available when Billing is enabled.

## Fields

| Field | Details |
| --- | --- |
| ErrorCode | Type  string  Properties  None  Description  Reference code for the type of error that occurred. |
| ErrorMessage | Type  string  Properties  None  Description  Information about the error that occurred during processing. |
| ErrorSourceId | Type  reference  Properties  Nillable  Description  The ID of the record where the error occurred. This record can be an invoice or a billing schedule.  This field is a polymorphic relationship field.  Relationship Name  ErrorSource  Refers To  BillingSchedule, Invoice |
| EventUuid | Type  string  Properties  Nillable  Description  A universally unique identifier (UUID) that identifies a platform event message. |
