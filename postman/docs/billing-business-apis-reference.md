# Revenue Cloud Billing Business APIs - Complete Reference
## Developer Guide v264 (API v68.0, Winter '27)

**Source**: `/commerce/`, `/revenue/`, `/connect/` API resources
**Documentation**: Revenue Lifecycle Management Developer Guide, Chapter 11: Billing

---

## Summary
- **Total Endpoints**: 47 (as of RLM v264; grounded re-extraction from the 264/v68.0 dev-guide snapshot — up from 30 in the v260 extraction)
- **API Versions Supported**: v60.0+ (individual resources carry their own "Available Version" from v62.0–v66.0; see per-endpoint notes below)
- **HTTP Methods**: Primarily POST, with GET (Billing Arrangement) and PATCH (sequence policy updates, Payment Scheduler Update)
- **Base Path Patterns**: `/commerce/`, `/revenue/`, `/connect/`

---

## Functional Areas and Endpoints

### 1. CREDITS (10 Endpoints)

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/commerce/invoicing/credit-memos/creditMemoId/actions/apply` | Adjust or correct already issued invoices by applying an existing credit memo to an invoice. | — |
| 2 | POST | `/commerce/invoicing/credit-memos/actions/generate` | Create a credit memo without applying it to an invoice. You can credit the invoice at a later date. | — |
| 3 | POST | `/commerce/invoicing/invoices/invoiceId/actions/void` | Void a posted invoice to rebill the customer, if necessary. | — |
| 4 | POST | `/commerce/invoicing/credit/collection/actions/post` | Post a draft credit memo to a credit memo record for review and approval. | — |
| 5 | POST | `/commerce/invoicing/credit-memo-inv-applications/creditMemoInvApplicationId/actions/unapply` | Unapply a credit memo from an invoice and return the invoice and the credit memo to their pre-application states. | v62.0 |
| 6 | POST | `/commerce/invoicing/credit-memo-lines/creditMemoLineId/actions/apply` | Adjust or correct already issued invoices by applying an existing credit memo line to an invoice line. | v62.0 |
| 7 | POST | `/commerce/invoicing/credit-memo-line-invoice-line/creditMemoLineInvoiceLineId/actions/unapply` | Unapply a credit memo line from an invoice line and return the invoice line and the credit memo line to their pre-application states. | v62.0 |
| 8 | POST | `/commerce/invoicing/invoices/invoiceId/actions/convert-to-credit` | Convert a list of invoice lines with a negative amount into a posted credit memo. Applicable for a single invoice at a time. | v62.0 |
| 9 | POST | `/commerce/invoicing/invoices/invoiceId/actions/credit` | Create a credit memo and apply it to an invoice. The credit memo can fully or partially credit the invoice. | v62.0 |
| 10 | POST | `/commerce/billing/credit-memos/creditMemoId/actions/void` | Void a credit memo in posted state. | v66.0 |

Endpoints 5–10 are new to this doc (not present in the v260/v66.0 extraction); they are documented in the 264 dev-guide but several were introduced in earlier API versions (v62.0–v66.0) and were simply missing from the prior extraction.

**Common Request Body Fields**:
- `creditMemoId` (URI parameter)
- `invoiceId` (URI parameter)
- `creditMemoInvApplicationId` (URI parameter, endpoint 5)
- `creditMemoLineId` (URI parameter, endpoint 6)
- `creditMemoLineInvoiceLineId` (URI parameter, endpoint 7)
- `description` (String, Optional — endpoints 5, 7, 8, 9)
- `effectiveDate` (String — Optional on 5, 7; Required on 8; Optional on 9)
- `applyCreditDetails` (array of Credit Memo Line Application Input, Required — endpoint 6)
- `invoiceLines` (String[] on endpoint 8, Optional despite being the core payload; array of Credit Invoice Line Input on endpoint 9, Required)
- `taxStrategy` (String, Required — endpoint 9; valid values `Ignore`/`ManualOverride`/`CopyFromInvoiceLine`/`Calculate`)
- `taxEffectiveDate` (Optional — endpoint 9)
- `type` (String, Optional — endpoint 9; valid values `Posted`/`Draft`)
- Endpoint 10 (Void Posted Credit Memo) has no request body by design — only the `creditMemoId` path parameter

Sources: `connect_resources_credit_memo_invoice_application_unapply.htm.md`, `connect_requests_credit_memo_unapply_input.htm.md`, `connect_resources_credit_memo_line_level_apply.htm.md`, `connect_requests_credit_memo_line_apply_input.htm.md`, `connect_resources_credit_memo_line_level_unapply.htm.md`, `connect_requests_credit_memo_line_unapply_input.htm.md`, `connect_resources_convert_negative_invoice_lines_to_credit.htm.md`, `connect_requests_convert_negative_invoice_lines_input.htm.md`, `connect_resources_create_and_apply_a_credit_memo.htm.md`, `connect_requests_credit_invoice_input.htm.md`, `connect_resources_void_posted_credit_memo.htm.md`, `connect_requests_void_posted_credit_memo_input.htm.md`.

---

### 2. BILLING SCHEDULES (5 Endpoints)

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/commerce/invoicing/billing-schedules/actions/create` | Generate billing schedules for orders by using context service. Request body: `billingTransactionIds` (String[], Required). | v62.0 |
| 2 | POST | `/commerce/invoicing/actions/suspend-billing` | Suspend billing for billing schedule groups or an account for a predefined period. | — |
| 3 | POST | `/commerce/invoicing/actions/resume-billing` | Resume billing for billing schedule groups or an account that's currently on hold. | — |
| 4 | POST | `/commerce/invoicing/standalone/billing-schedules/actions/create` | Generate billing schedules from any internal or external transaction by using context service. | v64.0 |
| 5 | POST | `/commerce/invoicing/billing-schedules/collection/actions/recover` | Recover the latest generated invoice associated with billing schedules in the `Error` or `Processing` status. | v62.0 |

