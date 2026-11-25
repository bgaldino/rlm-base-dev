---
page_id: billing-business-apis-requests
title: Request Bodies
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-business-apis-requests.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-api-overview
legacy_page_id: billing_business_apis_requests.htm
fetched_at: 2026-11-25
---

# Request Bodies

Learn more about the available request bodies of Billing APIs.

- 

**[Address Input](./connect-requests-address-input.md)**

Input representation of the details of an address.

- 

**[Addresses Input](./connect-requests-addresses-input.md)**

Input representation of the details of the addresses for calculating tax.

- 

**[Batch Invoice Filter Criteria Input](./connect-requests-batch-invoice-filter-criteria-input.md)**

Input representation of the filter criteria for an invoice batch run.

- 

**[Batch Invoice Scheduler Input](./connect-requests-batch-invoice-scheduler-input.md)**

Input representation of the details of the request to create an invoice scheduler.

- 

**[Billing Checkout Input](./connect-requests-billing-checkout-input.md)**

Input representation of the checkout transaction details used to create the order, invoice, and payment.

- 

**[Billing Schedule Recovery Input](./connect-requests-billing-schedule-recovery-input.md)**

Input representation of the details of the billing schedules to recover the associated invoice.

- 

**[Context-Aware Billing Schedule](./connect-requests-context-aware-billing-schedule-input.md)**

Input representation of the billing transaction details.

- 

**[Standalone Billing Schedule Input](./connect-requests-context-aware-standalone-billing-schedule-input.md)**

Input representation of the request to create a billing schedule based on transaction details. This representation includes the transaction and context service details.

- 

**[Standalone Billing Schedule Metadata Input](./connect-requests-context-aware-standalone-billing-schedule-metadata-input.md)**

Input representation of the metadata details to create a billing schedule. This representation includes the name of the context definition and context mapping along with the mapping details of the transaction, billing schedule, and billing schedule group.

- 

**[Composite Collection Plan Input](./connect-requests-composite-collection-plan-input.md)**

Input representation of one or more collection plans, each with its optional nested collection plan items.

- 

**[Collection Plan Input](./connect-requests-collection-plan-input.md)**

Input representation of a single collection plan, including its optional nested collection plan items.

- 

**[Collection Plan Item Input](./connect-requests-collection-plan-item-input.md)**

Input representation of a single collection plan item to create under a collection plan.

- 

**[Convert Negative Invoice Lines Input](./connect-requests-convert-negative-invoice-lines-input.md)**

Input representation of the details of the request to convert a list of negative invoice lines into a credit.

- 

**[Credit Invoice Input](./connect-requests-credit-invoice-input.md)**

Input representation of the details of the request to create a credit memo.

- 

**[Credit Invoice Line Input](./connect-requests-credit-invoice-line-input.md)**

Input representation of the details of the invoice lines to be credited.

- 

**[Credit Invoice Line Tax Input](./connect-requests-credit-invoice-line-tax-input.md)**

Input representation of the details of the tax lines to be created manually for the invoice line.

- 

**[Credit Memo Addresses Input](./connect-requests-credit-memo-addresses-input.md)**

Input representation of the details of the billing and shipping addresses.

- 

**[Credit Memo Apply Input](./connect-requests-credit-memo-apply-input.md)**

Input representation of the request to apply a credit memo to an invoice.

- 

**[Credit Memo Apply Application Input](./connect-requests-credit-memo-apply-application-input.md)**

Input representation of the request to specify one or more applications to apply a credit memo for, with each application representing an invoice.

- 

**[Credit Memo Draft to Posted Input](./connect-requests-credit-memo-draft-to-posted-input.md)**

Input representation of the request to post a draft credit memo.

- 

**[Credit Memo Unapply Input](./connect-requests-credit-memo-unapply-input.md)**

Input representation of the request to unapply a credit memo from an invoice.

- 

**[Credit Memo Line Apply Input](./connect-requests-credit-memo-line-apply-input.md)**

Input representation of the details of the request to apply a credit memo line to an invoice line.

- 

**[Credit Memo Line Application Input](./connect-requests-credit-memo-line-application-input.md)**

Input representation of the request to specify one or more applications to apply a credit memo line for, with each application representing an invoice line.

- 

**[Credit Memo Line Unapply Input](./connect-requests-credit-memo-line-unapply-input.md)**

Input representation of the details of the request to unapply a credit memo line from an invoice line.

- 

**[Customer Details Input](./connect-requests-customer-details-input.md)**

Input representation of the customer details for tax calculation.

- 

**[Frequency Cadence Options](./connect-requests-frequency-cadence-options.md)**

Input representation of the frequency cadence options for an invoice scheduler.

- 

**[Graph Record for Invoice Ingestion](./connect-requests-graph-record-input.md)**

A Graph record is an object that’s a part of the graph structure, representing both the fields and relationships among different objects. Each record in the graph can contain attributes, which are fields of the object, and references to other related records.

- 

**[Invoice Draft To Posted Input](./connect-requests-draft-to-posted-invoice-input.md)**

Input representation of the details of the draft invoice that’s posted.

- 

**[Invoice Estimated Tax Calculation Input](./connect-requests-invoice-estimated-tax-calculation-input.md)**

Details of the invoice for which the estimated tadsfsefx must be calculated.

- 

**[Invoice Ingestion Input](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-invoice-ingestion-input.html)**

Input representation of the details of the invoice to be processed. The details include the tax processing status, user preferences for tax callouts, and associated object graph representation.

- 

**[Invoice Input for Ingestion](./connect-requests-invoice-input-for-ingestion.md)**

Input representation of the details of the invoice that must be generated for or ingested into Billing.

