---
page_id: billing-business-api-overview
title: Billing Business APIs
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-business-api-overview.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-overview
legacy_page_id: billing_business_api_overview.htm
fetched_at: 2026-11-25
---

# Billing Business APIs

Use the Billing Business APIs to manage credit application and to handle billing scenarios.

These sections list the available resources.

## Credits

| Resource | Description |
| --- | --- |
| [`/commerce/invoicing/credit-memos/{creditMemoId}/actions/apply`](./connect-resources-credit-memo-apply.md) (POST) | Adjust or correct already issued invoices by applying an existing credit memo to an invoice. |
| [`/commerce/invoicing/credit-memo-inv-applications/{creditMemoInvApplicationId}/actions/unapply`](./connect-resources-credit-memo-invoice-application-unapply.md) (POST) | Unapply a credit memo from an invoice and return the invoice and the credit memo to their pre-application states. |
| [`/commerce/invoicing/credit-memo-lines/{creditMemoLineId}/actions/apply`](./connect-resources-credit-memo-line-level-apply.md) (POST) | Adjust or correct already issued invoices by applying an existing credit memo line to an invoice line. |
| [`/commerce/invoicing/credit-memo-line-invoice-line/{creditMemoLineInvoiceLineId}/actions/unapply`](./connect-resources-credit-memo-line-level-unapply.md) (POST) | Unapply a credit memo line from an invoice line and return the invoice line and the credit memo line to their pre-application states. |
| [`/commerce/invoicing/credit-memos/actions/generate`](./connect-resources-create-a-standalone-credit-memo.md) (POST) | Create a credit memo without applying it to an invoice. You can credit the invoice at a later date. |
| [`/commerce/invoicing/invoices/collection/actions/checkout`](./connect-resources-billing-checkout.md) (POST) | Create a unified checkout transaction that generates billing schedules, an invoice, and an optional payment in a single request. |
| [`/commerce/invoicing/invoices/{invoiceId}/actions/void`](./connect-resources-void-a-posted-invoice.md) (POST) | Void a posted invoice to rebill the customer, if necessary. |
| [`/commerce/invoicing/invoices/{invoiceId}/actions/convert-to-credit`](./connect-resources-convert-negative-invoice-lines-to-credit.md) (POST) | Convert a list of invoice lines with a negative amount into a posted credit memo. This conversion is applicable for a single invoice at a time. |
| [`/commerce/invoicing/invoices/{invoiceId}/actions/credit`](./connect-resources-create-and-apply-a-credit-memo.md) (POST) | Create a credit memo and apply it to an invoice. The credit memo can fully or partially credit the invoice. |
| [`/commerce/invoicing/credit/collection/actions/post`](./connect-resources-post-draft-credit-memo.md) (POST) | Post a draft credit memo to a credit memo record for review and approval. |
| [`/commerce/billing/credit-memos/{creditMemoId}/actions/void`](./connect-resources-void-posted-credit-memo.md) (POST) | Void a credit memo in posted state. |
| [`/revenue/billing/refunds/unreferenced-refunds/actions/process`](./connect-resources-refund-credit-memo.md) (POST) | Initiate a refund against a credit memo. |

## Billing Schedules

| Resource | Description |
| --- | --- |
| [`/commerce/invoicing/billing-schedules/actions/create`](./connect-resources-create-billing-schedules.md) (POST) | Generate billing schedules for orders by using context service. |
| [`/commerce/invoicing/standalone/billing-schedules/actions/create`](./connect-resources-create-billing-schedules-from-any-transaction.md) (POST) | Generate billing schedules from any internal or external transaction by using context service. |
| [`/commerce/invoicing/billing-schedules/collection/actions/recover`](./connect-resources-recover-billing-schedules.md) (POST) | Recover the latest generated invoice associated with the billing schedules in the `Error` or `Processing` status. |
| [`/commerce/invoicing/actions/suspend-billing`](./connect-resources-suspend-billing.md) (POST) | Suspend billing for billing schedule groups or an account for a predefined period. |
| [`/commerce/invoicing/actions/resume-billing`](./connect-resources-resume-billing.md) (POST) | Resume billing for billing schedule groups or an account that’s currently on hold. |

