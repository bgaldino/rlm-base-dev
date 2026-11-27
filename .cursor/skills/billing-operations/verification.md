# Billing Operations — Verifying Balances and Applications

Read this when checking, without writing anything, that invoices, invoice lines and
payments agree with the payments and credits applied to them. Parent:
[SKILL.md](SKILL.md). What the application levels do and how they were measured is in
[payments-and-credits.md](payments-and-credits.md) → *Measured: Line Level application*;
this page does not repeat it.

## The verifier

`cli verify` in the Transaction Data Harness reads records by id and runs the checks
below. It only runs SOQL queries [Repo: scripts/txn_data_harness/verify.py].

```bash
# ids from a harness manifest (repeat --manifest for several; --latest reads only the newest)
python -m scripts.txn_data_harness.cli verify --org <sf-alias> --manifest <run-id-or-path>
# ids by hand; add --payment-ids for a payment with no applications
python -m scripts.txn_data_harness.cli verify --org <sf-alias> \
  --invoice-ids <invoiceId>,<invoiceId> --payment-ids <paymentId> --json
# force the level, for example as a negative control
python -m scripts.txn_data_harness.cli verify --org <sf-alias> \
  --invoice-ids <invoiceId> --expect-level header
```

Exit codes:

- **0**: no check failed. A skipped check is not a failure, so a run where every
  balance check skipped also exits 0: read the counts. The last text line is
  `RESULT: pass (N checked, M skipped)`, or `RESULT: pass (no balances checked; M
  skipped)`; `--json` carries `checked` and `skipped`. They count balance-check
  results: one per invoice for `invoice_balance`, one per line when
  `invoice_line_balance` runs and one per invoice when it skips (or when it fails
  because no lines could be read, counted as checked), and one per payment for
  `payment_balance`.
- **1**: at least one check failed. `--json` prints every result with its check name,
  subject id, status and detail.
- **2**: no report, because the input or a Salesforce request was bad: a malformed,
  unknown or unreadable id, a missing manifest, one that is not UTF-8 JSON or not a JSON
  object, or an id value in it that is not a string or a list of strings; a refused
  query or login, a failed connection (including the `--api-version latest` lookup), or
  an `sf` CLI that is not on `PATH`, or any other unexpected error (named with its
  type). An `ERROR:` line goes to stderr; with `--json`, stdout gets
  `{"ok": false, "error": "..."}`. A usage error (no `--org`, an unknown
  `--expect-level` value, an unrecognized or extra argument) is reported by argparse
  instead: usage text and the error on stderr, exit 2, and, when the command line
  contains the token `--json`, one `{"ok": false, "error": "usage: ..."}` object on
  stdout. `verify` refuses abbreviated options: `--jso` is an unrecognized argument.

Ids may be 15 or 18 characters; they are converted to the 18-character form before
querying. As in Salesforce, the suffix of an 18-character id restores the case of its
first 15 characters, so `3TT000000000001AAA` reads as `3tt000000000001AAA`; an id whose
suffix fits no casing is refused. If stdout is closed early (`verify --json | head -1`),
the output stops quietly and the verify process still exits with the checks' result; a
shell pipeline reports the last command's status, so read verify's with
`set -o pipefail` or `PIPESTATUS` (`pipestatus` in zsh). From a manifest, `verify` reads `invoice_id` or `invoice_ids`, and `payment_id` or
`payment_ids` when the manifest has them (the `payment_applied` settlement stage writes
`payment_ids`; earlier stages write none). A manifest with no ids is only a warning when another
source supplies ids.
`--latest` reads only the newest manifest, so after a batch of several scenarios pass
each manifest with `--manifest` (repeatable) or the ids with `--invoice-ids`.
Payments are found through the invoices' application rows, or passed with
`--payment-ids` (for example one with no applications). `--payment-ids` alone checks just
those payments.

## Checks

Amounts compare exactly as decimals, with no rounding, so a currency with zero or three
decimal places is checked as it is stored. The net of a set of application rows is the
sum of the Applied amounts less the Unapplied amounts. A null `Balance` fails wherever the check runs.

**Only what was measured is checked.** The balance checks run only on records inside
one allow-list, the cases measured on a Line Level 264 org. Anything outside it is
skipped with the first cause found; nothing is guessed.

| Record | Measured when |
| ------ | ------------- |
| Application row | `Type` Applied, and no unapplied flag (`UnappliedStatus`, `HasBeenUnapplied`) is `Yes`. Both flags are picklists of No, Yes and NA [Measured: 2026-11-25, 264, scratch org, API 68.0]. Or, at Line Level, an unapplied pair: the Applied row flagged `UnappliedStatus` Yes and the one `Type` Unapplied row (its own `UnappliedStatus` NA) whose `RelatedPaymentLineInvcLineId` / `RelatedCrMemoLineInvcLineId` names it, on the same invoice line and payment or credit memo line, with the same `Amount` [Measured: 2026-11-26, 264, scratch org, API 68.0]. Rows net as Applied minus Unapplied, so a pair nets to zero, as the rollups did. |
| Invoice line | `Type` Charge (Tax, Adjustment, null or any other value is not), and `ConvertedNegAmount`, `ChargeConvertedNegAmount` and `AdjustmentAmount` null or zero. |
| Invoice | `Status` Posted; no header evidence (no header application rows, `SettlementLevel` not `Invoice`); no `WriteOffStatus`; `TotalConvertedNegAmount`, `WriteOffTotalChargeAmount`, `WriteOffTotalTaxAmount`, `TotalAdjustmentAmount` and `TotalTaxesCapturedAtHeader` null or zero; every line and every application row measured. |
| Payment | `Status` Processed with application rows, or Canceled with none; no header-level application rows; `NetRefundApplied` and `NetPaymentCreditApplied` null or zero; every application row measured. |
| Credit memo | `Status` Posted (Draft, Pending, Void In Progress, Canceled, Error and Voided are not). Every memo on the measured org was Posted. Read by the ids on the credit application rows (through `CreditMemoLine` for line rows). |

