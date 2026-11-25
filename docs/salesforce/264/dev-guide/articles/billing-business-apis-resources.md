---
page_id: billing-business-apis-resources
title: Resources
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-business-apis-resources.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-api-overview
legacy_page_id: billing_business_apis_resources.htm
fetched_at: 2026-11-25
---

# Resources

Learn more about the available Billing API resources.

- 

**[Sequence Gap Reconciliation (POST)](./connect-resources-sequences-gap-reconciliation.md)**

Restore a missing sequence value identified by using this API in gapless-enabled sequences. This sequence value can be used later in the subsequent sequence policy numbering, ensuring there are no gaps.

- 

**[Sequence Assignment (POST)](./connect-resources-sequences-assignment.md)**

Assign sequence pattern values to objects based on the configured sequence policy.

- 

**[Batch Invoices Document Generation (POST)](./connect-resources-invoice-batch-docgen.md)**

Asynchronously generate PDF documents for the invoices that are in the `Draft` or `Posted` status and are associated with an invoice batch run record.

- 

**[Batch Invoices Document Generation Retry (POST)](./connect-resources-invoice-batch-docgen-retry.md)**

Asynchronously regenerate PDF documents for the invoices that are in the `Draft` or `Posted` status and failed in an earlier invoice batch run.

- 

**[Batch Invoices Draft to Posted Status (POST)](./connect-resources-batch-draft-invoices-to-posted.md)**

Update a batch of invoices from `Draft` to `Posted` status for a credit memo application.

- 

**[Batch Invoice Scheduler (POST, PUT)](./connect-resources-create-an-invoice-scheduler.md)**

Create or update an invoice scheduler to automatically generate invoices. Use the criteria and filters of the invoice scheduler to set up the invoice run schedules based on your requirements.

- 

**[Batch Payment Scheduler (POST)](./connect-resources-create-payment-scheduler.md)**

Create a payment scheduler to automate and process payment runs on a recurring basis.

- 

**[Billing Arrangement (GET)](./connect-resources-get-billing-arrangement.md)**

Retrieve a billing arrangement and its associated billing arrangement lines.

- 

**[Billing Schedule Recovery List (POST)](./connect-resources-recover-billing-schedules.md)**

Recover the latest generated invoice associated with the billing schedules in the `Error` or `Processing` status.

- 

**[Composite Collection Plan Creation (POST)](./connect-resources-collections-composite-collection-plan.md)**

Create one or more collection plans, each with its collection plan items, in a single request.

- 

**[Create Billing Schedules for Orders (POST)](./connect-resources-create-billing-schedules.md)**

Generate billing schedules for orders by using context service.

- 

**[Create Sequence Policy (POST)](./connect-resources-create-sequence-policy.md)**

Create a sequence policy to configure a unique, sequential number for posted invoices or credit memos.

- 

**[Create Standalone Billing Schedules (POST)](./connect-resources-create-billing-schedules-from-any-transaction.md)**

Generate billing schedules from any internal or external transaction by using context service.

- 

**[Create and Apply Credit Memo (POST)](./connect-resources-create-and-apply-a-credit-memo.md)**

Create a credit memo and apply it to an invoice. The credit memo can fully or partially credit the invoice.

- 

**[Apply Credit Memo (POST)](./connect-resources-credit-memo-apply.md)**

Adjust or correct already issued invoices by applying an existing credit memo to an invoice.

- 

**[Unapply Credit Memo (POST)](./connect-resources-credit-memo-invoice-application-unapply.md)**

Unapply a credit memo from an invoice and return the invoice and the credit memo to their pre-application states.

- 

**[Apply Credit Memo Line (POST)](./connect-resources-credit-memo-line-level-apply.md)**

Adjust or correct already issued invoices by applying an existing credit memo line to an invoice line.

- 

**[Unapply Credit Memo Line (POST)](./connect-resources-credit-memo-line-level-unapply.md)**

Unapply a credit memo line from an invoice line and return the invoice line and the credit memo line to their pre-application states.

- 

**[Generate On-Demand Invoice Document (POST)](./connect-resources-generate-documents.md)**

Generate an invoice document for a record, and update any junction object record.

- 

**[Generate Account Statement (POST)](./connect-resources-generate-account-statement.md)**

Generate comprehensive account statement with transaction history and balance information.

- 

**[Invoice Creation (POST)](./connect-resources-create-invoices-from-billing-schedules.md)**