## Invoices

| Resource | Description |
| --- | --- |
| [`/commerce/invoicing/invoices/collection/actions/post`](./connect-resources-draft-to-posted-invoice.md) (POST) | Update the status of the invoice from Draft to Posted. |
| [`/commerce/invoicing/invoice-batch-runs/{invoiceBatchRunId}/actions/draft-to-posted`](./connect-resources-batch-draft-invoices-to-posted.md) (POST) | Update a batch of invoices from `Draft` to `Posted` status for a credit memo application. |
| [`/commerce/invoicing/invoices/collection/actions/preview`](./connect-resources-preview-invoices.md) (POST) | Generate preview invoices, which includes the estimated tax amounts, for a billing transaction for the next two billing periods. |
| [`/commerce/invoicing/invoices/collection/actions/ingest`](./connect-resources-invoices-ingestion.md) (POST) | Ingest or generate an invoice from an internal or external billing transaction data. |
| [`/commerce/billing/invoices/invoice-batch-docgen/{invoiceBatchRunId}/actions/{actionName}`](./connect-resources-invoice-batch-docgen.md) (POST) | Asynchronously generate PDF documents for the invoices that are in the `Draft` or `Posted` status and are associated with an invoice batch run record. |
| [`/commerce/billing/invoices/invoice-batch-docgen/{invoiceBatchRunId}/actions/{actionName}`](./connect-resources-invoice-batch-docgen-retry.md) (POST) | Asynchronously regenerate PDF documents for the invoices that are in the `Draft` or `Posted` status and failed in an earlier invoice batch run. |
| [`/commerce/invoicing/invoices/actions/write-off`](./connect-resources-write-off-invoices.md) (POST) | Create credit memos with the total charge amount on the invoice as the write-off amount and close the invoice. |
| [`/commerce/invoicing/invoice-batch-runs/actions/send-email`](./connect-resources-send-email-for-invoice-batch-run.md) (POST) | Send emails for the posted invoices of a specified invoice batch run ID. |
| [`/commerce/invoicing/invoices/collection/actions/generate`](./connect-resources-create-invoices-from-billing-schedules.md) (POST) | Create an invoice for an account, order, or a list of billing schedules. |
| [`/revenue/billing/transactions/actions/apply`](./connect-resources-rules-application.md) (POST) | Apply payments and credits to an account’s invoices based on specified rules defined on the Billing Settings page. |
| [`/revenue/billing/document/actions/generate`](./connect-resources-generate-documents.md) (POST) | Generate an invoice document for a record, and update any junction object record. |

## Invoice Scheduler

| Resource | Description |
| --- | --- |
| [`/commerce/invoicing/invoice-schedulers`](./connect-resources-create-an-invoice-scheduler.md) (POST) | Create or update an invoice scheduler to automatically generate invoices. Use the criteria and filters of the invoice scheduler to set up the invoice run schedules based on your requirements. |
| [`/commerce/invoicing/invoice-batch-runs/{invoiceBatchRunId}/actions/recover`](./connect-resources-recover-errored-invoices-batch-run.md) (POST) | Recover records associated with a failed invoice run. Recovery is required only when billing schedules remain in the `Processing`, `Void In Progress`, or `Error` status. |

## Invoice Sequencing

| Resource | Description |
| --- | --- |
| [`/connect/sequences/policy`](./connect-resources-create-sequence-policy.md) (POST) | Create a sequence policy to configure a unique, sequential number for posted invoices or credit memos. |
| [`/connect/sequences/policy/{sequencePolicyId}`](./connect-resources-update-sequence-policies.md) (PATCH) | Update the settings of a sequence policy that defines how unique, sequential numbers are generated by using specific patterns, values, and filters. |
| [`/connect/sequences/actions/assign`](./connect-resources-sequences-assignment.md) (POST) | Assign sequence pattern values to objects based on the configured sequence policy. |
| [`/connect/sequences/gap-reconciliation`](./connect-resources-sequences-gap-reconciliation.md) (POST) | Restore a missing sequence value identified by using this API in gapless-enabled sequences. This sequence value can be used later in the subsequent sequence policy numbering, ensuring there are no gaps. |

