---
page_id: billing_business_api_overview.htm
title: Billing Business APIs
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_business_api_overview.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_overview.htm
fetched_at: 2026-06-09
---

# Billing Business APIs

Use the Billing Business APIs to manage credit application and to handle billing
scenarios.

These sections list the available resources.

## Credits

| Resource | Description |
| --- | --- |
| [`/commerce/invoicing/credit-memos/creditMemoId/actions/apply`](./connect_resources_credit_memo_apply.htm.md "Adjust or correct already issued invoices by applying an existing credit memo to an invoice.") (POST) | Adjust or correct already issued invoices by applying an existing credit memo to an invoice. |
| [`/commerce/invoicing/credit-memo-inv-applications/creditMemoInvApplicationId/actions/unapply`](./connect_resources_credit_memo_invoice_application_unapply.htm.md "Unapply a credit memo from an invoice and return the invoice and the credit memo to their pre-application states.") (POST) | Unapply a credit memo from an invoice and return the invoice and the credit memo to their pre-application states. |
| [`/commerce/invoicing/credit-memo-lines/creditMemoLineId/actions/apply`](./connect_resources_credit_memo_line_level_apply.htm.md "Adjust or correct already issued invoices by applying an existing credit memo line to an invoice line.") (POST) | Adjust or correct already issued invoices by applying an existing credit memo line to an invoice line. |
| [`/commerce/invoicing/credit-memo-line-invoice-line/creditMemoLineInvoiceLineId/actions/unapply`](./connect_resources_credit_memo_line_level_unapply.htm.md "Unapply a credit memo line from an invoice line and return the invoice line and the credit memo line to their pre-application states.") (POST) | Unapply a credit memo line from an invoice line and return the invoice line and the credit memo line to their pre-application states. |
| [`/commerce/invoicing/credit-memos/actions/generate`](./connect_resources_create_a_standalone_credit_memo.htm.md "Create a credit memo without applying it to an invoice. You can credit the invoice at a later date.") (POST) | Create a credit memo without applying it to an invoice. You can credit the invoice at a later date. |
| [`/commerce/invoicing/invoices/invoiceId/actions/void`](./connect_resources_void_a_posted_invoice.htm.md "Void a posted invoice to rebill the customer, if necessary.") (POST) | Void a posted invoice to rebill the customer, if necessary. |
| [`/commerce/invoicing/invoices/invoiceId/actions/convert-to-credit`](./connect_resources_convert_negative_invoice_lines_to_credit.htm.md "Convert a list of invoice lines with a negative amount into a posted credit memo. This conversion is applicable for a single invoice at a time.") (POST) | Convert a list of invoice lines with a negative amount into a posted credit memo. This conversion is applicable for a single invoice at a time. |
| [`/commerce/invoicing/invoices/invoiceId/actions/credit`](./connect_resources_create_and_apply_a_credit_memo.htm.md "Create a credit memo and apply it to an invoice. The credit memo can fully or partially credit the invoice.") (POST) | Create a credit memo and apply it to an invoice. The credit memo can fully or partially credit the invoice. |
| [`/commerce/invoicing/credit/collection/actions/post`](./connect_resources_post_draft_credit_memo.htm.md "Post a draft credit memo to a credit memo record for review and approval.") (POST) | Post a draft credit memo to a credit memo record for review and approval. |
| [`/commerce/billing/credit-memos/creditMemoId/actions/void`](./connect_resources_void_posted_credit_memo.htm.md "Void a credit memo in posted state.") (POST) | Void a credit memo in posted state. |

## Billing Schedules

| Resource | Description |
| --- | --- |
| [`/commerce/invoicing/billing-schedules/actions/create`](./connect_resources_create_billing_schedules.htm.md "Generate billing schedules for orders by using context service.") (POST) | Generate billing schedules for orders by using context service. |
| [`/commerce/invoicing/standalone/billing-schedules/actions/create`](./connect_resources_create_billing_schedules_from_any_transaction.htm.md "Generate billing schedules from any internal or external transaction by using context service.") (POST) | Generate billing schedules from any internal or external transaction by using context service. |
| [`/commerce/invoicing/billing-schedules/collection/actions/recover`](./connect_resources_recover_billing_schedules.htm.md "Recover the latest generated invoice associated with the billing schedules in the Error or Processing status.") (POST) | Recover the latest generated invoice associated with the billing schedules in the `Error` or `Processing` status. |
| [`/commerce/invoicing/actions/suspend-billing`](./connect_resources_suspend_billing.htm.md "Suspend billing for billing schedule groups or an account for a predefined period.") (POST) | Suspend billing for billing schedule groups or an account for a predefined period. |
| [`/commerce/invoicing/actions/resume-billing`](./connect_resources_resume_billing.htm.md "Resume billing for billing schedule groups or an account that’s currently on hold.") (POST) | Resume billing for billing schedule groups or an account that’s currently on hold. |

## Invoices

