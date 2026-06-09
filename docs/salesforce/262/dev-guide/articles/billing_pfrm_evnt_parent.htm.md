---
page_id: billing_pfrm_evnt_parent.htm
title: Billing Platform Events
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_pfrm_evnt_parent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_overview.htm
fetched_at: 2026-06-09
---

# Billing Platform Events

Salesforce publishes standard platform events in response to an action that occurred in
the org or to report errors. For example, the InvoiceProcessedEvent platform event sends
notification to the customer when the billing invoice activity is complete. You can subscribe to a
standard platform event by using the subscription mechanism that the event supports.

- **[BillingScheduleCreatedEvent](./sforce_api_objects_billingschedulecreatedevent.htm.md)**  
  Notifies subscribers when the `/commerce/invoicing/billing-schedules/actions/create` request is complete. This object is available in API version 63.0 and later.
- **[CreditInvoiceProcessedEvent](./sforce_api_objects_creditinvoiceprocessedevent.htm.md)**  
  Represents the notification to the customers after the process initiated by the `/commerce/invoicing/invoices/{invoiceId}/actions/credit` request is complete. This object is available in API version 62.0 and later.
- **[CreditMemoProcessedEvent](./sforce_api_objects_creditmemoprocessedevent.htm.md)**  
  Represents the notification to the customers after the process initiated by the `/commerce/invoicing/credit-memos` request is complete. This object is available in API version 62.0 and later.
- **[InvoiceProcessedEvent](./sforce_api_objects_invoiceprocessedevent.htm.md)**  
  Represents the notification to the customers after the process started by the `/commerce/billing/invoices` request is complete. The process groups billing schedules by grouping keys and creates one invoice per grouping key. The `InvoiceProcessedEvent` platform event is a top-level object that contains a list of `InvoiceProcessedDetailEvents` platform events, where each detail event represents an attempt to create one invoice. This object is available in API version 62.0 and later.
- **[NegInvcLineProcessedEvent](./sforce_api_objects_neginvclineprocessedevent.htm.md)**  
  Represents the notification to the customers when a negative invoice line is converted to a credit memo This object is available in API version 62.0 and later.
- **[SequenceAssignedEvent](./sforce_api_objects_sequenceassignedevent.htm.md)**  
  Represents the notification to customers about the assignment of a sequence to a target record. This process is initiated by the `/sequences/actions/assign` request. This object is available in API version 65.0 and later.
- **[VoidInvoiceProcessedEvent](./sforce_api_objects_voidinvoiceprocessedevent.htm.md)**  
  Represents the notification to the customers after the process started by the `/commerce/invoicing/invoices/{invoiceId}/actions/void` request is complete. The request attempts to void an invoice by crediting an invoice and changing its status to `Voided`, which prevents further changes. This object is available in API version 62.0 and later.
