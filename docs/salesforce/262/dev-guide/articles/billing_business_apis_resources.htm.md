---
page_id: billing_business_apis_resources.htm
title: Resources
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_business_apis_resources.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_api_overview.htm
fetched_at: 2026-06-09
---

# Resources

Learn more about the available Billing API resources.

- **[Sequence Gap Reconciliation (POST)](./connect_resources_sequences_gap_reconciliation.htm.md)**  
  Restore a missing sequence value identified by using this API in gapless-enabled sequences. This sequence value can be used later in the subsequent sequence policy numbering, ensuring there are no gaps.
- **[Sequence Assignment (POST)](./connect_resources_sequences_assignment.htm.md)**  
  Assign sequence pattern values to objects based on the configured sequence policy.
- **[Batch Invoices Document Generation (POST)](./connect_resources_invoice_batch_docgen.htm.md)**  
  Asynchronously generate PDF documents for the invoices that are in the `Draft` or `Posted` status and are associated with an invoice batch run record.
- **[Batch Invoices Document Generation Retry (POST)](./connect_resources_invoice_batch_docgen_retry.htm.md)**  
  Asynchronously regenerate PDF documents for the invoices that are in the `Draft` or `Posted` status and failed in an earlier invoice batch run.
- **[Batch Invoices Draft to Posted Status (POST)](./connect_resources_batch_draft_invoices_to_posted.htm.md)**  
  Update a batch of invoices from `Draft` to `Posted` status for a credit memo application.
- **[Batch Invoice Scheduler (POST, PUT)](./connect_resources_create_an_invoice_scheduler.htm.md)**  
  Create or update an invoice scheduler to automatically generate invoices. Use the criteria and filters of the invoice scheduler to set up the invoice run schedules based on your requirements.
- **[Batch Payment Scheduler (POST)](./connect_resources_create_payment_scheduler.htm.md)**  
  Create a payment scheduler to automate and process payment runs on a recurring basis.
- **[Billing Arrangement (GET)](./connect_resources_get_billing_arrangement.htm.md)**  
  Retrieve a billing arrangement and its associated billing arrangement lines.
- **[Billing Schedule Recovery List (POST)](./connect_resources_recover_billing_schedules.htm.md)**  
  Recover the latest generated invoice associated with the billing schedules in the `Error` or `Processing` status.
- **[Create Billing Schedules for Orders (POST)](./connect_resources_create_billing_schedules.htm.md)**  
  Generate billing schedules for orders by using context service.
- **[Create Sequence Policy (POST)](./connect_resources_create_sequence_policy.htm.md)**  
  Create a sequence policy to configure a unique, sequential number for posted invoices or credit memos.
- **[Create Standalone Billing Schedules (POST)](./connect_resources_create_billing_schedules_from_any_transaction.htm.md)**  
  Generate billing schedules from any internal or external transaction by using context service.
- **[Create and Apply Credit Memo (POST)](./connect_resources_create_and_apply_a_credit_memo.htm.md)**  
  Create a credit memo and apply it to an invoice. The credit memo can fully or partially credit the invoice.
- **[Apply Credit Memo (POST)](./connect_resources_credit_memo_apply.htm.md)**  
  Adjust or correct already issued invoices by applying an existing credit memo to an invoice.
- **[Unapply Credit Memo (POST)](./connect_resources_credit_memo_invoice_application_unapply.htm.md)**  
  Unapply a credit memo from an invoice and return the invoice and the credit memo to their pre-application states.
- **[Apply Credit Memo Line (POST)](./connect_resources_credit_memo_line_level_apply.htm.md)**  
  Adjust or correct already issued invoices by applying an existing credit memo line to an invoice line.
- **[Unapply Credit Memo Line (POST)](./connect_resources_credit_memo_line_level_unapply.htm.md)**  
  Unapply a credit memo line from an invoice line and return the invoice line and the credit memo line to their pre-application states.
- **[Generate On-Demand Invoice Document (POST)](./connect_resources_generate_documents.htm.md)**  
  Generate an invoice document for a record, and update any junction object record.
- **[Generate Account Statement (POST)](./connect_resources_generate_account_statement.htm.md)**  
  Generate comprehensive account statement with transaction history and balance information.
