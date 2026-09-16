# Revenue Cloud Billing Business APIs - Complete Reference
## Developer Guide v264 (API v68.0, Winter '27)

**Source**: `/commerce/`, `/revenue/`, `/connect/` API resources
**Documentation**: Revenue Lifecycle Management Developer Guide, Chapter 11: Billing

---

## Summary
- **Total Endpoints**: 48 (as of RLM v264; grounded re-extraction from the 264/v68.0 dev-guide snapshot — up from 30 in the v260 extraction)
- **Provenance split**: 42 of the 48 are grounded in the 264 (v68.0) RLM dev-guide snapshot. The remaining 6 (Section 9, Salesforce Commerce Payments) are external Commerce Payments APIs — they are not part of the 264 RLM dev-guide and are retained here for continuity only.
- **API Versions Supported**: v60.0+ (individual resources carry their own "Available Version" from v62.0–v66.0; see per-endpoint notes below)
- **HTTP Methods**: Primarily POST, with GET (Billing Arrangement), PUT (Batch Invoice Scheduler update), and PATCH (sequence policy updates, Payment Scheduler Update)
- **Base Path Patterns**: `/commerce/`, `/revenue/`, `/connect/`

---

## Functional Areas and Endpoints

### 1. CREDITS (10 Endpoints)

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/commerce/invoicing/credit-memos/creditMemoId/actions/apply` | Adjust or correct already issued invoices by applying an existing credit memo to an invoice. | v62.0 |
| 2 | POST | `/commerce/invoicing/credit-memos/actions/generate` | Create a credit memo without applying it to an invoice. You can credit the invoice at a later date. | v62.0 |
| 3 | POST | `/commerce/invoicing/invoices/invoiceId/actions/void` | Void a posted invoice to rebill the customer, if necessary. | v62.0 |
| 4 | POST | `/commerce/invoicing/credit/collection/actions/post` | Post a draft credit memo to a credit memo record for review and approval. | v65.0 |
| 5 | POST | `/commerce/invoicing/credit-memo-inv-applications/creditMemoInvApplicationId/actions/unapply` | Unapply a credit memo from an invoice and return the invoice and the credit memo to their pre-application states. | v62.0 |
| 6 | POST | `/commerce/invoicing/credit-memo-lines/creditMemoLineId/actions/apply` | Adjust or correct already issued invoices by applying an existing credit memo line to an invoice line. | v62.0 |
| 7 | POST | `/commerce/invoicing/credit-memo-line-invoice-line/creditMemoLineInvoiceLineId/actions/unapply` | Unapply a credit memo line from an invoice line and return the invoice line and the credit memo line to their pre-application states. | v62.0 |
| 8 | POST | `/commerce/invoicing/invoices/invoiceId/actions/convert-to-credit` | Convert a list of invoice lines with a negative amount into a posted credit memo. Applicable for a single invoice at a time. | v62.0 |
| 9 | POST | `/commerce/invoicing/invoices/invoiceId/actions/credit` | Create a credit memo and apply it to an invoice. The credit memo can fully or partially credit the invoice. | v62.0 |
| 10 | POST | `/commerce/billing/credit-memos/creditMemoId/actions/void` | Void a credit memo in posted state. | v66.0 |

Endpoints 5–10 are new to this doc (not present in the v260/v66.0 extraction); they are documented in the 264 dev-guide but several were introduced in earlier API versions (v62.0–v66.0) and were simply missing from the prior extraction.

**Common Request Body Fields**:
- `creditMemoId` (URI parameter, endpoints 1, 10)
- `invoiceId` (URI parameter, endpoint 3)
- `creditMemoInvApplicationId` (URI parameter, endpoint 5)
- `creditMemoLineId` (URI parameter, endpoint 6)
- `creditMemoLineInvoiceLineId` (URI parameter, endpoint 7)
- `applications` (array of Credit Memo Apply Application Input, Required — endpoint 1; each entry: `appliedToId` Required, `amount` Double Required, `description` Optional, `effectiveDate` Optional)
- `billingAccountId` (String, Required — endpoint 2)
- `charges` (array of Standalone Credit Memo Charge Input, Required — endpoint 2; requires at least one charge line)
- `billToContactId`, `currencyIsoCode`, `externalReference`, `externalReferenceDataSource` (String, Optional — endpoint 2)
- `description` (String, Optional — endpoints 2, 5, 7, 8, 9)
- `effectiveDate` (String — Optional on 2, 5, 7; Required on 8; Optional on 9)
- `taxEffectiveDate` (Optional — endpoints 2, 9)
- `applyCreditDetails` (array of Credit Memo Line Application Input, Required — endpoint 6)
- `invoiceLines` (String[] on endpoint 8, Optional despite being the core payload; array of Credit Invoice Line Input on endpoint 9, Required)
- `taxStrategy` (String — Required on endpoints 2 and 9; valid values on endpoint 2: `Ignore`/`ManualOverride`/`Calculate`; valid values on endpoint 9: `Ignore`/`ManualOverride`/`CopyFromInvoiceLine`/`Calculate`)
- `type` (String, Optional — endpoints 2, 9; valid values `Posted`/`Draft`)
- `correlationId` (String, Optional — endpoint 4)
- `creditMemoIds` (String[], Required — endpoint 4; the API posts one draft credit memo per request despite the array type)
- Endpoint 3 (Void a Posted Invoice) has no request body by design — only the `invoiceId` path parameter
- Endpoint 10 (Void Posted Credit Memo) has no request body by design — only the `creditMemoId` path parameter

Sources: `connect_resources_credit_memo_apply.htm.md`, `connect_requests_credit_memo_apply_application_input.htm.md`, `connect_resources_create_a_standalone_credit_memo.htm.md`, `connect_requests_standalone_credit_memo_charge_input.htm.md`, `connect_resources_void_a_posted_invoice.htm.md`, `connect_resources_post_draft_credit_memo.htm.md`, `connect_resources_credit_memo_invoice_application_unapply.htm.md`, `connect_requests_credit_memo_unapply_input.htm.md`, `connect_resources_credit_memo_line_level_apply.htm.md`, `connect_requests_credit_memo_line_apply_input.htm.md`, `connect_resources_credit_memo_line_level_unapply.htm.md`, `connect_requests_credit_memo_line_unapply_input.htm.md`, `connect_resources_convert_negative_invoice_lines_to_credit.htm.md`, `connect_requests_convert_negative_invoice_lines_input.htm.md`, `connect_resources_create_and_apply_a_credit_memo.htm.md`, `connect_requests_credit_invoice_input.htm.md`, `connect_resources_void_posted_credit_memo.htm.md`, `connect_requests_void_posted_credit_memo_input.htm.md`.

---

### 2. BILLING SCHEDULES (5 Endpoints)

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/commerce/invoicing/billing-schedules/actions/create` | Generate billing schedules for orders by using context service. Request body: `billingTransactionIds` (String[], Required). | v62.0 |
| 2 | POST | `/commerce/invoicing/actions/suspend-billing` | Suspend billing for billing schedule groups or an account for a predefined period. | v63.0 |
| 3 | POST | `/commerce/invoicing/actions/resume-billing` | Resume billing for billing schedule groups or an account that's currently on hold. | v63.0 |
| 4 | POST | `/commerce/invoicing/standalone/billing-schedules/actions/create` | Generate billing schedules from any internal or external transaction by using context service. | v64.0 |
| 5 | POST | `/commerce/invoicing/billing-schedules/collection/actions/recover` | Recover the latest generated invoice associated with billing schedules in the `Error` or `Processing` status. | v62.0 |