Create an invoice for an account, order, or a list of billing schedules.

- 

**[Invoice Draft to Posted Status (POST)](./connect-resources-draft-to-posted-invoice.md)**

Update the status of the invoice from Draft to Posted.

- 

**[Invoice Ingestion (POST)](./connect-resources-invoices-ingestion.md)**

Ingest or generate an invoice from an internal or external billing transaction data.

- 

**[Invoice Estimated Tax Calculation (POST)](./connect-resources-calculate-estimated-tax.md)**

Calculate estimated tax for invoices with invoice lines that have the `TaxProcessingStatus` as either `Pending` or `Estimated`.

- 

**[Invoice Preview (POST)](./connect-resources-preview-invoices.md)**

Generate preview invoices, which includes the estimated tax amounts, for a billing transaction for the next two billing periods.

- 

**[Invoice Run Recovery (POST)](./connect-resources-recover-errored-invoices-batch-run.md)**

Recover records associated with a failed invoice run. Recovery is required only when billing schedules remain in the `Processing`, `Void In Progress`, or `Error` status.

- 

**[Negative Invoice Lines to Credit Conversion (POST)](./connect-resources-convert-negative-invoice-lines-to-credit.md)**

Convert a list of invoice lines with a negative amount into a posted credit memo. This conversion is applicable for a single invoice at a time.

- 

**[Payment Line Apply (POST)](./connect-resources-payment-line-apply.md)**

Allocate the balance of a payment to reduce the balance of an invoice. The response includes an ID of the payment line invoice or payment line invoice line that represents the payment balance allocated against the invoice.

- 

**[Payment Line Unapply (POST)](./connect-resources-payment-line-unapply.md)**

Revert the application of a payment line from an invoice, and return the payment and invoices to their preapplication state. Use this API to correct an input during the payment application process.

- 

**[Payment Scheduler Update (PATCH)](./connect-resources-update-payment-scheduler.md)**

Activate or deactivate a payment scheduler. You can set the status of a payment scheduler to `Active`, `Canceled`, `Draft`, or `Inactive`.

- 

**[Post a Draft Memo (POST)](./connect-resources-post-draft-credit-memo.md)**

Post a draft credit memo to a credit memo record for review and approval.

- 

**[Rules Application (POST)](./connect-resources-rules-application.md)**

Apply payments and credits to an account’s invoices based on specified rules defined on the Billing Settings page.

- 

**[Posted Invoice List Write-Off (POST)](./connect-resources-write-off-invoices.md)**

Create credit memos with the total charge amount on the invoice as the write-off amount and close the invoice.

- 

**[Void a Posted Invoice (POST)](./connect-resources-void-a-posted-invoice.md)**

Void a posted invoice to rebill the customer, if necessary.

- 

**[Refund Line Apply (POST)](./connect-resources-apply-refund-to-payment.md)**

Make a refund transaction against a payment.

- 

**[Send Emails for Posted Invoices (POST)](./connect-resources-send-email-for-invoice-batch-run.md)**

Send emails for the posted invoices of a specified invoice batch run ID.

- 

**[Resume Billing (POST)](./connect-resources-resume-billing.md)**

Resume billing for billing schedule groups or an account that’s currently on hold.

- 

**[Suspend Billing (POST)](./connect-resources-suspend-billing.md)**

Suspend billing for billing schedule groups or an account for a predefined period.

- 

**[Standalone Credit Memo (POST)](./connect-resources-create-a-standalone-credit-memo.md)**

Create a credit memo without applying it to an invoice. You can credit the invoice at a later date.

- 

**[Billing Checkout (POST)](./connect-resources-billing-checkout.md)**

Create a unified checkout transaction that generates billing schedules, an invoice, and an optional payment in a single request.

- 

**[Tax Calculation (POST)](./connect-resources-calculate-taxes.md)**

Calculate tax for a transaction.

- 

**[Update Sequence Policy (PATCH)](./connect-resources-update-sequence-policies.md)**

Update the settings of a sequence policy that defines how unique, sequential numbers are generated by using specific patterns, values, and filters.

- 

**[Void Posted Credit Memo (POST)](./connect-resources-void-posted-credit-memo.md)**

Void a credit memo in posted state.

- 

**[Refund Credit Memo (POST)](./connect-resources-refund-credit-memo.md)**

Initiate a refund against a credit memo.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-business-apis-resources.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
