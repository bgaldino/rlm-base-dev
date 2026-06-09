---
page_id: billing_apex_input_classes.htm
title: ConnectApi Input Classes
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_apex_input_classes.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_connect_api_namespace.htm
fetched_at: 2026-06-09
---

# ConnectApi Input Classes

Billing includes these Apex input classes.

- **[ConnectApi.ApplicationsRequest](./apex_connectapi_input_credit_memo_apply_application.htm.md)**  
  Connect API representation of an application item input request for credit memo apply api
- **[ConnectApi.BillingAddressRequest](./apex_connectapi_input_address.htm.md)**  
  Input representation of the details of an address.
- **[ConnectApi.BillingScheduleRecoveryInputRepresentation](./apex_connectapi_input_billing_schedule_recovery.htm.md)**  
  Input representation of the details of the billing schedules to recover the associated invoice.
- **[ConnectApi.ConvertNegativeInvoiceLinesInputRequest](./apex_connectapi_input_convert_negative_invoice_lines.htm.md)**  
  Input representation of the request details to convert a negative invoice line into a credit.
- **[ConnectApi.CreditDetailsApplyInput](./apex_connectapi_input_credit_memo_line_application.htm.md)**  
  Input representation of the request to specify one or more applications to apply a credit memo line for, with each application representing an invoice line.
- **[ConnectApi.CreditInvoiceInputRequest](./apex_connectapi_input_credit_invoice.htm.md)**  
  Input representation of the details of the request to create a credit memo.
- **[ConnectApi.CreditInvoiceInvoiceLine](./apex_connectapi_input_credit_invoice_invoice_line.htm.md)**  
  Input representation of the details of the invoice lines to be credited.
- **[ConnectApi.CreditInvoiceInvoiceLineTax](./apex_connectapi_input_credit_invoice_invoice_line_tax.htm.md)**  
  Input representation of the details of the tax lines to be created manually for the invoice line.
- **[ConnectApi.CreditMemoAddressesInputRequest](./apex_connectapi_input_credit_memo_addresses.htm.md)**  
  Input representation of the details of the billing and shipping addresses.
- **[ConnectApi.CreditMemoApplyInputRequest](./apex_connectapi_input_credit_memo_apply.htm.md)**  
  Input representation of the request to apply a credit memo to an invoice.
- **[ConnectApi.CreditMemoLineApplyInput](./apex_connectapi_input_credit_memo_line_apply.htm.md)**  
  Input representation of the details of the request to apply a credit memo line to an invoice line.
- **[ConnectApi.CreditMemoLineUnapplyInput](./apex_connectapi_input_credit_memo_line_unapply.htm.md)**  
  Input representation of the details of the request to unapply a credit memo line from an invoice line.
- **[ConnectApi.CreditMemoUnapplyInputRequest](./apex_connectapi_input_credit_memo_unapply.htm.md)**  
  Input representation of the request to unapply a credit memo from an invoice.
- **[ConnectApi.InvoiceDraftToPostedInputRequest](./apex_connectapi_input_invoice_draft_to_posted.htm.md)**  
  Input representation of the details of the draft invoice that’s posted.
- **[ConnectApi.InvoiceInputRepresentation](./apex_connectapi_input_invoice.htm.md)**  
  Input representation of the details of the billing schedule.
- **[ConnectApi.PaymentLineApplyRequest](./apex_connectapi_input_payment_line_apply.htm.md)**  
  Input representation of the payment line details. This representation covers details on allocation of a payment to a specific invoice line. It also provides additional context through optional fields, such as associated account and effective date.
- **[ConnectApi.PaymentLineUnapplyRequest](./apex_connectapi_input_payment_line_unapply.htm.md)**  
  Input representation of the payment line details. This representation covers fields that you can specify to revert a payment line application.
- **[ConnectApi.RefundLineApplyRequest](./apex_connectapi_input_refund_line_apply.htm.md)**  
  Input representation of the details of a transaction refund request. This representation outlines the properties of a refund, including the refund amount and ID of the payment or credit memo record that the refund is applied to.
- **[ConnectApi.SequenceGapReconciliationInputRepresentation](./apex_connectapi_input_sequence_gap_reconciliation.htm.md)**  
  The details of the input used to identify and reconcile gaps in sequence values based on the sequence policy or target object.
- **[ConnectApi.SequencesAssignmentInputRepresentation](./apex_connectapi_input_sequences_assignment.htm.md)**  
  The details of the target objects to which the sequence pattern values are assigned.
- **[ConnectApi.StandaloneCreditMemoChargeInputRequest](./apex_connectapi_input_standalone_credit_memo_charge.htm.md)**  
  Input representation of the details of the charge lines of a credit memo.
- **[ConnectApi.StandaloneCreditMemoInputRequest](./apex_connectapi_input_standalone_credit_memo.htm.md)**  
  Input representation of the details required to create a standalone credit memo.
- **[ConnectApi.StandaloneCreditMemoTaxInputRequest](./apex_connectapi_input_standalone_credit_memo_tax.htm.md)**  
  Connect API representation of Tax input request
- **[ConnectApi.VoidPostedCreditMemoInputRepresentation](./apex_connectapi_input_void_posted_credit_memo.htm.md)**  
  Input representation of the details of a credit memo to be voided.