Endpoints 4 and 5 are new to this doc. Endpoint 4's request body (`connect_requests_context_aware_standalone_billing_schedule_input.htm.md`) takes `transactionContextDetails` (Standalone Billing Schedule Metadata Input, Required — nested fields `contextDefinitionName` Required v64.0, `intraContextCustomMappingName` Optional v65.0, `readContextMappingName` Required v64.0, `saveContextMappingName` Required v64.0) and `transactionDetails` (String, Required v64.0 — a JSON-string transaction payload). Endpoint 5's request body (`connect_requests_billing_schedule_recovery_input.htm.md`) takes `billingScheduleIds` (String[], Required; the article notes only one billing schedule is recovered per API request despite the array type).

**Note on the `billing_schedule_input_for_*` article family**: `connect_requests_billing_schedule_input_for_{amendment, bundled_products_new_sale, cancellation, early_renewal, evergreen_new_sale, one_time_new_sale, ramps_new_sale, renewal, termed_new_sale, usage_new_sale}.htm.md` are **not separate endpoints** — they document the internal shape of the `transactionDetails` JSON string passed to endpoint 4 (Create Standalone Billing Schedules), discriminated inside that string by `SellingModelType__std` (`OneTime`/`TermDefined`/`Evergreen`) and `BillingActionType__std`. No endpoint rows were added for this family per the grounding rules (add endpoints only, not request-body variants).