Endpoints 4 and 5 are new to this doc. Endpoint 4's request body (`connect_requests_context_aware_standalone_billing_schedule_input.htm.md`) takes `transactionContextDetails` (Standalone Billing Schedule Metadata Input, Required — nested fields `contextDefinitionName` Required v64.0, `intraContextCustomMappingName` Optional v65.0, `readContextMappingName` Required v64.0, `saveContextMappingName` Required v64.0) and `transactionDetails` (String, Required v64.0 — a JSON-string transaction payload). Endpoint 5's request body (`connect_requests_billing_schedule_recovery_input.htm.md`) takes `billingScheduleIds` (String[], Required; the article notes only one billing schedule is recovered per API request despite the array type).

**Note on the `billing_schedule_input_for_*` article family**: `connect_requests_billing_schedule_input_for_{amendment, bundled_products_new_sale, cancellation, early_renewal, evergreen_new_sale, one_time_new_sale, ramps_new_sale, renewal, termed_new_sale, usage_new_sale}.htm.md` are **not separate endpoints** — they document the internal shape of the `transactionDetails` JSON string passed to endpoint 4 (Create Standalone Billing Schedules), discriminated inside that string by `SellingModelType__std` (`OneTime`/`TermDefined`/`Evergreen`) and `BillingActionType__std`. No endpoint rows were added for this family per the grounding rules (add endpoints only, not request-body variants).

**Common Request Body Fields**:
- `billingScheduleGroupId`
- `accountId`
- `suspensionReason`
- `resumptionDate`
- `suspensionDate`
- `billingTransactionIds` (String[], endpoint 1)
- `transactionContextDetails`, `transactionDetails` (endpoint 4)
- `billingScheduleIds` (String[], endpoint 5)

Sources: `connect_resources_create_billing_schedules_from_any_transaction.htm.md`, `connect_requests_context_aware_standalone_billing_schedule_input.htm.md`, `connect_requests_context_aware_standalone_billing_schedule_metadata_input.htm.md`, `connect_resources_recover_billing_schedules.htm.md`, `connect_requests_billing_schedule_recovery_input.htm.md`, `connect_resources_create_billing_schedules.htm.md`, `connect_requests_billing_schedule_input_for_one_time_new_sale.htm.md` (representative variant, confirmed by skimming termed_new_sale/renewal/amendment/cancellation).

---