- **[Invoice Creation (POST)](./connect_resources_create_invoices_from_billing_schedules.htm.md)**  
  Create an invoice for an account, order, or a list of billing schedules.
- **[Invoice Draft to Posted Status (POST)](./connect_resources_draft_to_posted_invoice.htm.md)**  
  Update the status of the invoice from Draft to Posted.
- **[Invoice Ingestion (POST)](./connect_resources_invoices_ingestion.htm.md)**  
  Ingest or generate an invoice from an internal or external billing transaction data.
- **[Invoice Estimated Tax Calculation (POST)](./connect_resources_calculate_estimated_tax.htm.md)**  
  Calculate estimated tax for invoices with invoice lines that have the `TaxProcessingStatus` as either `Pending` or `Estimated`.
- **[Invoice Preview (POST)](./connect_resources_preview_invoices.htm.md)**  
  Generate preview invoices, which includes the estimated tax amounts, for a billing transaction for the next two billing periods.
- **[Invoice Run Recovery (POST)](./connect_resources_recover_errored_invoices_batch_run.htm.md)**  
  Recover records associated with a failed invoice run. Recovery is required only when billing schedules remain in the `Processing`, `Void In Progress`, or `Error` status.
- **[Negative Invoice Lines to Credit Conversion (POST)](./connect_resources_convert_negative_invoice_lines_to_credit.htm.md)**  
  Convert a list of invoice lines with a negative amount into a posted credit memo. This conversion is applicable for a single invoice at a time.
- **[Payment Line Apply (POST)](./connect_resources_payment_line_apply.htm.md)**  
  Allocate the balance of a payment to reduce the balance of an invoice. The response includes an ID of the payment line invoice or payment line invoice line that represents the payment balance allocated against the invoice.
- **[Payment Line Unapply (POST)](./connect_resources_payment_line_unapply.htm.md)**  
  Revert the application of a payment line from an invoice, and return the payment and invoices to their preapplication state. Use this API to correct an input during the payment application process.
- **[Payment Scheduler Update (PATCH)](./connect_resources_update_payment_scheduler.htm.md)**  
  Activate or deactivate a payment scheduler. You can set the status of a payment scheduler to `Active`, `Canceled`, `Draft`, or `Inactive`.
- **[Post a Draft Memo (POST)](./connect_resources_post_draft_credit_memo.htm.md)**  
  Post a draft credit memo to a credit memo record for review and approval.
- **[Rules Application (POST)](./connect_resources_rules_application.htm.md)**  
  Apply payments and credits to an account's invoices based on specified rules defined on the Billing Settings page.
- **[Posted Invoice List Write-Off (POST)](./connect_resources_write_off_invoices.htm.md)**  
  Create credit memos with the total charge amount on the invoice as the write-off amount and close the invoice.
- **[Void a Posted Invoice (POST)](./connect_resources_void_a_posted_invoice.htm.md)**  
  Void a posted invoice to rebill the customer, if necessary.
- **[Refund Line Apply (POST)](./connect_resources_apply_refund_to_payment.htm.md)**  
  Make a refund transaction against a payment.
- **[Send Emails for Posted Invoices (POST)](./connect_resources_send_email_for_invoice_batch_run.htm.md)**  
  Send emails for the posted invoices of a specified invoice batch run ID.
- **[Resume Billing (POST)](./connect_resources_resume_billing.htm.md)**  
  Resume billing for billing schedule groups or an account that’s currently on hold.
- **[Suspend Billing (POST)](./connect_resources_suspend_billing.htm.md)**  
  Suspend billing for billing schedule groups or an account for a predefined period.
- **[Standalone Credit Memo (POST)](./connect_resources_create_a_standalone_credit_memo.htm.md)**  
  Create a credit memo without applying it to an invoice. You can credit the invoice at a later date.
- **[Tax Calculation (POST)](./connect_resources_calculate_taxes.htm.md)**  
  Calculate tax for a transaction.
- **[Update Sequence Policy (PATCH)](./connect_resources_update_sequence_policies.htm.md)**  
  Update the settings of a sequence policy that defines how unique, sequential numbers are generated by using specific patterns, values, and filters.
- **[Void Posted Credit Memo (POST)](./connect_resources_void_posted_credit_memo.htm.md)**  
  Void a credit memo in posted state.
