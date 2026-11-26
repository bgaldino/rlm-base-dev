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
| `Invoice.SettlementLevel` of THIS invoice (when the settings cannot be read), else the junction of its application rows | `SELECT ..., SettlementLevel FROM Invoice WHERE Id = '<invoiceId>'` (no org-wide query: another invoice's level may predate a change of the setting) | `null` on a Posted invoice until something is applied, then `InvoiceLine`. Picklist: `InvoiceLine`, `Invoice`. (`CreditMemo.SettlementLevel` read `LineLevel`.) |
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
  At most one credit and one payment are created per run: the credit and
  the Payment insert follow the write rule below. Each apply is sent once,
  and a retry applies only what is not yet applied to this invoice (read
  back from the application records).
- A refused apply becomes a `SettlementError` with the API's own messages. An apply `INVALID_FIELD` on `appliedToId` is reported as a
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
- When a step that `cli step` runs fails, `error` and `failure_class` are
  written on the manifest for any failure (`SfApiError` and transport errors
  as well as `LifecycleError`) before it exits. A refusal before any step
  runs (`--config` differences, a target the recorded block cannot reach,
  `--application-level` misuse, an account mismatch) writes nothing.
- **The account.** The memo and the payment belong to the invoice's account:
  `Invoice.BillingAccountId` (an Account id), else the manifest's
  `account_id`. `cli step` resolves the account by the manifest's
  `account_id`; an `--account` name whose accounts do not include that Id
  (names are not unique), or a manifest whose `account_id` differs from the
  invoice's, is refused before any write, so a
  resume can never find-or-create a second payment under another account.
- **Level check before the payment insert.** A wrong level would first show
  at the apply, after the insert, leaving an unapplied Processed payment. So
  before inserting, the recorded level is checked against the invoice's
  `SettlementLevel` (set once something was applied, e.g. the credit) or,
  failing that, the junction of any application row on the invoice; a
  mismatch fails deterministically with nothing inserted (`--application-level`
  while the payment is not yet planned, else a new run). No evidence: the
  insert proceeds as before.
- **Errors are cleared only by a step that runs and succeeds** -- in `cli
  step` or in a batch run's retry -- in the same manifest write that records
  the stage reached, so a kill cannot leave a stale error behind. A `cli
  step` to a stage the manifest already reached runs nothing and changes
  nothing: an earlier `error` / `failure_class` stays (a payment may exist
  that was never fully applied, or a write's outcome may be unknown).
- **Refused before any step runs:** `--to-stage payment_applied` on a
  manifest whose recorded block has no `payment` (the credit stage would
  otherwise write first); `--application-level` with a `--to-stage` other
  than `payment_applied` (the level decides where the payment is applied) or
  on a manifest that already reached it. A value equal to the recorded level
  is ignored (the recorded source is kept).
- **The write rule (credit and payment).** At most one credit memo and one
  payment are created per run. The memo is tagged `<run> credit` (its
  `Description`), the payment `<run>-PAY` (`GatewayRefNumber`). Just before
  the write the harness checkpoints `credit_submitted` (with `credit_baseline`,
  the invoice's `NetCreditsApplied`) or `payment_submitted`. From then on
  neither a scenario retry nor a `cli step` resume writes again: they look
  the record up by its tag.
  - **Any HTTP 4xx** means nothing was created: the flag is cleared. A
    retryable 4xx -- status 420/429, or an `errorCode` such as
    `UNABLE_TO_LOCK_ROW`, `REQUEST_LIMIT_EXCEEDED`, `QUERY_TIMEOUT` -- fails
    the stage as transient (a retry sends the same write again, which is safe).
    Any other 4xx is a refusal: deterministic. Rerunning sends the same write
    again and will normally be refused again; to change the options, start a
    new run.
  - **Anything else** -- a 5xx, a transport failure, a 2xx without `success`
    (or a body that is not JSON) -- keeps the flag: the step waits up to 15 s
    for the record (a convenience, not a safety measure) and otherwise fails
    for good, naming the `cli step` command that keeps looking. A resume
    with the flag set and still no record fails the same way after the
    short wait (the credit is polled for `Posted` only once a memo exists);
    if the record never appears, this run cannot settle: start a new run.
  - A memo that ends in `Error`, `Canceled` or `Voided`, two memos under the
    credit tag, two payments under the payment tag (the stray's id is named
    so it can be canceled), a recorded credit memo that can no longer be
    read (deleted, or no access), or a payment applied to this invoice
    beyond its planned target fail the stage for good: this run cannot
    settle; start a new run.
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
  `Unapplied` row (measured at Line Level for an unapply: see
  [Unapply](#unapply)). The settlement stages' read-backs of this run's memo
  and payment still read every row: any `Unapplied` row or flag `Yes` fails
  the stage (an application was reversed; this run cannot settle; start a new
  run) instead of computing amounts from it.
- **The settlement block is fixed once recorded.** The settlement block is fixed once it is recorded on the manifest, which happens when the first settlement step starts (the whole block, `payment` included when the run stops at `credit_applied`, so the run can be stepped on to `payment_applied`). `cli step` then uses the recorded block only; a `--config` that differs from it is refused, naming the keys (changed options = a new run). `--config` supplies the block only when the manifest has none (a run that stopped before the settlement stages), evaluated against `--to-stage`, not the file's own `target_stage`. A config
  scenario pinning an account's new name matches the manifest when that name
  resolves to the manifest's `account_id`. The check runs before the
  "already reached" check, so a differing `--config` is never ignored; a
  manifest that reached its target never reruns a stage.
- **Settlement failures are classified from structured fields only.** Every
  settlement error is a `SettlementError` with a pinned class, so
  `failure.py`'s text matching never sees one (run and record ids hold digits:
  `...T150342Z` holds "503"; an amount may read "1503.50"). Every
  `SfApiError` leaving a settlement step is wrapped at the step boundary and
  classed from its HTTP status and the body's `errorCode` fields
  (`lifecycle.settlement_failure_class`): a retryable 4xx (above) and a 5xx
  or `-1` (timeout, exhausted retries) are transient; a refusal, and a CLI
  failure with no HTTP status (expired auth), are deterministic. An
  application level that could not be read is transient when the
  BillingSettings read failed in a way that may clear (5xx, 420/429,
  network, a CLI retrieve timeout or a retrieve error not named as a
  refusal) and this invoice shows no level
  (its `SettlementLevel`, or its application rows); nothing is recorded, so
  a retry reads again. With evidence on this invoice, that level is used
  (source `invoice_evidence`).
  A refused read is deterministic: a 4xx, or a SOAP fault whose
  `faultcode` is `INVALID_SESSION_ID`, `INSUFFICIENT_ACCESS`, `INVALID_TYPE`
  (and similar) -- Metadata SOAP faults arrive as HTTP 500, measured. Only the
  payment stage resolves the level (the credit stage reads its application
  rows back from both junctions by memo id and needs none), so both level
  errors arise there and name `cli step --to-stage payment_applied
  --application-level line|header`. A level taken from this invoice's
  evidence is recorded on the manifest but not cached in the process:
  another manifest reads the settings again.
- **`payment_applied` never advances without a payment.** A config whose
  target is `payment_applied` needs `settlement.payment`, and the stage
  refuses (not retried) a settlement block without one: with `cli step
  --config` when the manifest has no block yet, else by starting a new run.
  A configured credit or payment that rounds to 0 in the invoice currency
  (e.g. JPY 0.4, or a tiny percent) is refused the same way, naming the
  currency and its decimal places; fixed amounts are checked before the
  first write of the run (so a sub-unit payment refuses before the credit
  is sent; this holds on a run that stops at `credit_applied` too, because
  the whole block is recorded), percents where they are computed. The credit is also capped at the invoice's own `Balance` (tax included): per line, the invoice budget left is turned into its pre-tax share by the same rule as the line capacity (`Calculate` in proportion, `CopyFromInvoiceLine` less the line's tax, `Ignore` as is), rounded down, so the memo, tax included, cannot exceed what the invoice owes.
  A credit `percent` is taken of that capped amount (a warning says when the
  cap reduced its base). When the invoice owes something but none of the
  chosen lines can take even the smallest credit (tax included) within it,
  the credit is refused (nothing is sent), naming each such line and the
  least it would need. Only lines with no open balance, or an invoice whose `Balance` is 0,
  skip the stage with a warning (naming which). The payment's open amount is
  capped at the invoice's `Balance` at Line Level too (no tax split), at
  planning and at every apply.
- **The memo must apply its whole total to this invoice.** Every memo the
  harness creates is for this one invoice, so the amount applied to it
  (application rows filtered by this invoice) must equal the memo's
  `TotalAmountWithTax` exactly (both rounded to the currency's decimal places;
  even one minor unit short fails), whatever its `Balance`. Measured: all 7
  harness memos on the verification org applied exactly their total to their
  own invoice.
  The rows are polled until they add up to that total (a multi-line memo's
  rows can arrive one by one) or `poll_timeout` passes. More than the total
  fails for good. Less -- no rows or some rows -- fails naming the applied
  amount, the total and the `cli step` rerun to look again (nothing is sent
  again); only if a rerun still finds it short, start a new run: the rest
  then stayed on the memo (e.g. the platform's tax on a `Calculate` credit
  above what was applied; it would settle the account's next posted
  invoice) or was absorbed by another invoice (measured: memo
  `50gWt000001BElRIAW` has a second row on another invoice).
- A refused payment apply reports the refusal itself (nothing is read after
  it) and says the payment may be partly applied (an earlier line may have
  applied at Line Level): check its applications in the org, then apply the
  rest, or unapply them and cancel the payment, before posting more invoices
  on the account. An apply that answers 2xx without an id may have
  committed: the error names the `cli step` rerun, which re-reads what was
  applied and applies only the rest.
- A failed header read (`fetch_invoice_header`) or `CurrencyType` read raises,
  except the two answers that mean "not there": SOQL `INVALID_FIELD` with
  `No such column 'CurrencyIsoCode'` (single-currency org, read again without
  it; the message echoes the whole SOQL, so the column name alone proves
  nothing) and
  `INVALID_TYPE` on `CurrencyType` (ISO 4217 minor units of the code, not
  cached). A transient error is never recorded as "no currency" or cached.
- The BillingSettings retrieve on `cli` is bounded (`--wait 1` and a 90 s
  process timeout). A failure whose sf JSON error `name` is a measured
  refusal -- `NamedOrgNotFoundError` (unknown alias; sf 2.159, exit 2) or a
  Salesforce refusal code such as `INSUFFICIENT_ACCESS` /
  `INVALID_SESSION_ID`, optionally `sf:`-prefixed -- is a refusal, as a 4xx
  is on `requests`. `RefreshTokenAuthError` is not: sf raises it for any
  failed token refresh, network errors and OAuth 5xx included. On a timeout
  or any other failure the level comes from this invoice's evidence, else
  the stage fails transient (retry later).

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
were empty for all eight invoices (re-checked by SOQL on 2026-11-26:
0 `PaymentLineInvoice` and 0 `CreditMemoInvApplication` rows on them). The `cli step` resume without `--config` (no
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

## Unapply

Measured live on 2026-11-26 (264 scratch org, Line Level, API 68.0) on a
settled run (invoice 495.00, credit 49.50, payment 445.50, balance 0); `cli
unapply` (todo 490) is built on it.

| Call | Response |
|---|---|
| `POST /services/data/v68.0/commerce/billing/payments/{PaymentId}/paymentlines/{PaymentLineInvoiceLine Id}/actions/unapply`, body `{"comments": ...}` | `{"id": <new row>, "unappliedDate": ...}` |
| `POST /services/data/v68.0/commerce/invoicing/credit-memo-line-invoice-line/{CreditMemoLineInvoiceLine Id}/actions/unapply`, body `{}` | `{"creditMemoLineInvoiceLineId": <new row>, "errors": [], "success": true}` |

- **Synchronous and whole.** The rows and rollups had changed when the call
  returned. Neither body takes an amount: an unapply reverses the whole row.
- **Rows.** The original row stays `Type` Applied with `Amount` and
  `ImpactAmount` unchanged; `UnappliedStatus` goes No -> Yes and
  `UnappliedDateTime` is set (the payment row's `AppliedImpactAmount` goes to
  0). A new row is added: `Type` Unapplied, a positive `Amount` equal to the
  original's, on the same `InvoiceLineId` and `PaymentId` / `CreditMemoLineId`,
  `UnappliedStatus` NA, `RelatedPaymentLineInvcLineId` /
  `RelatedCrMemoLineInvcLineId` naming the original, positive `ImpactAmount`.
  Both Related fields are filterable: a rerun found the existing Unapplied rows
  by them.
- **Balances.** After the payment's unapply: invoice and line `Balance` 445.50,
  `NetPaymentsApplied` 0; payment `Balance` 445.50, `NetApplied` 0. After the
  credit's too: invoice `Balance` 495.00, both nets 0, credit memo `Balance`
  49.50, and `Invoice.SettlementLevel` back to null (it was InvoiceLine).
- **Twice.** A second unapply of the same row is refused with HTTP 400
  `INVALID_FIELD_FOR_INSERT_UPDATE` and writes nothing.
- **The next invoice absorbs it.** The payment and memo then carry open
  balances, and posting the account's next invoice applied both to it (the
  same rule as above): that run's credit and payment steps found no open
  balance and wrote nothing. `cli verify` on that invoice with the reversed
  payment (run DEMO-20261126T040031Z) passed: the payment's pair nets to 0, its
  new Applied row on the next invoice is 445.50, and `NetApplied` 445.50,
  `Balance` 0.
- Not measured: header-level unapply (`credit-memo-inv-applications/.../unapply`,
  payment header rows), reapplying by hand after an unapply, voiding a credit
  memo.
- **Either order.** Unapplying the credit while the payment stays applied
  (`--only credit`, run DEMO-20261126T041707Z) left invoice and line `Balance`
  49.50 = 495.00 − 445.50 with the payment untouched; the payment's unapply
  after it restored 495.00, as in the first order.

`cli unapply --org <sf-alias> --manifest <run> [--only payment|credit]`
reverses the run's own recorded line-level applications, the payment's first.
It takes only a finished settlement: no error on the manifest, and
`payment_applied` reached or a block with no payment, so every application the
run made is recorded and no `cli step` can advance it afterwards. It reads each
row first and unapplies only a line-level Applied row (a run that stopped at
`credit_applied` records no application level; its rows decide). One already
unapplied is not sent again (the platform would refuse it); its Unapplied row
is looked up instead, and a flagged row with none fails. The new rows go in the
manifest's `unapplied_row_ids`. Exit 0 when every selected application is
unapplied and recorded; 1 when one could not be (a failed read or write on one
row included) or nothing was recorded to unapply; 2 when the manifest cannot be
read, the settlement is not finished, the run is recorded at Header Level, or
the org cannot be read before any unapply. `cli verify` then checks the pair (see `verify.py`).

## Cleanup

Payments, credit memos and their application records were not deleted, and no
delete, void or cancel path was probed. A Payment's `Status` picklist includes
`Canceled`; voiding credit memos is documented but not exercised here.
Unapplying is measured ([Unapply](#unapply)). Treat settlement records like Posted
invoices: leftovers. Tracked in [`followups.md`](followups.md#billing-settlement).
