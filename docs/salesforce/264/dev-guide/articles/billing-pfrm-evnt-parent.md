---
page_id: billing-pfrm-evnt-parent
title: Billing Platform Events
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-pfrm-evnt-parent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-overview
legacy_page_id: billing_pfrm_evnt_parent.htm
fetched_at: 2026-11-25
---

# Billing Platform Events

Salesforce publishes standard platform events in response to an action that occurred in the org or to report errors. For example, the InvoiceProcessedEvent platform event sends notification to the customer when the billing invoice activity is complete. You can subscribe to a standard platform event by using the subscription mechanism that the event supports.

- 

**[BillingScheduleCreatedEvent](./sforce-api-objects-billingschedulecreatedevent.md)**

Notifies subscribers when the `/commerce/invoicing/billing-schedules/actions/create` request is complete. This object is available in API version 63.0 and later.

- 

**[CreditInvoiceProcessedEvent](./sforce-api-objects-creditinvoiceprocessedevent.md)**

Represents the notification to the customers after the process initiated by the `/commerce/invoicing/invoices/{invoiceId}/actions/credit` request is complete. This object is available in API version 62.0 and later.

- 

**[CreditMemoProcessedEvent](./sforce-api-objects-creditmemoprocessedevent.md)**

Represents the notification to the customers after the process initiated by the `/commerce/invoicing/credit-memos` request is complete. This object is available in API version 62.0 and later.

- 

**[InvoiceProcessedEvent](./sforce-api-objects-invoiceprocessedevent.md)**

Represents the notification to the customers after the process started by the `/commerce/billing/invoices` request is complete. The process groups billing schedules by grouping keys and creates one invoice per grouping key. The `InvoiceProcessedEvent` platform event is a top-level object that contains a list of `InvoiceProcessedDetailEvents` platform events, where each detail event represents an attempt to create one invoice. This object is available in API version 62.0 and later.

- 

**[NegInvcLineProcessedEvent](./sforce-api-objects-neginvclineprocessedevent.md)**

Represents the notification to the customers when a negative invoice line is converted to a credit memo This object is available in API version 62.0 and later.

- 

**[SequenceAssignedEvent](./sforce-api-objects-sequenceassignedevent.md)**

Represents the notification to customers about the assignment of a sequence to a target record. This process is initiated by the `/sequences/actions/assign` request. This object is available in API version 65.0 and later.

- 

**[VoidInvoiceProcessedEvent](./sforce-api-objects-voidinvoiceprocessedevent.md)**

Represents the notification to the customers after the process started by the `/commerce/invoicing/invoices/{invoiceId}/actions/void` request is complete. The request attempts to void an invoice by crediting an invoice and changing its status to `Voided`, which prevents further changes. This object is available in API version 62.0 and later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-pfrm-evnt-parent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