An invoice and a payment or credit memo joined by an application row, both read, are
measured only together: when either is outside the allow-list, the other is skipped too,
and this repeats until nothing changes, so a payment or memo applied to two invoices
links them. At every hop the skip names the neighbour and the origin record with its
cause, for example `linked payment 0aQ...; origin invoice 3tt...: Status Draft; ...`.
Invoices and payments outside the set are not read, so they do not propagate. Header
Level was never measured, so every record with header evidence (header rows or
`SettlementLevel` `Invoice`) skips its balance checks; an unpaid invoice with no
evidence still gets `invoice_balance`, as the table says, and `application_level`
still runs.

| Check | Passes when |
| ----- | ----------- |
| `application_level` | The invoice has no application rows of the other level, and its `SettlementLevel` does not name the other level. Line rows: `PaymentLineInvoiceLine`, `CreditMemoLineInvoiceLine`. Header rows: `PaymentLineInvoice`, `CreditMemoInvApplication`. Skipped for an invoice with neither application rows nor a `SettlementLevel`, whether the level was detected or forced with `--expect-level`. Not gated by the allow-list. |
| `invoice_balance` | On a measured invoice: `Balance = TotalAmountWithTax - NetCreditsApplied - NetPaymentsApplied`, and each rollup equals the net of the invoice's line-level credit or payment rows. An unpaid invoice with no rows and no `SettlementLevel` is measured. |
| `invoice_line_balance` | On a measured invoice whose own evidence is line level (line rows or `SettlementLevel` `InvoiceLine`; an invoice with no evidence is skipped): per line, `Balance = LineAmount - NetCreditsApplied - NetPaymentsApplied`, and each rollup equals the net of that line's rows. An invoice with no readable lines fails. |
| `payment_balance` | On a measured payment: `Balance = Amount - NetApplied`, and `NetApplied` equals the net of the payment's rows on any invoice. |

The level to expect comes from `--expect-level`, or else from the records: application
rows of one level, or a `SettlementLevel` of `InvoiceLine` or `Invoice`. An invoice with
neither is skipped, however the level was chosen. When the invoices show both levels, each invoice with
rows or a `SettlementLevel` fails, and each invoice with neither is skipped. The Billing Settings
level itself is not read: `BillingSettings` is not queryable through the Tooling API
(`INVALID_TYPE`) [Measured: 2026-11-25, 264, scratch org, API 68.0].

## What the formulas rest on

[Measured: 2026-11-25, 264, scratch org, API 68.0, Line Level], on a payment applied at
posting and two credit memos applied to one line:

- `Invoice.SettlementLevel` was `InvoiceLine` on invoices with an application and null
  on invoices without one. It is also null on an invoice whose every
  application was unapplied (the original rows stay Applied with `UnappliedStatus` Yes, so
  do not read an Applied row alone as in force)
  [Measured: 2026-11-27, 264, fresh scratch build, API 68.0, Line Level]
  (*Measured: unapply* in [payments-and-credits.md](payments-and-credits.md)).
- The invoice total to use is `TotalAmountWithTax`. `TotalChargeAmountWithTax` held the
  charge without tax, and `InvoiceLine.ChargeAmountWithTax` equalled `ChargeAmount`
  with `ChargeTaxAmount` 0, although the line carried `TaxAmount`.
- `InvoiceLine.LineAmount` was charge plus tax, and the line's `Balance` was
  `LineAmount` less its `NetCreditsApplied` and `NetPaymentsApplied`.
- A Canceled payment with no applications kept `Balance` equal to `Amount`.

Not measured, so outside the allow-list: Header Level, unapplied rows other than the
measured line-level pair (an unapply is always whole; `cli unapply` and the
measurements are in the harness's `docs/contracts-billing-settlement.md` → *Unapply*),
credit memos in any status other than
Posted, how
`NetRefundApplied` and `NetPaymentCreditApplied` change a payment's `Balance` (both were
0 on every payment read), how converted negative amounts, write-offs and adjustments
change an invoice's or line's `Balance` (each field listed in the table above was 0 or
null on every invoice and line read), invoices with header-level tax or separate tax
lines (every line read was `Type` Charge and `TotalTaxesCapturedAtHeader` was null, so
both are skipped), and payments in any status other than Processed or Canceled. A failure
in one of those cases may be the formula, not the data; measure the fields with SOQL
before changing either.

## Validation Checks

- `python -m pytest tests/txn_data_harness/test_verify_billing.py` runs every check
  against recorded query results, plus one failing case per check. The line-level
  fixture exercises the balance checks; the header-level fixture asserts that they skip
  for its records with header evidence, that its unpaid invoice with no evidence still
  gets `invoice_balance`, and that `application_level` still runs.
- On a live org, `--expect-level` set to the wrong level must exit 1 naming
  `application_level`. Use an invoice with application rows or a `SettlementLevel`: an
  invoice with neither is skipped, so it cannot fail.
