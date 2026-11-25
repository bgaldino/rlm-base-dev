---
page_id: billing-apex-input-classes
title: ConnectApi Input Classes
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-apex-input-classes.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-connect-api-namespace
legacy_page_id: billing_apex_input_classes.htm
fetched_at: 2026-11-25
---

# ConnectApi Input Classes

Billing includes these Apex input classes.

- 

**[ConnectApi.ApplicationsRequest](./apex-connectapi-input-credit-memo-apply-application.md)**

Connect API representation of an application item input request for credit memo apply api

- 

**[ConnectApi.BillingAddressRequest](./apex-connectapi-input-address.md)**

Input representation of the details of an address.

- 

**[ConnectApi.BillingScheduleRecoveryInputRepresentation](./apex-connectapi-input-billing-schedule-recovery.md)**

Input representation of the details of the billing schedules to recover the associated invoice.

- 

**[ConnectApi.ConvertNegativeInvoiceLinesInputRequest](./apex-connectapi-input-convert-negative-invoice-lines.md)**

Input representation of the request details to convert a negative invoice line into a credit.

- 

**[ConnectApi.CreditDetailsApplyInput](./apex-connectapi-input-credit-memo-line-application.md)**

Input representation of the request to specify one or more applications to apply a credit memo line for, with each application representing an invoice line.

- 

**[ConnectApi.CreditInvoiceInputRequest](./apex-connectapi-input-credit-invoice.md)**

Input representation of the details of the request to create a credit memo.

- 

**[ConnectApi.CreditInvoiceInvoiceLine](./apex-connectapi-input-credit-invoice-invoice-line.md)**

Input representation of the details of the invoice lines to be credited.

- 

**[ConnectApi.CreditInvoiceInvoiceLineTax](./apex-connectapi-input-credit-invoice-invoice-line-tax.md)**

Input representation of the details of the tax lines to be created manually for the invoice line.

- 

**[ConnectApi.CreditMemoAddressesInputRequest](./apex-connectapi-input-credit-memo-addresses.md)**

Input representation of the details of the billing and shipping addresses.

- 

**[ConnectApi.CreditMemoApplyInputRequest](./apex-connectapi-input-credit-memo-apply.md)**

Input representation of the request to apply a credit memo to an invoice.

- 

**[ConnectApi.CreditMemoLineApplyInput](./apex-connectapi-input-credit-memo-line-apply.md)**

Input representation of the details of the request to apply a credit memo line to an invoice line.

- 

**[ConnectApi.CreditMemoLineUnapplyInput](./apex-connectapi-input-credit-memo-line-unapply.md)**

Input representation of the details of the request to unapply a credit memo line from an invoice line.

- 

**[ConnectApi.CreditMemoUnapplyInputRequest](./apex-connectapi-input-credit-memo-unapply.md)**

Input representation of the request to unapply a credit memo from an invoice.

- 

**[ConnectApi.InvoiceDraftToPostedInputRequest](./apex-connectapi-input-invoice-draft-to-posted.md)**

Input representation of the details of the draft invoice that’s posted.

- 

**[ConnectApi.InvoiceInputRepresentation](./apex-connectapi-input-invoice.md)**

Input representation of the details of the billing schedule.

- 

**[ConnectApi.PaymentLineApplyRequest](./apex-connectapi-input-payment-line-apply.md)**

Input representation of the payment line details. This representation covers details on allocation of a payment to a specific invoice line. It also provides additional context through optional fields, such as associated account and effective date.

- 

**[ConnectApi.PaymentLineUnapplyRequest](./apex-connectapi-input-payment-line-unapply.md)**

Input representation of the payment line details. This representation covers fields that you can specify to revert a payment line application.

- 

**[ConnectApi.RefundLineApplyRequest](./apex-connectapi-input-refund-line-apply.md)**

Input representation of the details of a transaction refund request. This representation outlines the properties of a refund, including the refund amount and ID of the payment or credit memo record that the refund is applied to.

- 

**[ConnectApi.SequenceGapReconciliationInputRepresentation](./apex-connectapi-input-sequence-gap-reconciliation.md)**

The details of the input used to identify and reconcile gaps in sequence values based on the sequence policy or target object.

- 

**[ConnectApi.SequencesAssignmentInputRepresentation](./apex-connectapi-input-sequences-assignment.md)**

The details of the target objects to which the sequence pattern values are assigned.

- 

**[ConnectApi.StandaloneCreditMemoChargeInputRequest](./apex-connectapi-input-standalone-credit-memo-charge.md)**

Input representation of the details of the charge lines of a credit memo.

- 

**[ConnectApi.StandaloneCreditMemoInputRequest](./apex-connectapi-input-standalone-credit-memo.md)**

Input representation of the details required to create a standalone credit memo.

- 

**[ConnectApi.StandaloneCreditMemoTaxInputRequest](./apex-connectapi-input-standalone-credit-memo-tax.md)**

Connect API representation of Tax input request

- 

**[ConnectApi.VoidPostedCreditMemoInputRepresentation](./apex-connectapi-input-void-posted-credit-memo.md)**

Input representation of the details of a credit memo to be voided.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-apex-input-classes.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