**Common Request Body Fields**:
- `billingTransactionIds` (String[], Required — endpoint 1)
- `referenceIds` (array of Suspend Billing Object Input, Required — endpoint 2; each entry: `referenceId` String, `suspendDate` String, `resumeDate` String — account or billing schedule group ID plus suspend/resume dates)
- `referenceIds` (array of Resume Billing Object Input, Required — endpoint 3; each entry: `referenceId` String, `resumeDate` String)
- `transactionContextDetails`, `transactionDetails` (endpoint 4)
- `billingScheduleIds` (String[], Required — endpoint 5; the article notes only one billing schedule is recovered per API request despite the array type)

Sources: `connect_resources_create_billing_schedules.htm.md`, `connect_resources_suspend_billing.htm.md`, `connect_requests_suspend_billing_entity_input.htm.md`, `connect_resources_resume_billing.htm.md`, `connect_requests_resume_billing_entity_input.htm.md`, `connect_resources_create_billing_schedules_from_any_transaction.htm.md`, `connect_requests_context_aware_standalone_billing_schedule_input.htm.md`, `connect_requests_context_aware_standalone_billing_schedule_metadata_input.htm.md`, `connect_resources_recover_billing_schedules.htm.md`, `connect_requests_billing_schedule_recovery_input.htm.md`, `connect_requests_billing_schedule_input_for_one_time_new_sale.htm.md` (representative variant, confirmed by skimming termed_new_sale/renewal/amendment/cancellation).

---