## Account Statement

| Resource | Description |
| --- | --- |
| [`/revenue/billing/accounts/{accountId}/statement`](./connect-resources-generate-account-statement.md) (POST) | Generate comprehensive account statement with transaction history and balance information. |

## Payments

| Resource | Description |
| --- | --- |
| [`/commerce/billing/payments/{paymentId}/actions/apply`](./connect-resources-payment-line-apply.md) (POST) | Allocate the balance of a payment to reduce the balance of an invoice. The response includes an ID of the payment line invoice or payment line invoice line that represents the payment balance allocated against the invoice. |
| [`/commerce/billing/payments/{paymentId}/paymentlines/{paymentLineId}/actions/unapply`](./connect-resources-payment-line-unapply.md) (POST) | Revert the application of a payment line from an invoice, and return the payment and invoices to their preapplication state. Use this API to correct an input during the payment application process. |
| [`/commerce/billing/refunds/{refundId}/actions/apply`](./connect-resources-apply-refund-to-payment.md) (POST) | Make a refund transaction against a payment. |

## Tax Calculation

| Resource | Description |
| --- | --- |
| [`/commerce/taxes/actions/calculate`](./connect-resources-calculate-taxes.md) (POST) | Calculate tax for a transaction. |
| [`/commerce/invoicing/invoices/collection/actions/calculate-estimated-tax`](./connect-resources-calculate-estimated-tax.md) (POST) | Calculate estimated tax for invoices with invoice lines that have the `TaxProcessingStatus` as either `Pending` or `Estimated`. |

## Salesforce Commerce Payments API

| Resource | Description |
| --- | --- |
| [`/commerce/payments/payment-methods`](https://developer.salesforce.com/docs/commerce/salesforce-commerce/references/comm-ccs-payments-ref?meta=tokenizePaymentMethod) (POST) | Tokenize a payment method. |
| [`/commerce/payments/sales`](https://developer.salesforce.com/docs/commerce/salesforce-commerce/references/comm-ccs-payments-ref?meta=salePayment) (POST) | Make a payment sale. |
| [`/commerce/payments/payments/{paymentId}/refunds`](https://developer.salesforce.com/docs/commerce/salesforce-commerce/references/comm-ccs-payments-ref?meta=createPaymentRefund) (POST) | Create a refund for a payment. |
| [`/commerce/payments/authorizations`](https://developer.salesforce.com/docs/commerce/salesforce-commerce/references/comm-ccs-payments-ref?meta=authorizePayment) (POST) | Authorize a payment. |
| [`/commerce/payments/authorizations/{authorizationId}/reversals`](https://developer.salesforce.com/docs/commerce/salesforce-commerce/references/comm-ccs-payments-ref?meta=reverseAuthorization) (POST) | Reverse an authorized payment. |
| [`/commerce/payments/authorizations/{authorizationId}/captures`](https://developer.salesforce.com/docs/commerce/salesforce-commerce/references/comm-ccs-payments-ref?meta=capturePayment) (POST) | Capture an authorized payment. |

- 

**[Billing Business API Limits](./billing-business-apis-limits.md)**

Learn about the default limits on the usage of the Billing business APIs.

- 

**[Resources](./billing-business-apis-resources.md)**

Learn more about the available Billing API resources.

- 

**[Request Bodies](./billing-business-apis-requests.md)**

Learn more about the available request bodies of Billing APIs.

- 

**[Response Bodies](./billing-business-apis-responses.md)**

Learn more about the available response bodies of Billing APIs.

**See Also**

- [*Connect REST API Developer Guide*: Introduction](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/intro_what_is_chatter_connect.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-business-api-overview.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