### 3. INVOICES (11 Endpoints)

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/commerce/invoicing/invoices/collection/actions/post` | Update the status of the invoice from Draft to Posted. | — |
| 2 | POST | `/commerce/invoicing/invoices/collection/actions/preview` | Generate preview invoices, which includes the estimated tax amounts, for a billing transaction for the next two billing periods. | — |
| 3 | POST | `/commerce/invoicing/invoices/collection/actions/ingest` | Ingest or generate an invoice from an internal or external billing transaction data. | — |
| 4 | POST | `/commerce/invoicing/invoices/actions/write-off` | Create credit memos with the total charge amount on the invoice as the write-off amount and close the invoice. | — |
| 5 | POST | `/commerce/invoicing/invoice-batch-runs/actions/send-email` | Send emails for the posted invoices of a specified invoice batch run ID. | — |
| 6 | POST | `/commerce/invoicing/invoices/collection/actions/generate` | Create an invoice for an account, order, or a list of billing schedules. | — |
| 7 | POST | `/revenue/billing/transactions/actions/apply` | Apply payments and credits to an account's invoices based on specified rules defined on the Billing Settings page. | v66.0 |
| 8 | POST | `/revenue/billing/document/actions/generate` | Generate an invoice document for a record, and update any junction object record. | v66.0 |
| 9 | POST | `/commerce/invoicing/invoice-batch-runs/invoiceBatchRunId/actions/draft-to-posted` | Update a batch of invoices from Draft to Posted status for a credit memo application. | v62.0 |
| 10 | POST | `/commerce/billing/invoices/invoice-batch-docgen/invoiceBatchRunId/actions/actionName` | Asynchronously generate PDF documents for invoices in Draft or Posted status associated with an invoice batch run record (`actionName` = `run`). | v63.0 |
| 11 | POST | `/commerce/billing/invoices/invoice-batch-docgen/invoiceBatchRunId/actions/actionName` | Asynchronously regenerate PDF documents for invoices in Draft or Posted status that failed in an earlier invoice batch run (same URI template, `actionName` = `retry`). | v63.0 |

Endpoints 9–11 are new to this doc. Endpoint 9 (`connect_resources_batch_draft_invoices_to_posted.htm.md`) documents no request body — only the `invoiceBatchRunId` path parameter. Endpoints 10 and 11 share one URI template distinguished by the `actionName` path segment (`run` vs `retry`); neither documents a request body (`connect_resources_invoice_batch_docgen.htm.md`, `connect_resources_invoice_batch_docgen_retry.htm.md`); the response shape for both is `connect_responses_batch_invoice_doc_gen_output.htm.md`.

**Common Request Body Fields**:
- `invoiceId` (URI parameter)
- `billingTransactionId`
- `invoiceBatchRunId` (URI parameter, endpoints 5, 9, 10, 11)
- `actionName` (URI parameter, endpoints 10, 11)
- `accountId`
- `orderId`
- `billingScheduleIds`
- `TaxProcessingStatus` (Pending, Estimated)

Sources: `connect_resources_batch_draft_invoices_to_posted.htm.md`, `connect_resources_invoice_batch_docgen.htm.md`, `connect_resources_invoice_batch_docgen_retry.htm.md`, `connect_responses_batch_invoice_doc_gen_output.htm.md`, `connect_resources_rules_application.htm.md`, `connect_resources_generate_documents.htm.md`.

---

### 4. INVOICE SCHEDULER (2 Endpoints)

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/commerce/invoicing/invoice-schedulers` | Create or update an invoice scheduler to automatically generate invoices. Use the criteria and filters of the invoice scheduler to set up the invoice run schedules based on your requirements. | — |
| 2 | POST | `/commerce/invoicing/invoice-batch-runs/invoiceBatchRunId/actions/recover` | Recover records associated with a failed invoice run. Recovery is required only when billing schedules remain in the Processing, Void In Progress, or Error status. | v62.0 |

Endpoint 2 is new to this doc. It documents no request body — only the `invoiceBatchRunId` path parameter (`connect_resources_recover_errored_invoices_batch_run.htm.md`); response shape is `connect_responses_invoice_batch_run_recovery_output.htm.md`.

**Common Request Body Fields**:
- `schedulerName`
- `status` (Draft, Active)
- `invoiceStatus` (Posted, Draft)
- `frequencyCadenceOptions`
- `billingBatchSchedulerId`
- `invoiceRunSchedule`
- `filterCriteria`
- `invoiceBatchRunId` (URI parameter, endpoint 2)

---