| Resource | Description |
| --- | --- |
| [`/commerce/invoicing/invoices/collection/actions/post`](./connect_resources_draft_to_posted_invoice.htm.md "Update the status of the invoice from Draft to Posted.") (POST) | Update the status of the invoice from Draft to Posted. |
| [`/commerce/invoicing/invoice-batch-runs/invoiceBatchRunId/actions/draft-to-posted`](./connect_resources_batch_draft_invoices_to_posted.htm.md "Update a batch of invoices from Draft to Posted status for a credit memo application.") (POST) | Update a batch of invoices from `Draft` to `Posted` status for a credit memo application. |
| [`/commerce/invoicing/invoices/collection/actions/preview`](./connect_resources_preview_invoices.htm.md "Generate preview invoices, which includes the estimated tax amounts, for a billing transaction for the next two billing periods.") (POST) | Generate preview invoices, which includes the estimated tax amounts, for a billing transaction for the next two billing periods. |
| [`/commerce/invoicing/invoices/collection/actions/ingest`](./connect_resources_invoices_ingestion.htm.md "Ingest or generate an invoice from an internal or external billing transaction data.") (POST) | Ingest or generate an invoice from an internal or external billing transaction data. |
| [`/commerce/billing/invoices/invoice-batch-docgen/invoiceBatchRunId/actions/actionName`](./connect_resources_invoice_batch_docgen.htm.md "Asynchronously generate PDF documents for the invoices that are in the Draft or Posted status and are associated with an invoice batch run record.") (POST) | Asynchronously generate PDF documents for the invoices that are in the `Draft` or `Posted` status and are associated with an invoice batch run record. |
| [`/commerce/billing/invoices/invoice-batch-docgen/invoiceBatchRunId/actions/actionName`](./connect_resources_invoice_batch_docgen_retry.htm.md "Asynchronously regenerate PDF documents for the invoices that are in the Draft or Posted status and failed in an earlier invoice batch run.") (POST) | Asynchronously regenerate PDF documents for the invoices that are in the `Draft` or `Posted` status and failed in an earlier invoice batch run. |
| [`/commerce/invoicing/invoices/actions/write-off`](./connect_resources_write_off_invoices.htm.md "Create credit memos with the total charge amount on the invoice as the write-off amount and close the invoice.") (POST) | Create credit memos with the total charge amount on the invoice as the write-off amount and close the invoice. |
| [`/commerce/invoicing/invoice-batch-runs/actions/send-email`](./connect_resources_send_email_for_invoice_batch_run.htm.md "Send emails for the posted invoices of a specified invoice batch run ID.") (POST) | Send emails for the posted invoices of a specified invoice batch run ID. |
| [`/commerce/invoicing/invoices/collection/actions/generate`](./connect_resources_create_invoices_from_billing_schedules.htm.md "Create an invoice for an account, order, or a list of billing schedules.") (POST) | Create an invoice for an account, order, or a list of billing schedules. |
| [`/revenue/billing/transactions/actions/apply`](./connect_resources_rules_application.htm.md "Apply payments and credits to an account's invoices based on specified rules defined on the Billing Settings page.") (POST) | Apply payments and credits to an account's invoices based on specified rules defined on the Billing Settings page. |
| [`/revenue/billing/document/actions/generate`](./connect_resources_generate_documents.htm.md "Generate an invoice document for a record, and update any junction object record.") (POST) | Generate an invoice document for a record, and update any junction object record. |

## Invoice Scheduler

| Resource | Description |
| --- | --- |
| [`/commerce/invoicing/invoice-schedulers`](./connect_resources_create_an_invoice_scheduler.htm.md "Create or update an invoice scheduler to automatically generate invoices. Use the criteria and filters of the invoice scheduler to set up the invoice run schedules based on your requirements.") (POST) | Create or update an invoice scheduler to automatically generate invoices. Use the criteria and filters of the invoice scheduler to set up the invoice run schedules based on your requirements. |
| [`/commerce/invoicing/invoice-batch-runs/invoiceBatchRunId/actions/recover`](./connect_resources_recover_errored_invoices_batch_run.htm.md "Recover records associated with a failed invoice run. Recovery is required only when billing schedules remain in the Processing, Void In Progress, or Error status.") (POST) | Recover records associated with a failed invoice run. Recovery is required only when billing schedules remain in the `Processing`, `Void In Progress`, or `Error` status. |

## Invoice Sequencing

| Resource | Description |
| --- | --- |
| [`/connect/sequences/policy`](./connect_resources_create_sequence_policy.htm.md "Create a sequence policy to configure a unique, sequential number for posted invoices or credit memos.") (POST) | Create a sequence policy to configure a unique, sequential number for posted invoices or credit memos. |
| [`/connect/sequences/policy/sequencePolicyId`](./connect_resources_update_sequence_policies.htm.md "Update the settings of a sequence policy that defines how unique, sequential numbers are generated by using specific patterns, values, and filters.") (PATCH) | Update the settings of a sequence policy that defines how unique, sequential numbers are generated by using specific patterns, values, and filters. |
| [`/connect/sequences/actions/assign`](./connect_resources_sequences_assignment.htm.md "Assign sequence pattern values to objects based on the configured sequence policy.") (POST) | Assign sequence pattern values to objects based on the configured sequence policy. |
| [`/connect/sequences/gap-reconciliation`](./connect_resources_sequences_gap_reconciliation.htm.md "Restore a missing sequence value identified by using this API in gapless-enabled sequences. This sequence value can be used later in the subsequent sequence policy numbering, ensuring there are no gaps.") (POST) | Restore a missing sequence value identified by using this API in gapless-enabled sequences. This sequence value can be used later in the subsequent sequence policy numbering, ensuring there are no gaps. |

