# Revenue Cloud Billing Business APIs — Quick Reference

**API Version:** v66.0 (Spring '26) | **Total Endpoints:** 30 | **Source:** RLM Developer Guide Chapter 11, Pages 1924–2007

---

## Endpoint Summary by Functional Area

### 1. Credits (4 endpoints)

- `POST /commerce/invoicing/credit-memos/{creditMemoId}/actions/apply`
- `POST /commerce/invoicing/credit-memos/actions/generate`
- `POST /commerce/invoicing/invoices/{invoiceId}/actions/void`
- `POST /commerce/invoicing/credit/collection/actions/post`

### 2. Billing Schedules (3 endpoints)

- `POST /commerce/invoicing/billing-schedules/actions/create`
- `POST /commerce/invoicing/actions/suspend-billing`
- `POST /commerce/invoicing/actions/resume-billing`

### 3. Invoices (8 endpoints)

- `POST /commerce/invoicing/invoices/collection/actions/post`
- `POST /commerce/invoicing/invoices/collection/actions/preview`
- `POST /commerce/invoicing/invoices/collection/actions/ingest`
- `POST /commerce/invoicing/invoices/actions/write-off`
- `POST /commerce/invoicing/invoice-batch-runs/actions/send-email`
- `POST /commerce/invoicing/invoices/collection/actions/generate`
- `POST /revenue/billing/transactions/actions/apply`
- `POST /revenue/billing/document/actions/generate`

### 4. Invoice Scheduler (1 endpoint)

- `POST /commerce/invoicing/invoice-schedulers`

### 5. Invoice Sequencing (4 endpoints)

- `POST /connect/sequences/policy`
- `PATCH /connect/sequences/policy/{sequencePolicyId}`
- `POST /connect/sequences/actions/assign`
- `POST /connect/sequences/gap-reconciliation`

### 6. Account Statement (1 endpoint)

- `POST /revenue/billing/accounts/{accountId}/statement`

### 7. Payments (2 endpoints)

- `POST /commerce/billing/payments/{paymentId}/actions/apply`
- `POST /commerce/billing/refunds/{refundId}/actions/apply`

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

---

## HTTP Methods

POST: 29 endpoints (actions, creation, batch operations), PATCH: 1 endpoint (sequence policy updates).

## API Base Paths

| Path | Domain |
|------|--------|
| `/commerce/invoicing/` | Invoice and credit memo operations |
| `/commerce/billing/` | Payment and refund operations |
| `/revenue/billing/` | Transaction and document operations |
| `/connect/sequences/` | Invoice sequencing |
| `/commerce/payments/` | Payment processing |
| `/commerce/taxes/` | Tax calculations |

## Authentication and Standards

OAuth 2.0 Bearer Token over HTTPS/REST. Content-Type: `application/json`. Minimum API version v60.0; current v66.0. Standard Salesforce API rate limits apply.

## Related Archive Files

- `billing-business-apis-reference.md` — comprehensive endpoint details
- `billing-endpoints.json` — machine-readable JSON format
- `billing-apis-extraction-summary.md` — extraction methodology and findings

---

*Extracted March 26, 2026 from RLM Developer Guide v260 (Spring '26)*
