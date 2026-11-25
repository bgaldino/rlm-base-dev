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
  an `sf` CLI that is not on `PATH`. An `ERROR:` line goes to stderr; with `--json`,
  stdout gets `{"ok": false, "error": "..."}`.

Ids may be 15 or 18 characters; they are converted to the 18-character form before
querying. From a manifest, `verify` reads `invoice_id` or `invoice_ids`, and `payment_id`
or `payment_ids` when the manifest has them. Manifests that stop at an invoice stage carry
no payment ids. A manifest with no ids is only a warning when another source supplies ids.
`--latest` reads only the newest manifest, so after a batch of several scenarios pass
each manifest with `--manifest` (repeatable) or the ids with `--invoice-ids`.
Payments are the ones named in a manifest or by `--payment-ids`, plus every payment with
an application row on the invoices. `--payment-ids` alone checks just those payments.

## Checks

The net of a set of application rows is the sum of `Applied` amounts minus the sum of
`Unapplied` amounts. Amounts compare exactly as decimals, with no rounding, so a
currency with zero or three decimal places is checked as it is stored. A null `Balance`
always fails.

**Posted invoices only.** The balance formulas were measured on Posted invoices, so
`invoice_balance` and `invoice_line_balance` skip an invoice whose `Status` is anything
else (Draft, for example); the skip names the status. `application_level` still runs.

| Check | Passes when |
| ----- | ----------- |
| `application_level` | The invoice has no application rows of the other level, and its `SettlementLevel` does not name the other level. Line rows: `PaymentLineInvoiceLine`, `CreditMemoLineInvoiceLine`. Header rows: `PaymentLineInvoice`, `CreditMemoInvApplication`. |
| `invoice_balance` | `Balance = TotalAmountWithTax - NetCreditsApplied - NetPaymentsApplied`, and each rollup equals the net of the invoice's credit or payment rows (both levels). Skipped for an invoice with a non-zero `TotalConvertedNegAmount`, `WriteOffTotalChargeAmount`, `WriteOffTotalTaxAmount` or `TotalAdjustmentAmount`, or any `WriteOffStatus`; the skip names the field. Skipped for an invoice that is not Posted. |
| `invoice_line_balance` | Per line, `Balance = LineAmount - NetCreditsApplied - NetPaymentsApplied`, and each rollup equals the net of that line's rows. Skipped for every invoice when the level is header (expected or detected), for an invoice that is not Posted, for an invoice whose rows are header rows only, and for a line of `Type` Adjustment or with a non-zero `ConvertedNegAmount`, `ChargeConvertedNegAmount` or `AdjustmentAmount`. An invoice with no readable lines fails. |
| `payment_balance` | `Balance = Amount - NetApplied`, and `NetApplied` equals the net of the payment's rows on any invoice. Skipped for a payment whose `NetRefundApplied` or `NetPaymentCreditApplied` is not zero; the skip names the field. |
| `unapplied_rows` | Every `Unapplied` row pairs, by its self-lookup, with an `Applied` row marked unapplied (`UnappliedStatus` or `HasBeenUnapplied` = `Yes`), and every `Applied` row marked unapplied has its pair. Both flags are picklists of No, Yes and NA [Measured: 2026-11-25, 264, scratch org, API 68.0]. The pair's amounts are not compared (see below). |

The level to expect comes from `--expect-level`, or else from the records: application
rows of one level, or a `SettlementLevel` of `InvoiceLine` or `Invoice`. With neither,
`application_level` is skipped. When the invoices show both levels, each invoice with
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

Not measured: Header Level (its fixture is built from field shapes), `Unapplied` rows
(including the sign of their `Amount`, so either sign is counted as a reversal, and
whether an unapply reverses the whole applied amount or can be partial; the org read
had no `Unapplied` rows, so `unapplied_rows` pairs rows by `Type` and self-lookup but
does not compare their amounts, and does not fail on a difference), how
`NetRefundApplied` and `NetPaymentCreditApplied` change a payment's `Balance` (both were
0 on every payment read), how converted negative amounts, write-offs and adjustments
change an invoice's or line's `Balance` (each field listed in the table above was 0 or
null on every invoice and line read), and invoices with header-level tax or separate tax lines. A failure in one of those cases may be the
formula, not the data; measure the fields with SOQL before changing either.

## Validation Checks

- `python -m pytest tests/txn_data_harness/test_verify_billing.py` runs every check
  against recorded query results for both levels, plus one failing case per check.
- On a live org, `--expect-level` set to the wrong level must exit 1 naming
  `application_level`.
