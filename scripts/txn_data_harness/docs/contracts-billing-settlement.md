# Billing Settlement (credit_applied / payment_applied) — Contracts

> ✅ VERIFIED LIVE at **Line Level** (2026-11-25, `rlm-base__apexcov-ac1125-r1` —
> Release 264 scratch org, API v68.0, account Infinitech, Credit, Payment and
> Refund Application Level = Line Level). Every request below was sent at
> `v68.0`.
>
> ⚠️ **Header Level is NOT live-verified.** The verification org is at Line
> Level and its level was not changed. The Header Level branch (payment applied
> to the Invoice id, application rows read from `PaymentLineInvoice` /
> `CreditMemoInvApplication`) is implemented from the 264 developer guide and
> Help, and tested offline only. So is the mapping of the BillingSettings
> value `true` to Header Level. See [`followups.md`](followups.md#billing-settlement).

The settlement stages run after `invoice_posted` on every kind
(`sales_txn_quote`, `sales_txn_order`, `invoice_ingestion`):

```text
... → invoice_posted → credit_applied → payment_applied
```

`credit_applied` credits the Posted invoice with one credit memo;
`payment_applied` creates one processed payment and applies it. Each is driven
by the scenario's `settlement:` block and is a no-op (it only advances
`reached_stage`) when its own block is absent. Code: `lifecycle.py` → *Step 7 —
Settlement*; `steps.py` → `run_credit`, `run_payment`.

## Application level — read once per org

| Source | How | Observed |
| ------ | --- | -------- |
| BillingSettings (primary) | Metadata SOAP `readMetadata`, type `BillingSettings`, fullName `Billing`, `POST /services/Soap/m/68.0` with the session id. No REST equivalent (BillingSettings is not a Tooling sObject). | `enableTransactionsApplicationToInvoices` = `false` on this Line Level org (Line Level confirmed by the payment-apply error below). |
| `Invoice.SettlementLevel` (fallback) | `SELECT SettlementLevel FROM Invoice WHERE SettlementLevel != null ORDER BY LastModifiedDate DESC LIMIT 1` | `null` on a Posted invoice until something is applied, then `InvoiceLine`. Picklist: `InvoiceLine`, `Invoice`. (`CreditMemo.SettlementLevel` read `LineLevel`.) |
| `settlement.application_level: line\|header` | Pinned in the scenario; skips the read. | — |

