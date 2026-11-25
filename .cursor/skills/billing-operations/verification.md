# Billing Operations — Verifying Balances and Applications

Read this when checking, without writing anything, that invoices, invoice lines and
payments agree with the payments and credits applied to them. Parent:
[SKILL.md](SKILL.md). What the application levels do and how they were measured is in
[payments-and-credits.md](payments-and-credits.md) → *Measured: Line Level application*;
this page does not repeat it.

## The verifier

`cli verify` in the Transaction Data Harness reads records by id and runs the checks
below. It only runs SOQL queries [Repo: `scripts/txn_data_harness/verify.py`].

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

- **0**: no check failed (a skipped check is not a failure).
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
the output stops quietly and the exit code is still the checks' result. From a manifest, `verify` reads `invoice_id` or `invoice_ids`. Harness
manifests carry no payment ids (no stage writes them); `payment_id` or `payment_ids` is
read only if a manifest has one. A manifest with no ids is only a warning when another
source supplies ids.
`--latest` reads only the newest manifest, so after a batch of several scenarios pass
each manifest with `--manifest` (repeatable) or the ids with `--invoice-ids`.
Payments are found through the invoices' application rows, or passed with
`--payment-ids` (for example one with no applications). `--payment-ids` alone checks just
those payments.

## Checks

The net of a set of application rows is the sum of their amounts; every row is
`Applied`, or the check skips (below). Amounts compare exactly as decimals, with no rounding, so a
currency with zero or three decimal places is checked as it is stored. A null `Balance`
fails wherever the check runs (a skipped case skips).

**Posted invoices only.** The balance formulas were measured on Posted invoices, so
`invoice_balance` and `invoice_line_balance` skip an invoice whose `Status` is anything
else (Draft, for example); the skip names the status. `application_level` still runs.
Likewise `payment_balance` checks a Processed payment, and a Canceled payment with no
application rows, the two measured cases; any other status, or a Canceled payment with
rows, is skipped with the status named. Where nothing was measured, a check skips with a
reason; it never guesses a formula.

**Line Level only.** Header Level was never measured (its fixture is built from field
shapes), so every balance check is skip-only there: `invoice_balance` skips an invoice
whose own evidence includes header level (header application rows or `SettlementLevel`
`Invoice`), `invoice_line_balance` runs only on line-level evidence (below), and
`payment_balance` skips a payment with any header-level application row. Each skip names
the evidence. An unpaid invoice with no rows and no `SettlementLevel` keeps
`invoice_balance`, as measured on a Line Level org. `application_level` still runs.

**No unapplied rows.** Unapplied application rows were not measured on 264 (the org read
had none). An invoice or payment with any application row whose `Type` is not Applied
(Unapplied, another value or null), or any row flagged unapplied (`UnappliedStatus` or
`HasBeenUnapplied` = `Yes`; both are picklists of No, Yes and NA [Measured: 2026-11-25, 264, scratch org, API 68.0]), skips
`invoice_balance`, `invoice_line_balance` or `payment_balance`, with the reason "has
unapplied application rows, or rows not of Type Applied (not measured on 264)".

| Check | Passes when |
| ----- | ----------- |
| `application_level` | The invoice has no application rows of the other level, and its `SettlementLevel` does not name the other level. Line rows: `PaymentLineInvoiceLine`, `CreditMemoLineInvoiceLine`. Header rows: `PaymentLineInvoice`, `CreditMemoInvApplication`. Skipped for an invoice with neither application rows nor a `SettlementLevel`, whether the level was detected or forced with `--expect-level`. |
| `invoice_balance` | `Balance = TotalAmountWithTax - NetCreditsApplied - NetPaymentsApplied`, and each rollup equals the net of the invoice's line-level credit or payment rows. Skipped for an invoice whose own evidence includes header level. Skipped for an invoice with a non-zero `TotalConvertedNegAmount`, `WriteOffTotalChargeAmount`, `WriteOffTotalTaxAmount` or `TotalAdjustmentAmount`, or any `WriteOffStatus`; the skip names the field. Skipped for an invoice that is not Posted, has `Type` Tax lines, or has a non-zero `TotalTaxesCapturedAtHeader`. |
| `invoice_line_balance` | Per line, `Balance = LineAmount - NetCreditsApplied - NetPaymentsApplied`, and each rollup equals the net of that line's rows. Every invoice-level reason that skips `invoice_balance` (header evidence, not Posted, tax, write-off and the other unmeasured fields, unapplied or non-Applied rows) also skips it: the two checks share one gate. Runs only on an invoice whose own evidence is line level alone: line application rows and/or `SettlementLevel` `InvoiceLine`, with no header rows and no `SettlementLevel` `Invoice`. Any other invoice (no evidence, header evidence, or both) is skipped with its evidence named, whatever level the set has or `--expect-level` forces. Also skipped for a line of `Type` Adjustment or with a non-zero `ConvertedNegAmount`, `ChargeConvertedNegAmount` or `AdjustmentAmount`. An invoice with no readable lines fails. |
| `payment_balance` | `Balance = Amount - NetApplied`, and `NetApplied` equals the net of the payment's rows on any invoice. Skipped for a payment with any header-level application row. Checked for a Processed payment and for a Canceled payment with no application rows; skipped for any other status or a Canceled payment with rows. Skipped for a payment whose `NetRefundApplied` or `NetPaymentCreditApplied` is not zero; the skip names the field. |

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
  on invoices without one.
- The invoice total to use is `TotalAmountWithTax`. `TotalChargeAmountWithTax` held the
  charge without tax, and `InvoiceLine.ChargeAmountWithTax` equalled `ChargeAmount`
  with `ChargeTaxAmount` 0, although the line carried `TaxAmount`.
- `InvoiceLine.LineAmount` was charge plus tax, and the line's `Balance` was
  `LineAmount` less its `NetCreditsApplied` and `NetPaymentsApplied`.
- A Canceled payment with no applications kept `Balance` equal to `Amount`.

Not measured: Header Level (balance checks skip there, as above), unapplied rows
(their sign, pairing, and whether an unapply can be partial; such invoices and payments
are skipped, as above), how
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
  and that `application_level` still runs.
- On a live org, `--expect-level` set to the wrong level must exit 1 naming
  `application_level`. Use an invoice with application rows or a `SettlementLevel`: an
  invoice with neither is skipped, so it cannot fail.