### 5. INVOICE SEQUENCING (4 Endpoints) — unchanged from v260, versions confirmed

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/connect/sequences/policy` | Create a sequence policy to configure a unique, sequential number for posted invoices or credit memos. | v65.0 |
| 2 | PATCH | `/connect/sequences/policy/sequencePolicyId` | Update the settings of a sequence policy that defines how unique, sequential numbers are generated by using specific patterns, values, and filters. | v65.0 |
| 3 | POST | `/connect/sequences/actions/assign` | Assign sequence pattern values to objects based on the configured sequence policy. | v65.0 |
| 4 | POST | `/connect/sequences/gap-reconciliation` | Restore a missing sequence value identified by using this API in gapless-enabled sequences. This sequence value can be used later in the subsequent sequence policy numbering, ensuring there are no gaps. | v65.0 |

Sources: `connect_resources_create_sequence_policy.htm.md`, `connect_resources_update_sequence_policies.htm.md`, `connect_resources_sequences_assignment.htm.md`, `connect_resources_sequences_gap_reconciliation.htm.md` — paths and field shapes unchanged vs. the v260 extraction; only the Available Version column was added.

**Common Request Body Fields**:
- `sequencePolicyId` (URI parameter for PATCH)
- `policyName`
- `patternPrefix`
- `startNumber`
- `endNumber`
- `sequenceNumber`
- `objectName` (Invoice, CreditMemo)

---

### 6. ACCOUNT STATEMENT (1 Endpoint) — unchanged from v260

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/revenue/billing/accounts/accountId/statement` | Generate comprehensive financial statements with transaction history and balance information. | v66.0 |

Source: `connect_resources_generate_account_statement.htm.md`.

**Common Request Body Fields**:
- `accountId` (URI parameter)
- `statementDate`
- `startDate`
- `endDate`

---

### 7. PAYMENTS (3 Endpoints)

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/commerce/billing/payments/paymentId/actions/apply` | Allocate the balance of a payment to reduce the balance of an invoice. The response includes an ID of the payment line invoice or payment line invoice line that represents the payment balance allocated against the invoice. | — |
| 2 | POST | `/commerce/billing/refunds/refundId/actions/apply` | Make a refund transaction against a payment. | — |
| 3 | POST | `/commerce/billing/payments/paymentId/paymentlines/paymentLineId/actions/unapply` | Revert the application of a payment line from an invoice, and return the payment and invoices to their pre-application state. | v64.0 |

Endpoint 3 is new to this doc. Path parameters `paymentId` and `paymentLineId` (both Required). Body: `comments` (String, Optional), `effectiveDate` (String, Optional). Sources: `connect_resources_payment_line_unapply.htm.md`, `connect_requests_payment_line_unapply_input.htm.md`.

**Common Request Body Fields**:
- `paymentId` (URI parameter)
- `refundId` (URI parameter)
- `paymentLineId` (URI parameter, endpoint 3)
- `invoiceId`
- `refundAmount`
- `paymentAmount`
- `reason`
- `comments` (String, Optional — endpoint 3)
- `effectiveDate` (String, Optional — endpoint 3)

---

### 8. TAX CALCULATION (2 Endpoints) — unchanged from v260, versions confirmed

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/commerce/taxes/actions/calculate` | Calculate tax for a transaction. | v62.0 |
| 2 | POST | `/commerce/invoicing/invoices/collection/actions/calculate-estimated-tax` | Calculate estimated tax for invoices with invoice lines that have the TaxProcessingStatus as either Pending or Estimated. | v63.0 |

Sources: `connect_resources_calculate_taxes.htm.md`, `connect_resources_calculate_estimated_tax.htm.md`.

**Common Request Body Fields**:
- `transactionId`
- `invoiceLineItems`
- `taxDate`
- `jurisdictionCode`
- `taxExemptionNumber`

---

### 9. SALESFORCE COMMERCE PAYMENTS API (6 Endpoints) — unchanged; external Commerce doc links, not part of the 264 RLM dev-guide grounding source

| # | HTTP Method | URI | Description |
|---|---|---|---|
| 1 | POST | `/commerce/payments/payment-methods` | Tokenize a payment method. |
| 2 | POST | `/commerce/payments/sales` | Make a payment sale. |
| 3 | POST | `/commerce/payments/payments/paymentId/refunds` | Create a refund for a payment. |
| 4 | POST | `/commerce/payments/authorizations` | Authorize a payment. |
| 5 | POST | `/commerce/payments/authorizations/authorizationId/reversals` | Reverse an authorized payment. |
| 6 | POST | `/commerce/payments/authorizations/authorizationId/captures` | Capture an authorized payment. |

**Common Request Body Fields**:
- `paymentId` (URI parameter)
- `authorizationId` (URI parameter)
- `paymentMethodDetails`
- `amount`
- `currency`
- `cardDetails`
- `gatewayId`

---

