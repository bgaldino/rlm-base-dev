# Revenue Cloud Billing Business APIs — Quick Reference

**API Version:** v68.0 (Winter '27) | **Total Endpoints:** 48 | **Source:** RLM Developer Guide (264/Winter '27 dev-guide snapshot), Chapter 11: Billing — grounded re-extraction, up from 30 in the v260 (Spring '26) extraction

**Provenance split**: 42 of the 48 endpoints below are grounded in the 264 (v68.0) RLM dev-guide snapshot. The 6 endpoints in Section 9 (Salesforce Commerce Payments) are external Commerce Payments APIs — they are not part of the 264 RLM dev-guide and are retained here for continuity only. See `billing-business-apis-reference.md` for the full per-endpoint provenance and field detail.

---

## Endpoint Summary by Functional Area

### 1. Credits (10 endpoints)

- `POST /commerce/invoicing/credit-memos/{creditMemoId}/actions/apply`
- `POST /commerce/invoicing/credit-memos/actions/generate`
- `POST /commerce/invoicing/invoices/{invoiceId}/actions/void`
- `POST /commerce/invoicing/credit/collection/actions/post`
- `POST /commerce/invoicing/credit-memo-inv-applications/{creditMemoInvApplicationId}/actions/unapply` *(new — v62.0)*
- `POST /commerce/invoicing/credit-memo-lines/{creditMemoLineId}/actions/apply` *(new — v62.0)*
- `POST /commerce/invoicing/credit-memo-line-invoice-line/{creditMemoLineInvoiceLineId}/actions/unapply` *(new — v62.0)*
- `POST /commerce/invoicing/invoices/{invoiceId}/actions/convert-to-credit` *(new — v62.0)*
- `POST /commerce/invoicing/invoices/{invoiceId}/actions/credit` *(new — v62.0)*
- `POST /commerce/billing/credit-memos/{creditMemoId}/actions/void` *(new — v66.0)*

### 2. Billing Schedules (5 endpoints)

- `POST /commerce/invoicing/billing-schedules/actions/create`
- `POST /commerce/invoicing/actions/suspend-billing`
- `POST /commerce/invoicing/actions/resume-billing`
- `POST /commerce/invoicing/standalone/billing-schedules/actions/create` *(new — v64.0)*
- `POST /commerce/invoicing/billing-schedules/collection/actions/recover` *(new — v62.0)*

### 3. Invoices (11 endpoints)

- `POST /commerce/invoicing/invoices/collection/actions/post`
- `POST /commerce/invoicing/invoices/collection/actions/preview`
- `POST /commerce/invoicing/invoices/collection/actions/ingest`
- `POST /commerce/invoicing/invoices/actions/write-off`
- `POST /commerce/invoicing/invoice-batch-runs/actions/send-email`
- `POST /commerce/invoicing/invoices/collection/actions/generate`
- `POST /revenue/billing/transactions/actions/apply`
- `POST /revenue/billing/document/actions/generate`
- `POST /commerce/invoicing/invoice-batch-runs/{invoiceBatchRunId}/actions/draft-to-posted` *(new — v62.0)*
- `POST /commerce/billing/invoices/invoice-batch-docgen/{invoiceBatchRunId}/actions/run` *(new — v63.0)*
- `POST /commerce/billing/invoices/invoice-batch-docgen/{invoiceBatchRunId}/actions/retry` *(new — v63.0, same URI template as docgen, different `actionName`)*

### 4. Invoice Scheduler (3 endpoints)

- `POST /commerce/invoicing/invoice-schedulers`
- `PUT /commerce/invoicing/invoice-schedulers/{billingBatchSchedulerId}` *(new — v63.0; Draft/Inactive schedulers only)*
- `POST /commerce/invoicing/invoice-batch-runs/{invoiceBatchRunId}/actions/recover` *(new — v62.0)*

### 5. Invoice Sequencing (4 endpoints)

- `POST /connect/sequences/policy`
- `PATCH /connect/sequences/policy/{sequencePolicyId}`
- `POST /connect/sequences/actions/assign`
- `POST /connect/sequences/gap-reconciliation`

### 6. Account Statement (1 endpoint)

- `POST /revenue/billing/accounts/{accountId}/statement`

### 7. Payments (3 endpoints)

- `POST /commerce/billing/payments/{paymentId}/actions/apply`
- `POST /commerce/billing/refunds/{refundId}/actions/apply`
- `POST /commerce/billing/payments/{paymentId}/paymentlines/{paymentLineId}/actions/unapply` *(new — v64.0)*

### 8. Tax Calculation (2 endpoints)

- `POST /commerce/taxes/actions/calculate`
- `POST /commerce/invoicing/invoices/collection/actions/calculate-estimated-tax`

### 9. Salesforce Commerce Payments (6 endpoints)

- `POST /commerce/payments/payment-methods`
- `POST /commerce/payments/sales`
- `POST /commerce/payments/payments/{paymentId}/refunds`
- `POST /commerce/payments/authorizations`
- `POST /commerce/payments/authorizations/{authorizationId}/reversals`
- `POST /commerce/payments/authorizations/{authorizationId}/captures`

### 10. Billing Arrangement (1 endpoint) — new section

- `GET /revenue/billing/billing-arrangement/{billingArrangementId}` *(new — v66.0)*

### 11. Batch Payment Scheduler (2 endpoints) — new section

- `POST /commerce/payments/payment-schedulers/` *(new — v64.0)*
- `PATCH /commerce/payments/payment-schedulers/{billingBatchSchedulerId}` *(new — v64.0)*

---

## HTTP Methods

POST: 44 endpoints (actions, creation, batch operations), PATCH: 2 endpoints (sequence policy updates, Payment Scheduler Update), PUT: 1 endpoint (Invoice Scheduler Update, Draft/Inactive only), GET: 1 endpoint (Billing Arrangement).

## API Base Paths

| Path | Domain |
|------|--------|
| `/commerce/invoicing/` | Invoice and credit memo operations |
| `/commerce/billing/` | Payment, refund, credit memo, and invoice batch docgen operations |
| `/revenue/billing/` | Transaction, document, account statement, and billing arrangement operations |
| `/connect/sequences/` | Invoice sequencing |
| `/commerce/payments/` | Payment processing and batch payment scheduler operations |
| `/commerce/taxes/` | Tax calculations |

## Authentication and Standards

OAuth 2.0 Bearer Token over HTTPS/REST. Content-Type: `application/json`. Minimum API version v60.0; current v68.0 (individual resources carry their own Available Version from v62.0–v66.0 — see `billing-business-apis-reference.md`). Standard Salesforce API rate limits apply.

## Related Domains

- **[Billing APIs (full reference)](billing-business-apis-reference.md)** — comprehensive per-endpoint detail: request/response fields, path/query parameters, and provenance (264-grounded vs. Section 9's external Commerce Payments carryover).

---

*Grounded re-extraction September 16, 2026 from the RLM Developer Guide v264 (Winter '27) dev-guide snapshot at `docs/salesforce/264/dev-guide/articles/`, reconciled against the prior v260 (Spring '26) extraction*