The harness maps `false → line`, `true → header`. The `true` half is inferred
from the developer guide (the setting "applies balances of credit memos and
payments to invoices or balances of credit memo lines and payments lines to
invoice lines") and the Help setup page (a Line Level / Header Level choice);
it was not read on a Header Level org. The result is cached per instance URL
for the process and recorded on the manifest (`application_level`,
`application_level_source`); a resumed manifest keeps its recorded level.

Other BillingSettings values on the verification org that shape settlement:

```xml
<enablePaymentApplicationToPostedInvoices>true</enablePaymentApplicationToPostedInvoices>
<enableCrMemoApplicationToPostedInvoices>true</enableCrMemoApplicationToPostedInvoices>
<ruleBasedCrAndPymtAppln>{"first":"Payments","rules":["EA","OI","HI"]}</ruleBasedCrAndPymtAppln>
```

## Order matters: the platform applies open balances at post

| Observation | Evidence |
| ----------- | -------- |
| **Posting a Draft invoice through the post action applied the account's unapplied payment and credit balances to it.** A payment with 40 unapplied and a credit memo with 10 unapplied were both applied to the next quote-path invoice at post, before the settlement stages ran. | Run `DEMO-20261125T142256Z`, invoice `3ttWt000002lgVhIAI`: `PaymentLineInvoiceLine` `1AlWt000000fk0TKAQ` (40, payment `0aQWt000000XOefMAG`) and `CreditMemoLineInvoiceLine` `4sGWt0000000tqvMAA` (10, memo `50gWt000001BElRIAW`), both created 14:23:46Z, the post time. The manifest's `settlement_baseline` recorded both. |
| Same effect reported earlier on this org: a Processed payment created before a Draft invoice was posted was applied to it at post (invoice `NetPaymentsApplied` 1000, payment `Balance` 0). | Payment `0aQWt000000XOLJMA4`, invoice `3ttWt000002lg4HIAQ`, `PaymentLineInvoiceLine` `1AlWt000000fjafKAA`. |
| **Ingesting an invoice directly as Posted did not apply open balances.** | Run `DEMO-20261125T142132Z` (40 + 10 available) and runs `DEMO-20261125T142843Z`, `DEMO-20261125T143052Z` (99 available): baseline `net_payments_applied` and `net_credits_applied` both 0. |
| **A payment created after the invoice posts was not applied on its own** within 60 s, with several open Posted invoices on the account. | Payment `0aQWt000000XOefMAG`: `Balance` 100, no application rows at 0–60 s. |

How the harness designs around it:

1. The payment is created **in `payment_applied`, after the invoice is Posted**,
   and applied explicitly — never created ahead of the post.
2. Before applying anything, the first settlement stage records
   `settlement_baseline` (invoice `Balance`, `NetCreditsApplied`,
   `NetPaymentsApplied`, and the ids of any application rows already there).
   Non-zero values were applied by the platform; the stage adds a warning.
3. Amounts (`exact`, `percent`) are computed against the open balance **read
   when the stage runs**, i.e. after whatever the platform applied.
4. Credits are capped so the memo is fully applied (an over-balance memo keeps
   an unapplied balance, measured below), and an `over` payment warns, because
   either leftover will settle the account's next invoice posted through the
   post action.
5. What was applied is read back from the application records **on this
   invoice**, not assumed: an over-payment's rest applied to another invoice is
   not counted (measured: the 99 left on `0aQWt000000XOtBMAW` was applied to
   the next posted invoice, `3ttWt000002lgx7IAA`, row `1AlWt000000fkDNKAY`).
6. **Serial runs per account.** A payment is open between its create and apply
   calls, so a sibling scenario posting an invoice for the same account in that
   gap would absorb it. `cli run` refuses `--concurrency > 1` when a batch has a
   settlement target on an account with more than one transaction (`cli plan`
   warns). Separate harness processes against one account are not guarded.

## Credit — `POST /commerce/invoicing/invoices/{invoiceId}/actions/credit`

Async. Measured request and response (invoice `3ttWt000002lgQrIAI`):

```jsonc
POST /services/data/v68.0/commerce/invoicing/invoices/3ttWt000002lgQrIAI/actions/credit
{
  "type": "POSTED",
  "taxStrategy": "CopyFromInvoiceLine",
  "effectiveDate": "2026-11-25",
  "description": "PROBE-275 credit",
  "invoiceLines": [{ "invoiceLineId": "5TVWt000002HH1hOAG", "amountToCredit": 40 }]
}
→ 201 (0.59 s)
{ "errors": [], "referenceLineErrorResults": null, "referenceLineType": null,
  "requestIdentifier": "7ce2a890-e55f-45eb-bdb9-f165285ada32",
  "statusURL": "", "success": true }
```

- No tracker (`statusURL` empty). The `CreditMemo` row (`ReferenceEntityId` =
  invoice, `Description` from the body) exists at once in `Pending`, then reads
  `Posted` with the application done about 3 s later.
- Line Level read-back: one `CreditMemoLineInvoiceLine` (`Type` Applied,
  `InvoiceLineId`, `CreditMemoLineId`); no `CreditMemoInvApplication`. Invoice
  `Balance` 250 → 210, `SettlementLevel` `InvoiceLine`, `SettlementStatus`
  `Partially Settled`; line `Balance` 100 → 60.
- The harness sends `description: "<run_id> credit"` and finds the memo by
  `ReferenceEntityId` + `Description` (the action has no idempotency key; a
  retry after an accepted POST polls instead of POSTing again).

### Tax strategy (per line; the top-level value is required)

| `taxStrategy` | Line | `amountToCredit` | Memo `TotalAmount` / `TotalTaxAmount` / `TotalAmountWithTax` |
| ------------- | ---- | ---------------- | ------------------------------------------------------------ |
| `CopyFromInvoiceLine` | taxed (charge 450, tax 45) | 45 | 45 / **45** / 90 — the line's **whole** tax was copied onto a partial credit (run `DEMO-20261125T142256Z`, memo `50gWt000001BEofIAG`) |
| `Calculate` | same taxed line | 10 | 10 / 1 / 11 — tax in proportion (memo `50gWt000001BErtIAG`) |
| `Calculate` (per line, top-level also `Calculate`) | taxed | 45 | 45 / 4.5 / 49.5 (run `DEMO-20261125T142717Z`, memo `50gWt000001BEv7IAG`) |
| `Ignore` | same taxed line | 10 | 10 / 0 / 10 (memo `50gWt000001BEqHIAW`) |
| `CopyFromInvoiceLine` | untaxed ingested line | 20 | 20 / 0 / 20 (run `DEMO-20261125T142132Z`, memo `50gWt000001BEn3IAG`) |
| `Ignore` (per line) | untaxed ingested line | 30 | 30 / 0 / 30 (runs `DEMO-20261125T142843Z`, `DEMO-20261125T143052Z`) |
| `Calculate` | untaxed ingested line | 5 | **refused** (below) |

The harness default `tax_strategy: auto` sends `Calculate` on lines with
`TaxAmount > 0` and `Ignore` on lines without. Each line carries its own
`taxStrategy`; the top-level value is the first line's.

### Credit errors (all synchronous, HTTP 400, no memo created)

| Case | Response |
| ---- | -------- |
| `amountToCredit` 200 > line charge 100 | `{"enhancedErrorType":"RecordError","message":"Can't complete request because one or more invoice lines contained an invalid value.","output":{"errors":[],"referenceLineErrorResults":[{"errors":[{"errorCode":"INVALID_API_INPUT","message":"Couldn't credit invoice line 5TVWt000002HH1hOAG because the credit line amount exceeds the invoice line amount"}],"referenceLineId":"5TVWt000002HH1hOAG"}],"referenceLineType":"Invoice Line","requestIdentifier":null,"statusURL":"","success":false}}` |
| `invoiceLines: []` | `{"enhancedErrorType":"RecordError","message":"Provide at least one invoice line","output":{"errors":[{"errorCode":"INVALID_API_INPUT","message":"Provide at least one invoice line"}],...,"success":false}}` |
| `Calculate` on a line with no tax line | `{"enhancedErrorType":"RecordError","message":"Couldn't create credit memo.","output":{"errors":[{"errorCode":"INVALID_API_INPUT","message":"To calculate tax, the invoice line must have a tax line."}],...,"success":false}}` |

(Apostrophes arrive HTML-escaped as `&#39;` in the raw body.)

### Over the balance but within the charge: accepted, leaves a credit balance

`amountToCredit` 70 on a line with charge 100 and balance 60 was **accepted**:
memo `50gWt000001BElRIAW` posted at 70, applied 60, and kept `Balance` 10. That
10 was later applied by the platform to the next invoice posted through the post
action (above). The harness caps each line's credit so the memo, tax included,
fits the line's open balance: `Ignore` → balance; `Calculate` → balance ×
charge / line amount, rounded down to the currency's smallest unit; `CopyFromInvoiceLine` → balance
less the line's tax; every case also capped at the charge amount.

## Payment — create, then `POST /commerce/billing/payments/{paymentId}/actions/apply`

### Create (sObject, synchronous)

```jsonc
POST /services/data/v68.0/sobjects/Payment
{
  "AccountId": "001Wt00001rcnYbIAI",
  "Amount": 230.0,
  "Status": "Processed",
  "Type": "Sale",
  "ProcessingMode": "External",
  "GatewayRefNumber": "<run_id>-PAY",
  "Comments": "Transaction Data Harness payment (<run_id>)",
  "EffectiveDate": "2026-11-25T00:00:00.000Z",
  "CurrencyIsoCode": "USD"          // the invoice's currency; omitted on single-currency orgs
}
→ { "id": "0aQWt000000XOl7MAG", "success": true, "errors": [] }
```

No gateway is involved. `GatewayRefNumber` is the retry key (`Comments` is a
textarea and cannot be filtered). The org is multi-currency; the harness copies
`Invoice.CurrencyIsoCode` onto the payment. Only USD was exercised.

### Apply (synchronous)

```jsonc
POST /services/data/v68.0/commerce/billing/payments/0aQWt000000XOefMAG/actions/apply
{ "appliedToId": "5TVWt000002HH1iOAG", "amount": 60,
  "comments": "PROBE-275 apply", "effectiveDate": "2026-11-25T00:00:00.000Z" }
→ 201 (1.25 s)
{ "appliedDate": "2026-11-25T14:14:38.273Z", "id": "1AlWt000000fjvdKAA" }
```

- The returned `id` is the `PaymentLineInvoiceLine` (`Type` Applied,
  `PaymentBalance` 40, `InvoiceLineBalance` 90). No `PaymentLineInvoice` row.
  Payment `Balance` 100 → 40, `NetApplied` 60.
- One call per line at Line Level; the harness spreads the amount over the
  chosen lines in order, each up to its balance.
- At Header Level the harness sends the Invoice id as `appliedToId` (not
  live-verified).

### Apply errors (HTTP 400, synchronous)

| Case | Response |
| ---- | -------- |
| `appliedToId` = Invoice id at Line Level | `[{"errorCode":"INVALID_FIELD","message":"Specify an InvoiceLineId as the appliedToId because the Credit Application Level is Invoice Line."}]` |
| `amount` 160 > line balance 150 | `[{"errorCode":"FIELD_INTEGRITY_EXCEPTION","message":"Enter an amount that’s less than or equal to the balance of the related invoice line."}]` |
| `amount` 5 on a line with balance 0 | same as above |
| `amount` 150 > payment balance 100 | `[{"errorCode":"FIELD_INTEGRITY_EXCEPTION","message":"Enter an amount that’s less than or equal to the balance of the related payment."}]` |

## Writes, retries and errors

- The credit POST, the Payment insert and each apply are sent **once** per
  call (`SfRestClient.post(..., retry=False)`; `sf api request rest` does not
  retry POST either): none has an idempotency key, so a transport-level retry
  after a 5xx the server had committed would credit, pay or apply twice.
  Recovery is by read-back: the payment is found by its `GatewayRefNumber`
  tag, and a retry applies only what is not yet applied to this invoice. The
  credit follows the stricter rule below.
- A 4xx from the credit action or the apply becomes a `LifecycleError` with the
  API's own messages. An apply `INVALID_FIELD` on `appliedToId` is reported as a
  likely wrong application level: the payment is then Processed and unapplied
  (and may be absorbed by the account's next posted invoice). The level cannot
  change once the payment is planned (amount and apply target are fixed
  before the first apply): `cli step --application-level` is refused then;
  start a new run with `settlement.application_level` pinned.
  `--application-level` corrects the level only before the payment is
  planned, and is the remedy when the level cannot be read at all.
- The 4xx / 5xx split holds on both transports. `--transport cli` runs
  `sf api request rest --include`, whose output starts with the HTTP status
  line and headers, then the body with no blank line in between (measured
  with sf 2.159 on 200, 400 and 404); an empty body (204) prints as one blank
  line. `SfApiError.status` is the HTTP status there too. A CLI failure that
  never reached the API (no status line) keeps the CLI exit code and counts
  as an unknown outcome, like a 5xx.
- BillingSettings (the application level) is read through the client's
  transport: Metadata SOAP `readMetadata` on `requests` (SOAP takes the
  session only inside the envelope; a bearer header is refused with
  `INVALID_SESSION_ID`, measured), and `sf project retrieve start --metadata
  Settings:Billing` on `cli`, so nothing from our process carries a token
  there.
- `cli step` writes `error` on the manifest for any failure (`SfApiError` and
  transport errors as well as `LifecycleError`) before it exits.
- **The account.** The memo and the payment belong to the invoice's account:
  `Invoice.BillingAccountId` (an Account id), else the manifest's
  `account_id`. `cli step` resolves the account by the manifest's
  `account_id`; an `--account` resolving to another Id, or a manifest whose
  `account_id` differs from the invoice's, is refused before any write, so a
  resume can never find-or-create a second payment under another account.
- **One credit per run, never re-sent automatically.** The credit memo is
  tagged `<run> credit` (its `Description`). Just before the one POST the
  harness checkpoints `credit_submitted` and `credit_baseline` (the invoice's
  `NetCreditsApplied`). From then on neither a scenario retry nor a `cli
  step` resume POSTs again: they poll for the memo by the tag. A confirmed
  refusal (HTTP 4xx: nothing was created) clears `credit_submitted` and fails
  the stage: the options are fixed, so start a new run. A 2xx without
  `success: true` (or a body that is not JSON), a 5xx or a transport failure
  counts as accepted: the step waits up to 15 s for the memo (a convenience,
  not a safety measure) and otherwise fails naming the `cli step` command
  that keeps waiting. A memo that ends in `Error`, `Canceled` or `Voided`, or
  two memos under the tag, fails the stage for good: this run cannot settle;
  start a new run. Recovering a failed credit needs a new run.
- **Double-credit check.** After the credit stage the invoice's
  `NetCreditsApplied` gain since `credit_baseline` must equal what the run's
  memo applied; any difference (another credit, a reversal) fails the stage
  rather than warning. A credit the platform applied before the POST is not
  counted. Manifests without `credit_baseline` compare against
  `settlement_baseline.net_credits_applied`.
- **Reversed applications.** Unapplying or voiding keeps the original
  `Applied` row, flags it (`UnappliedStatus` on `CreditMemoLineInvoiceLine` /
  `PaymentLineInvoiceLine`, `HasBeenUnapplied` on `CreditMemoInvApplication` /
  `PaymentLineInvoice` = `Yes`; field names from describe on 264) and adds an
  `Unapplied` row. Reversals are not measured, so the read-backs of this
  run's memo and payment read every row: any `Unapplied` row or flag `Yes`
  fails the stage (an application was reversed outside the harness; this run
  cannot settle; start a new run) instead of computing amounts from it.
- **The settlement block is fixed once recorded.** The settlement block is fixed once it is recorded on the manifest, which happens when the first settlement step starts (only the parts the run's target reaches: no `payment` for `credit_applied`). `cli step` then uses the recorded block only; a `--config` that differs from it is refused, naming the keys (changed options = a new run). `--config` supplies the block only when the manifest has none (a run that stopped before the settlement stages), evaluated against `--to-stage`, not the file's own `target_stage`. A config
  scenario pinning an account's new name matches the manifest when that name
  resolves to the manifest's `account_id`. The check runs before the
  "already reached" check, so a differing `--config` is never ignored; a
  manifest that reached its target never reruns a stage.
- **Settlement failures are classified by cause, not by text.** Every
  settlement error is a `SettlementError`, pinned `deterministic` (its text
  holds run and record ids whose digits, `...T150342Z` holds "503", would
  match the transient patterns), and a raw 4xx `SfApiError` from a settlement
  query or write is wrapped into one at the step boundary -- except 420/429
  and 4xx bodies `failure.py` reads as transient (`UNABLE_TO_LOCK_ROW`,
  `QUERY_TIMEOUT`, `REQUEST_LIMIT_EXCEEDED`, ...), which are not refusals
  (`lifecycle.is_api_refusal` uses failure.py's own lists). Also transient: a
  5xx / transport `SfApiError`, and an application level that could not be
  read because the BillingSettings read failed in a way that may clear (5xx,
  420/429, network, CLI retrieve failure or timeout) with no invoice
  evidence. A refused read is deterministic: a 4xx, or a SOAP fault whose
  `faultcode` is `INVALID_SESSION_ID`, `INSUFFICIENT_ACCESS`, `INVALID_TYPE`
  (and similar) -- Metadata SOAP faults arrive as HTTP 500, measured. Both level
  errors name `cli step --application-level line|header`. A successful `cli
  step` clears `error` and `failure_class`, as does a `cli step` to a stage
  the manifest already reached.
- **`payment_applied` never advances without a payment.** A config whose
  target is `payment_applied` needs `settlement.payment`, and the stage
  refuses (not retried) a settlement block without one: with `cli step
  --config` when the manifest has no block yet, else by starting a new run.
- A failed header read (`fetch_invoice_header`) or `CurrencyType` read raises,
  except the two answers that mean "not there": SOQL `INVALID_FIELD` with
  `No such column 'CurrencyIsoCode'` (single-currency org, read again without
  it; the message echoes the whole SOQL, so the column name alone proves
  nothing) and
  `INVALID_TYPE` on `CurrencyType` (ISO 4217 minor units of the code, not
  cached). A transient error is never recorded as "no currency" or cached.
- The BillingSettings retrieve on `cli` is bounded (`--wait 1` and a 90 s
  process timeout); on a timeout or failure the level comes from the
  invoice-evidence probe, with the reason logged.

## Currency precision

Every amount the harness computes or sends is rounded to
`CurrencyType.DecimalPlaces` of the invoice currency: percent shares, per-line
credit caps and allocations, `Payment.Amount`, each apply `amount`, and the
balances they are compared with. The places are recorded in
`settlement_baseline.decimal_places`. A single-currency org's invoices have
no `CurrencyIsoCode` and the org no `CurrencyType` to read, so its places come
from `Organization.DefaultCurrencyIsoCode` (a field single-currency orgs have;
a multi-currency org answers `INVALID_FIELD`, measured) through ISO 4217 minor
units (source: the ISO 4217 list maintained by SIX): 0 for BIF, CLP, DJF, GNF,
ISK, JPY, KMF, KRW, PYG, RWF, UGX, UYI, VND, VUV, XAF, XOF, XPF; 3 for BHD,
IQD, JOD, KWD, LYD, OMR, TND; 2 otherwise. Config `amount:` values are not
pre-rounded, so a 3-place currency keeps `10.005`. Read on the verification
org: USD, EUR, GBP, CAD, AUD, CHF = 2, **JPY = 0**. Only USD invoices were
settled live; JPY and 3-place currencies (KWD) are covered offline only.

## Read-back queries the harness uses

```sql
-- credit (the run's memo id), on this invoice only; every row is read and any
-- Type 'Unapplied' row or UnappliedStatus / HasBeenUnapplied = 'Yes' fails
SELECT Id, Amount, InvoiceLineId, Type, UnappliedStatus FROM CreditMemoLineInvoiceLine
 WHERE CreditMemoLine.CreditMemoId IN (...)
   AND InvoiceLine.InvoiceId = '<invoiceId>'                            -- Line Level
SELECT Id, Amount, InvoiceId, Type, HasBeenUnapplied FROM CreditMemoInvApplication
 WHERE CreditMemoId IN (...) AND InvoiceId = '<invoiceId>'                 -- Header Level
-- payment, on this invoice only (same reversal rule)
SELECT Id, Amount, InvoiceLineId, Type, UnappliedStatus FROM PaymentLineInvoiceLine
 WHERE PaymentId IN (...) AND InvoiceLine.InvoiceId = '<invoiceId>'     -- Line Level
SELECT Id, Amount, InvoiceId, Type, HasBeenUnapplied FROM PaymentLineInvoice
 WHERE PaymentId IN (...) AND InvoiceId = '<invoiceId>'                    -- Header Level
-- invoice
SELECT Balance, NetCreditsApplied, NetPaymentsApplied, SettlementStatus, SettlementLevel
  FROM Invoice WHERE Id = '<invoiceId>'
```

Both junctions are read whatever the level; rows in the other level's junction
are recorded and raise a warning (they would mean the level read was wrong).

## Live runs (2026-11-25, Line Level)

Each ran `cli plan` first, then `cli run --concurrency 1`, count 1. Balances
are from SOQL on the invoice, payment and credit memo by manifest id.

| Run | Kind | Settlement | Invoice (total) | Credit memo (applied) | Payment (amount / applied / mode) | Invoice balance after |
| --- | ---- | ---------- | --------------- | --------------------- | --------------------------------- | --------------------- |
| `DEMO-20261125T142132Z` | `invoice_ingestion` | credit 20% of line 0 (`CopyFromInvoiceLine`, before `auto`), payment exact | `3ttWt000002lgU5IAI` (250) | `50gWt000001BEn3IAG` (20) | `0aQWt000000XOl7MAG` 230 / 230 / exact (2 line applications) | 0, Settled |
| `DEMO-20261125T142256Z` | `sales_txn_quote` | credit 45 (`CopyFromInvoiceLine`), payment 100 | `3ttWt000002lgVhIAI` (495) | `50gWt000001BEofIAG` (90: 45 + 45 copied tax) | `0aQWt000000XOmjMAG` 100 / 100 / partial | 255 (40 + 10 applied by the platform at post) |
| `DEMO-20261125T142717Z` | `sales_txn_quote` | credit 10% (`auto` → `Calculate`), payment exact | `3ttWt000002lgXJIAY` (495) | `50gWt000001BEv7IAG` (49.5) | `0aQWt000000XOpxMAG` 445.5 / 445.5 / exact | 0, Settled |
| `DEMO-20261125T142843Z` | `invoice_ingestion` | credit 30 on line "Partial Line B" (`auto` → `Ignore`), payment 50% | `3ttWt000002lgYvIAI` (300) | `50gWt000001BEwjIAG` (30) | `0aQWt000000XOrZMAW` 135 / 135 / partial (2 line applications) | 135 |
| `DEMO-20261125T142934Z` | `sales_txn_order` | payment 120% | `3ttWt000002lgaXIAQ` (495) | — | `0aQWt000000XOtBMAW` 594 / 495 / over (payment keeps 99) | 0, Settled |
| `DEMO-20261125T143052Z` | `invoice_ingestion` | run to `invoice_posted`, then `cli step --to-stage payment_applied --config ...` (credit 30 on "Partial Line B", payment 50%) | `3ttWt000002lgc9IAA` (300) | `50gWt000001BEyLIAW` (30) | `0aQWt000000XOunMAG` 135 / 135 / partial | 135 |
| `DEMO-20261125T145514Z-001` | `sales_txn_quote` | `scenarios/sales_txn_quote/17-settlement.yaml` #1: credit 10% (`auto`), payment exact; `--concurrency 1` | `3ttWt000002lgx7IAA` (495) | `50gWt000001BFBFIA4` (39.6: 36 + 3.6 tax) | `0aQWt000000XPPRMA4` 356.4 / 356.4 / exact | 0, Settled (99 applied by the platform at post) |
| `DEMO-20261125T145514Z-002` | `sales_txn_quote` | same file #2: credit 50, payment 300 | `3ttWt000002lgyjIAA` (990) | `50gWt000001BFCrIAO` (55: 50 + 5 tax) | `0aQWt000000XPR3MAO` 300 / 300 / partial | 635 |

Every application row landed in `CreditMemoLineInvoiceLine` /
`PaymentLineInvoiceLine`; `PaymentLineInvoice` and `CreditMemoInvApplication`
were empty for all six invoices. The `cli step` resume without `--config` (no
settlement on the manifest) failed before any write, as designed.

Probe records left on the org (not from a harness run): invoice
`3ttWt000002lgQrIAI` (ingested Posted, balance 90 after probes), memos
`50gWt000001BEiDIAW`, `50gWt000001BElRIAW`, payment `0aQWt000000XOefMAG`;
probe memos `50gWt000001BEqHIAW`, `50gWt000001BErtIAG` on `3ttWt000002lgVhIAI`
(its balance is 234 after them). Payment `0aQWt000000XOtBMAW` still holds 99
unapplied after its run; the next Infinitech post (`DEMO-20261125T145514Z-001`)
absorbed it, as the baseline of that run shows. The same file run at the
default `--concurrency 4` was refused before any write (and `cli plan`
warned).

## Cleanup

Payments, credit memos and their application records were not deleted and no
cleanup path was probed. A Payment's `Status` picklist includes `Canceled`;
unapplying (`.../paymentlines/{id}/actions/unapply`) and voiding credit memos
are documented but not exercised here. Treat settlement records like Posted
invoices: leftovers. Tracked in [`followups.md`](followups.md#billing-settlement).