### 3. INVOICES (11 Endpoints)

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/commerce/invoicing/invoices/collection/actions/post` | Update the status of the invoice from Draft to Posted. | v62.0 |
| 2 | POST | `/commerce/invoicing/invoices/collection/actions/preview` | Generate preview invoices, which includes the estimated tax amounts, for a billing transaction for the next two billing periods. | v63.0 |
| 3 | POST | `/commerce/invoicing/invoices/collection/actions/ingest` | Ingest or generate an invoice from an internal or external billing transaction data. | v63.0 |
| 4 | POST | `/commerce/invoicing/invoices/actions/write-off` | Create credit memos with the total charge amount on the invoice as the write-off amount and close the invoice. | v64.0 |
| 5 | POST | `/commerce/invoicing/invoice-batch-runs/actions/send-email` | Send emails for the posted invoices of a specified invoice batch run ID. | v65.0 |
| 6 | POST | `/commerce/invoicing/invoices/collection/actions/generate` | Create an invoice for an account, order, or a list of billing schedules. | v62.0 |
| 7 | POST | `/revenue/billing/transactions/actions/apply` | Apply payments and credits to an account's invoices based on specified rules defined on the Billing Settings page. | v66.0 |
| 8 | POST | `/revenue/billing/document/actions/generate` | Generate an invoice document for a record, and update any junction object record. | v66.0 |
| 9 | POST | `/commerce/invoicing/invoice-batch-runs/invoiceBatchRunId/actions/draft-to-posted` | Update a batch of invoices from Draft to Posted status for a credit memo application. | v62.0 |
| 10 | POST | `/commerce/billing/invoices/invoice-batch-docgen/invoiceBatchRunId/actions/actionName` | Asynchronously generate PDF documents for invoices in Draft or Posted status associated with an invoice batch run record (`actionName` = `run`). | v63.0 |
| 11 | POST | `/commerce/billing/invoices/invoice-batch-docgen/invoiceBatchRunId/actions/actionName` | Asynchronously regenerate PDF documents for invoices in Draft or Posted status that failed in an earlier invoice batch run (same URI template, `actionName` = `retry`). | v63.0 |

Endpoints 9–11 are new to this doc. Endpoint 9 (`connect_resources_batch_draft_invoices_to_posted.htm.md`) documents no request body — only the `invoiceBatchRunId` path parameter. Endpoints 10 and 11 share one URI template distinguished by the `actionName` path segment (`run` vs `retry`); neither documents a request body (`connect_resources_invoice_batch_docgen.htm.md`, `connect_resources_invoice_batch_docgen_retry.htm.md`); the response shape for both is `connect_responses_batch_invoice_doc_gen_output.htm.md`.

**Common Request Body Fields**:
- `correlationId` (String, Optional — endpoints 1, 6)
- `invoiceIds` (String[], Required — endpoint 1; the API posts one draft invoice per request despite the array type)
- `billingTransactionId` (String, Required — endpoint 2; String, Required if `accountId`/`billingScheduleIds` is absent — endpoint 6)
- `numberOfBillingPeriods` (Integer, Optional, v64.0 — endpoint 2), `previewDate` (String, Optional — endpoint 2)
- `invoices` (array of Invoice Ingestion Input, Required — endpoint 3; API supports one invoice per request)
- `invoices` (array of Posted Invoice Write-Off Input, Required — endpoint 4; each entry: `invoiceId`, `reasonCode`, `description`)
- `invoiceBatchRunId` (String, Required — endpoint 5; this is a **request body field**, not a URI parameter — the endpoint-5 resource `/commerce/invoicing/invoice-batch-runs/actions/send-email` has no path placeholder for it. It IS a URI parameter for endpoints 9, 10, 11, whose paths include the `invoiceBatchRunId` segment.)
- `accountId` (String, Required if `billingScheduleIds`/`billingTransactionId` is absent, v63.0 — endpoint 6)
- `action` (String, Required; valid values `Draft`/`Posted`, v62.0 — endpoint 6)
- `billingScheduleIds` (String[], Required if `accountId`/`billingTransactionId` is absent, v62.0 — endpoint 6; max 200 IDs)
- `invoiceDate`, `targetDate` (String, Required, v62.0 — endpoint 6)
- `actionName` (URI parameter, endpoints 10, 11)

Sources: `connect_resources_draft_to_posted_invoice.htm.md`, `connect_resources_preview_invoices.htm.md`, `connect_resources_invoices_ingestion.htm.md`, `connect_resources_write_off_invoices.htm.md`, `connect_resources_send_email_for_invoice_batch_run.htm.md`, `connect_resources_create_invoices_from_billing_schedules.htm.md`, `connect_resources_batch_draft_invoices_to_posted.htm.md`, `connect_resources_invoice_batch_docgen.htm.md`, `connect_resources_invoice_batch_docgen_retry.htm.md`, `connect_responses_batch_invoice_doc_gen_output.htm.md`, `connect_resources_rules_application.htm.md`, `connect_resources_generate_documents.htm.md`.

---

### 4. INVOICE SCHEDULER (3 Endpoints)

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/commerce/invoicing/invoice-schedulers` | Create an invoice scheduler to automatically generate invoices. Use the criteria and filters of the invoice scheduler to set up the invoice run schedules based on your requirements. | v62.0 |
| 2 | PUT | `/commerce/invoicing/invoice-schedulers/billingBatchSchedulerId` | Update an invoice scheduler. PUT is supported only for invoice schedulers in `Draft` or `Inactive` status. | v63.0 |
| 3 | POST | `/commerce/invoicing/invoice-batch-runs/invoiceBatchRunId/actions/recover` | Recover records associated with a failed invoice run. Recovery is required only when billing schedules remain in the Processing, Void In Progress, or Error status. | v62.0 |