### 10. BILLING ARRANGEMENT (1 Endpoint) — new section, previously absent from this doc

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | GET | `/revenue/billing/billing-arrangement/billingArrangementId` | Retrieve a billing arrangement and its associated billing arrangement lines. | v66.0 |

No request body (GET). Path parameter `billingArrangementId` (Required). Response shape: `connect_responses_billing_arrangement_output.htm.md` / `connect_responses_billing_arrangement_line.htm.md`. Source: `connect_resources_get_billing_arrangement.htm.md`. This resource is listed in the 264 dev-guide's flat Resources index but was not grouped into one of the overview page's named sections — added here as its own section rather than folded into an existing one.

---

### 11. BATCH PAYMENT SCHEDULER (2 Endpoints) — new section, previously absent from this doc

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/commerce/payments/payment-schedulers/` | Create a payment scheduler to automate and process payment runs on a recurring basis. | v64.0 |
| 2 | PATCH | `/commerce/payments/payment-schedulers/billingBatchSchedulerId` | Activate or deactivate a payment scheduler (`Active`, `Canceled`, `Draft`, or `Inactive`). | v64.0 |

**Common Request Body Fields**:
- `schedulerName` (Required, endpoint 1)
- `startDate` (Required, endpoint 1)
- `endDate` (Required if `frequencyCadence` is `Monthly`, endpoint 1)
- `preferredTime` (Required, endpoint 1)
- `frequencyCadence` (Required; valid values `Once`/`Daily`/`Weekly`/`Monthly`, endpoint 1)
- `recursEveryMonthOnDay` (Required if Monthly, endpoint 1)
- `criteriaMatchType` (Required if Monthly; valid values `MatchAny`/`MatchNone`, endpoint 1)
- `filterCriteria` (array of Payment Run Batch Filter Criteria Input, Required if Monthly, endpoint 1 — nested field detail not fully documented in the source article beyond its JSON example)
- `status` (Required; valid values `Active`/`Canceled`/`Draft`/`Inactive` — both endpoints)
- `billingBatchSchedulerId` (URI parameter, endpoint 2)

Distinct from the existing "Invoice Scheduler" section (section 4) — this is a separate Payment Scheduler resource family under `/commerce/payments/`. Sources: `connect_resources_create_payment_scheduler.htm.md`, `connect_requests_payment_scheduler_input.htm.md`, `connect_resources_update_payment_scheduler.htm.md`, `connect_requests_payment_scheduler_update_input.htm.md`.

---

## API Version Information

- **Reference target:** Revenue Cloud API v68.0 (Winter '27)
- **Minimum availability varies per endpoint** — the earliest resources appear in Salesforce API v60.0, with others introduced through v62.0–v66.0. See each endpoint's **Available Version** for its own minimum; do not assume all 47 endpoints are available from v60.0.
- Supports REST protocol only

---

## Key Characteristics

### Request/Response Format
- **Content-Type**: `application/json`
- **HTTP Status Codes**:
  - `200 OK` - Successful request
  - `201 Created` - Resource created
  - `400 Bad Request` - Invalid input
  - `401 Unauthorized` - Authentication required
  - `404 Not Found` - Resource not found
  - `500 Internal Server Error` - Server error

### Common Header Requirements
- `Authorization: Bearer {access_token}`
- `Content-Type: application/json`
- `Accept: application/json`

### Rate Limiting
- Standard Salesforce API rate limits apply
- Batch operations may have specific limits

---

## Additional Resources

- **Request Body Details**: `docs/salesforce/264/dev-guide/articles/billing_business_apis_requests.htm.md` (the 264 dev-guide snapshot is HTML-derived, not paginated — the v260-era page-number citation below is retained for the pre-264 print edition and is unverified against 264)
- **Response Body Details**: `docs/salesforce/264/dev-guide/articles/billing_business_apis_responses.htm.md`
- **Apex Reference**: ConnectApi, InvoiceWriteOff, RulesAppln namespaces (unverified against 264 for this pass — flagged, not re-confirmed)
- **Platform Events** (unverified against 264 for this pass — flagged, not re-confirmed):
  - BillingScheduleCreatedEvent
  - CreditInvoiceProcessedEvent
  - CreditMemoProcessedEvent
  - InvoiceProcessedEvent

---

*Grounded re-extraction from: Revenue Cloud Developer Guide v264 (Winter '27) snapshot at `docs/salesforce/264/dev-guide/articles/`, reconciled against the prior v260 (Spring '26) extraction*
*Last Updated: 2026-09-16*