## Account Statement

| Resource | Description |
| --- | --- |
| [`/revenue/billing/accounts/accountId/statement`](./connect_resources_generate_account_statement.htm.md "Generate comprehensive account statement with transaction history and balance information.") (POST) | Generate comprehensive account statement with transaction history and balance information. |

## Payments

| Resource | Description |
| --- | --- |
| [`/commerce/billing/payments/paymentId/actions/apply`](./connect_resources_payment_line_apply.htm.md "Allocate the balance of a payment to reduce the balance of an invoice. The response includes an ID of the payment line invoice or payment line invoice line that represents the payment balance allocated against the invoice.") (POST) | Allocate the balance of a payment to reduce the balance of an invoice. The response includes an ID of the payment line invoice or payment line invoice line that represents the payment balance allocated against the invoice. |
| [`/commerce/billing/payments/paymentId/paymentlines/paymentLineId/actions/unapply`](./connect_resources_payment_line_unapply.htm.md "Revert the application of a payment line from an invoice, and return the payment and invoices to their preapplication state. Use this API to correct an input during the payment application process.") (POST) | Revert the application of a payment line from an invoice, and return the payment and invoices to their preapplication state. Use this API to correct an input during the payment application process. |
| [`/commerce/billing/refunds/refundId/actions/apply`](./connect_resources_apply_refund_to_payment.htm.md "Make a refund transaction against a payment.") (POST) | Make a refund transaction against a payment. |

## Tax Calculation

| Resource | Description |
| --- | --- |
| [`/commerce/taxes/actions/calculate`](./connect_resources_calculate_taxes.htm.md "Calculate tax for a transaction.") (POST) | Calculate tax for a transaction. |
| [`/commerce/invoicing/invoices/collection/actions/calculate-estimated-tax`](./connect_resources_calculate_estimated_tax.htm.md "Calculate estimated tax for invoices with invoice lines that have the TaxProcessingStatus as either Pending or Estimated.") (POST) | Calculate estimated tax for invoices with invoice lines that have the `TaxProcessingStatus` as either `Pending` or `Estimated`. |

## Salesforce Commerce Payments API

| Resource | Description |
| --- | --- |
| [`/commerce/payments/payment-methods`](https://developer.salesforce.com/docs/commerce/salesforce-commerce/references/comm-ccs-payments-ref?meta=tokenizePaymentMethod "HTML (New Window)") (POST) | Tokenize a payment method. |
| [`/commerce/payments/sales`](https://developer.salesforce.com/docs/commerce/salesforce-commerce/references/comm-ccs-payments-ref?meta=salePayment "HTML (New Window)") (POST) | Make a payment sale. |
| [`/commerce/payments/payments/paymentId/refunds`](https://developer.salesforce.com/docs/commerce/salesforce-commerce/references/comm-ccs-payments-ref?meta=createPaymentRefund "HTML (New Window)") (POST) | Create a refund for a payment. |
| [`/commerce/payments/authorizations`](https://developer.salesforce.com/docs/commerce/salesforce-commerce/references/comm-ccs-payments-ref?meta=authorizePayment "HTML (New Window)") (POST) | Authorize a payment. |
| [`/commerce/payments/authorizations/authorizationId/reversals`](https://developer.salesforce.com/docs/commerce/salesforce-commerce/references/comm-ccs-payments-ref?meta=reverseAuthorization "HTML (New Window)") (POST) | Reverse an authorized payment. |
| [`/commerce/payments/authorizations/authorizationId/captures`](https://developer.salesforce.com/docs/commerce/salesforce-commerce/references/comm-ccs-payments-ref?meta=capturePayment "HTML (New Window)") (POST) | Capture an authorized payment. |

- **[Billing Business API Limits](./billing_business_apis_limits.htm.md)**  
  Learn about the default limits on the usage of the Billing business APIs.
- **[Resources](./billing_business_apis_resources.htm.md)**  
  Learn more about the available Billing API resources.
- **[Request Bodies](./billing_business_apis_requests.htm.md)**  
  Learn more about the available request bodies of Billing APIs.
- **[Response Bodies](./billing_business_apis_responses.htm.md)**  
  Learn more about the available response bodies of Billing APIs.

#### See Also

- [*Connect REST API Developer Guide*: Introduction](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/intro_what_is_chatter_connect.htm "Connect REST API Developer Guide: Introduction - HTML (New Window)")