Endpoints 2 and 3 are new to this doc. Endpoint 2 (PUT) shares the same resource family and request body shape as endpoint 1 (POST) — both are documented under the single "Batch Invoice Scheduler (POST, PUT)" article (`connect_resources_create_an_invoice_scheduler.htm.md`); PUT is available from v63.0 and only accepted while the scheduler's `status` is `Draft` or `Inactive`. Endpoint 3 documents no request body — only the `invoiceBatchRunId` path parameter (`connect_resources_recover_errored_invoices_batch_run.htm.md`); response shape is `connect_responses_invoice_batch_run_recovery_output.htm.md`.

**Common Request Body Fields** (endpoints 1 and 2):
- `billingBatchSchedulerId` (URI parameter, endpoint 2 only)
- `schedulerName` (String, Required, v62.0)
- `status` (String, Required; valid values `Draft`/`Active`/`Inactive`, v62.0)
- `invoiceStatus` (String, Required; valid values `Draft`/`Posted`, v62.0)
- `frequencyCadence` (String, Required; valid values `Once`/`Daily`/`Weekly`/`Monthly`, v62.0)
- `frequencyCadenceOptions` (Object, Required, v62.0)
- `preferredTime` (String, Required, v62.0)
- `startDate` (String, Required, v62.0)
- `endDate` (String, Optional, v63.0)
- `timezone` (String, Optional, v62.0)
- `isInvoiceDateFromRunDate` (Boolean, Optional, v63.0)
- `invoiceDate`, `targetDate` (String, Required if `frequencyCadence` is `Once`, v62.0)
- `invoiceDateOffset`, `targetDateOffset` (Integer, Required if `frequencyCadence` is `Daily`, `Weekly`, or `Monthly`, v62.0)
- `filterCriteria` (array of Batch Invoice Filter Criteria Input, Optional, v62.0)
- `invoiceBatchRunId` (URI parameter, endpoint 3)

---

