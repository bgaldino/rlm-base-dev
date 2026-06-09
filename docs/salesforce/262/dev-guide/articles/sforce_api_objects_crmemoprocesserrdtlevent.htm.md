---
page_id: sforce_api_objects_crmemoprocesserrdtlevent.htm
title: CrMemoProcessErrDtlEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_crmemoprocesserrdtlevent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: sforce_api_objects_creditinvoiceprocessedevent.htm
fetched_at: 2026-06-09
---

# CrMemoProcessErrDtlEvent

Represents the information about errors that occurred while creating
or applying a credit memo as part of a request. This object is included in a `CreditInvoiceProcessedEvent`, `CreditMemoProcessedEvent,` `NegInvcLineProcessedEvent`, or `VoidInvoiceProcessedEvent` platform event message. You can't subscribe
to `CrMemoProcessErrDtlEvent` platform event
directly. This object is available in API version 62.0 and later.

## Supported Calls

`describeSObjects()`

## Special Access Rules

This object is available when Billing is enabled.

## Fields

| Field | Details |
| --- | --- |
| ErrorCode | Type  string  Properties  Nillable  Description  Reference code for the type of error that occurred. |
| ErrorMessage | Type  string  Properties  Nillable  Description  Information about the error that occurred during processing. |
| ErrorSourceId | Type  reference  Properties  Nillable  Description  The ID of the record on which the error occurred during the credit memo creation process and the application process.  This field is a polymorphic relationship field.  Relationship Name  ErrorSource  Refers To  CreditMemo, CreditMemoLine, Invoice, InvoiceLine |
| EventUuid | Type  string  Properties  Nillable  Description  A universally unique identifier (UUID) that identifies a platform event message. |