- 

**[Invoice Input](./connect-requests-invoice-input.md)**

Input representation of the details of the billing schedule.

- 

**[Invoice Preview Input](./connect-requests-invoice-preview-input.md)**

Input representation of the details of the billing transaction that the preview invoices are generated for.

- 

**[Line Item Input](./connect-requests-line-item-input.md)**

Input representation of the details of the line item for tax calculation.

- 

**[On-Demand Document Generation Input](./connect-requests-on-demand-doc-gen-input.md)**

Input representation of the details to generate a comprehensive on-demand document for specified record types.

- 

**[Payment Line Apply Input](./connect-requests-payment-line-apply-input.md)**

Input representation of the payment line details. This representation covers details on allocation of a payment to a specific invoice line. It also provides additional context through optional fields such as associated account and effective date.

- 

**[Payment Line Unapply Input](./connect-requests-payment-line-unapply-input.md)**

Input representation of the payment line details. This representation covers fields that you can specify to revert a payment line application to their preapplication state.

- 

**[Payment Run Batch Filter Criteria Input](./connect-requests-payment-run-batch-filter-criteria-input.md)**

Input representation of the filter criteria for an invoice batch run. This representation covers the criteria and sequence for filtering payment run details. It specifies the field and object names, comparison operations, and values to be used for filtering.

- 

**[Payment Batch Scheduler Input](./connect-requests-payment-scheduler-input.md)**

Input representation of the details of the request to create a payment scheduler. This representation sets the rules and timing for a payment scheduler, including match types, dates, frequency, and filter criteria.

- 

**[Payment Scheduler Update Input](./connect-requests-payment-scheduler-update-input.md)**

Input representation of the details of the request to update the status of a payment scheduler. This representation defines the status of a payment scheduler, which can be set to Active, Canceled, Draft, or Inactive.

- 

**[Posted Invoice List Write-Off Input](./connect-requests-write-off-posted-invoice-list-input.md)**

Input representation of the request to write off a list of posted invoices. This representation includes the details of invoices that you want to write off.

- 

**[Posted Invoice Write-Off Input](./connect-requests-write-off-posted-invoice-input.md)**

Input representation of the details of the request to write off a posted invoice. This representation includes invoice details such as invoice ID and reason for writing off invoices.

- 

**[Refund Credit Memo Input](./connect-requests-refund-credit-memo-input.md)**

Input representation of the details required to initiate a refund against a credit memo.

- 

**[Refund Line Apply Input](./connect-requests-refund-line-apply-input.md)**

Input representation of the details of a transaction refund request. This representation outlines the properties of a refund, including the refund amount and ID of the payment or credit memo record that the refund is applied to.

- 

**[Resume Billing Input](./connect-requests-resume-billing-input.md)**

Input representation of the details of the request to resume the billing operation for an account or a billing schedule group.

- 

**[Resume Billing Object Input](./connect-requests-resume-billing-entity-input.md)**

Input representation of the details such as the ID of the account or billing schedule group along with the effective date. These details are used to start the billing operation.

- 

**[Rules Application Input](./connect-requests-rules-application-input.md)**

Input representation for applying payments and credits to invoices based on rules.

- 

**[Selection Condition Input](./connect-requests-selection-condition-input.md)**

Input representation of the criteria that’s used to determine which sequencing policy is applied to a record. The criteria stores the conditions based on any standard or custom fields of the record.

- 

**[Seller Details Input](./connect-requests-seller-details-input.md)**

Input representation of the seller details for tax calculation.

- 

**[Send Email Input](./connect-requests-send-email-for-invoice-batch-run-input.md)**

Input representation of the request to send an email for an invoice batch run.

- 

**[Sequence Policy Input](./connect-requests-sequence-policy-input.md)**

Input representation of the configured rules and properties to generate unique, sequential numbers for objects.

- 

**[Sequence Gap Reconciliation Input](./connect-requests-sequence-gap-reconciliation-input.md)**

Input representation of the details that are used to identify and reconcile gaps in sequence values based on the sequence policy or target object.

- 

**[Sequences Assignment Input](./connect-requests-sequences-assignment-input.md)**

Input representation of the details of the target objects to which the sequence pattern values are assigned.

- 

**[Standalone Credit Memo Charge Input](./connect-requests-standalone-credit-memo-charge-input.md)**

Input representation of the details of the charge lines of a credit memo.

- 

**[Standalone Credit Memo Input](./connect-requests-standalone-credit-memo-input.md)**

Input representation of the details required to create a standalone credit memo.

- 

**[Standalone Credit Memo Tax Input](./connect-requests-standalone-credit-memo-tax-input.md)**

Input representation of the details of the tax request.

- 

**[Account Statement Input](./connect-requests-statement-of-account-input.md)**

Input representation of the details required to generate a comprehensive account statement with transaction history and balance information.

- 

**[Suspend Billing Input](./connect-requests-suspend-billing-input.md)**

Input representation of the details of the request to suspend the billing operation for an account or a billing schedule group.

- 

**[Suspend Billing Object Input](./connect-requests-suspend-billing-entity-input.md)**

Input representation of the details such as the ID of the account or billing schedule group along with the effective dates. These details are used to suspend the billing operation.

- 

**[Tax Calculation Input](./connect-requests-calculate-tax-input.md)**

Input representation of the details of the request to calculate tax.

- 

**[Void Posted Credit Memo Input](./connect-requests-void-posted-credit-memo-input.md)**

Input representation of the details of a credit memo to be voided.

- 

**[Void Posted Invoice Input](./connect-requests-void-posted-invoice-input.md)**

Input representation of the details of the invoice to be voided.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-business-apis-requests.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