### 5. INVOICE SEQUENCING (4 Endpoints) — versions confirmed; Common Request Body Fields corrected (PR #459 sweep — prior field list was fabricated)

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/connect/sequences/policy` | Create a sequence policy to configure a unique, sequential number for posted invoices or credit memos. | v65.0 |
| 2 | PATCH | `/connect/sequences/policy/sequencePolicyId` | Update the settings of a sequence policy that defines how unique, sequential numbers are generated by using specific patterns, values, and filters. | v65.0 |
| 3 | POST | `/connect/sequences/actions/assign` | Assign sequence pattern values to objects based on the configured sequence policy. | v65.0 |
| 4 | POST | `/connect/sequences/gap-reconciliation` | Restore a missing sequence value identified by using this API in gapless-enabled sequences. This sequence value can be used later in the subsequent sequence policy numbering, ensuring there are no gaps. | v65.0 |

Sources: `connect_resources_create_sequence_policy.htm.md`, `connect_resources_update_sequence_policies.htm.md`, `connect_resources_sequences_assignment.htm.md`, `connect_resources_sequences_gap_reconciliation.htm.md` — paths and Available Version confirmed unchanged vs. the v260 extraction; the Common Request Body Fields list below was rewritten against these four articles (the prior field list was fabricated).

**Common Request Body Fields**:
- `sequencePolicyId` (URI parameter for PATCH, endpoint 2)
- `name` (String, Required — endpoints 1, 2)
- `description` (String, Optional — endpoints 1, 2)
- `effectiveFromDateTime` (String, Required — endpoints 1, 2), `expirationDateTime` (String, Optional — endpoints 1, 2)
- `filterCriteria` (String, Required — endpoints 1, 2), `selectionCondition` (array of Selection Condition Input, Optional — endpoints 1, 2), `selectionLogic` (String, Optional — endpoints 1, 2)
- `isActive` (Boolean, Required — endpoints 1, 2)
- `sequenceMode` (String, Required; valid values `Basic`/`Gapless` — endpoints 1, 2)
- `sequencePattern` (String, Required — endpoints 1, 2)
- `sequenceStartNumber` (Integer, Required — endpoints 1, 2), `incrementNumber` (Integer, Required — endpoints 1, 2), `maximumSequenceNumber` (Integer, Optional — endpoints 1, 2), `minimumSequenceNumberWidth` (Integer, Optional — endpoints 1, 2)
- `targetObject` (String, Required; valid values `Invoice`/`CreditMemo` (v66.0+) — endpoints 1, 2)
- `dateStampFormat` (String, Required — endpoints 1, 2), `timeZone` (String, Optional — endpoints 1, 2)
- `targetObjectIds` (String[], Required — endpoint 3); `sequencePolicyId` (String, Optional — endpoint 3); `shouldPublishPlatformEvent` (Boolean, Optional — endpoint 3)
- `sequencePolicyIds` (String[], Required if `targetObjects` is absent — endpoint 4); `targetObjects` (String[], Required if `sequencePolicyIds` is absent; valid values `Invoice`/`CreditMemo` (v66.0+) — endpoint 4). The two properties are mutually exclusive — don't specify both.
- Note: `policyName`, `patternPrefix`, `startNumber`, `endNumber`, `sequenceNumber`, and `objectName` are **not** the real field names — they were close-but-incorrect placeholders, replaced above with the snapshot's actual field names (`name`, `sequencePattern`, `sequenceStartNumber`, `maximumSequenceNumber`, `incrementNumber`, `targetObject`, respectively).

---

### 6. ACCOUNT STATEMENT (1 Endpoint) — path and version unchanged from v260; Common Request Body Fields corrected (PR #459 sweep — prior field list was fabricated)

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/revenue/billing/accounts/accountId/statement` | Generate comprehensive financial statements with transaction history and balance information. | v66.0 |

Source: `connect_resources_generate_account_statement.htm.md`.

**Common Request Body Fields**:
- `accountId` (URI parameter)
- `startDate` (String, Required — format `YYYY-MM-DD`; the system processes records up to 90 days from this date)
- `associatedAccountIds` (String[], Optional — up to 50 associated account IDs from the hierarchy)
- `transactionTypes` (String[], Optional; valid values `All`/`CreditMemo`/`DebitMemo`/`Invoice`/`Payment`/`Refund`)
- `sortBy`, `sortingOrder` (String, Optional; `sortingOrder` valid values `Ascending`/`Descending`)
- `shouldShowOpenBalancesOnly` (Boolean, Optional)
- `documentTemplateId` (String, Optional)
- `customFields` (String, Optional, v67.0 — JSON string of custom fields to include)
- `correlationId` (String, Optional)
- Note: `statementDate` and `endDate` are **not** documented fields for this endpoint — they were removed from this list as fabricated/incorrect; the snapshot's actual field set is as listed above.

---

### 7. PAYMENTS (3 Endpoints)

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/commerce/billing/payments/paymentId/actions/apply` | Allocate the balance of a payment to reduce the balance of an invoice. The response includes an ID of the payment line invoice or payment line invoice line that represents the payment balance allocated against the invoice. | v64.0 |
| 2 | POST | `/commerce/billing/refunds/refundId/actions/apply` | Make a refund transaction against a payment. | v64.0 |
| 3 | POST | `/commerce/billing/payments/paymentId/paymentlines/paymentLineId/actions/unapply` | Revert the application of a payment line from an invoice, and return the payment and invoices to their pre-application state. | v64.0 |

Endpoint 3 is new to this doc. Path parameters `paymentId` and `paymentLineId` (both Required). Body: `comments` (String, Optional), `effectiveDate` (String, Optional). Sources: `connect_resources_payment_line_apply.htm.md`, `connect_resources_apply_refund_to_payment.htm.md`, `connect_resources_payment_line_unapply.htm.md`, `connect_requests_payment_line_unapply_input.htm.md`.

**Common Request Body Fields**:
- `paymentId` (URI parameter, endpoints 1, 3)
- `refundId` (URI parameter, endpoint 2)
- `paymentLineId` (URI parameter, endpoint 3)
- `appliedToId` (String, Required — endpoints 1, 2; ID of the invoice line (endpoint 1) or payment/credit memo record (endpoint 2) the amount is applied to)
- `amount` (Double, Required — endpoints 1, 2)
- `associatedAccountId` (String, Optional — endpoint 1 only)
- `comments` (String, Optional — endpoints 1, 2, 3)
- `effectiveDate` (String, Optional — endpoints 1, 2, 3)
- Note: `invoiceId`, `refundAmount`, `paymentAmount`, and `reason` are **not** real fields on these endpoints — they were removed from this list as fabricated/incorrect; the snapshot's actual field set is as listed above.

---

### 8. TAX CALCULATION (2 Endpoints) — paths and versions unchanged from v260; Common Request Body Fields corrected (PR #459 sweep — prior field list was fabricated)

| # | HTTP Method | URI | Description | Available Version |
|---|---|---|---|---|
| 1 | POST | `/commerce/taxes/actions/calculate` | Calculate tax for a transaction. | v62.0 |
| 2 | POST | `/commerce/invoicing/invoices/collection/actions/calculate-estimated-tax` | Calculate estimated tax for invoices with invoice lines that have the TaxProcessingStatus as either Pending or Estimated. | v63.0 |

Sources: `connect_resources_calculate_taxes.htm.md`, `connect_resources_calculate_estimated_tax.htm.md`.

**Common Request Body Fields**:
- `lineItems` (array of Line Item Input, Required — endpoint 1)
- `taxEngineId` (String, Required — endpoint 1)
- `taxType` (String, Required; valid values `Actual`/`Estimated` — endpoint 1)
- `transactionDate` (String, Required — endpoint 1)
- `addresses` (Object, Optional — endpoint 1), `customerDetails` (Object, Optional — endpoint 1), `sellerDetails` (Object, Optional — endpoint 1)
- `currencyIsoCode`, `description`, `documentCode`, `effectiveDate`, `referenceDocumentCode`, `referenceEntityId` (String, Optional — endpoint 1)
- `isCommit`, `shouldVoidTax` (Boolean, Optional — endpoint 1)
- `taxTransactionType` (String, Optional; valid values `Debit`/`Credit`/`Void` — endpoint 1)
- `correlationId` (String, Optional — endpoint 2)
- `invoiceIds` (String[], Required — endpoint 2; one invoice per API request despite the array type)
- Note: `transactionId`, `invoiceLineItems`, `taxDate`, `jurisdictionCode`, and `taxExemptionNumber` are **not** real fields on either endpoint — they were removed from this list as fabricated/incorrect; the snapshot's actual field set is as listed above.

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
- **Minimum availability varies per endpoint** — the earliest resources appear in Salesforce API v60.0, with others introduced through v62.0–v66.0. See each endpoint's **Available Version** for its own minimum; do not assume all 48 endpoints are available from v60.0.
- 6 of the 48 endpoints (Section 9, Salesforce Commerce Payments) are external Commerce Payments APIs, not part of the 264 RLM dev-guide grounding source — see Section 9's own header for that caveat.
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
