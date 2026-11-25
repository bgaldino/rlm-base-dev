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
# ids from a harness manifest (repeat --manifest for several; --latest for the newest)
python -m scripts.txn_data_harness.cli verify --org <sf-alias> --manifest <run-id-or-path>
# ids by hand; add --payment-ids for a payment with no applications
python -m scripts.txn_data_harness.cli verify --org <sf-alias> \
  --invoice-ids <invoiceId>,<invoiceId> --payment-ids <paymentId> --json
# force the level, for example as a negative control
python -m scripts.txn_data_harness.cli verify --org <sf-alias> \
  --invoice-ids <invoiceId> --expect-level header
```

Exit 0 when no check fails (a skipped check is not a failure); exit 1 when any check
fails, or when an id is malformed, not found or not readable. `--json` prints every
result with its check name, subject id, status and detail. Payments are the ones named
in the manifest or by `--payment-ids`, plus every payment with an application row on
the invoices.

## Checks

The net of a set of application rows is the sum of `Applied` amounts minus the sum of
`Unapplied` amounts. Amounts compare to the cent.

| Check | Passes when |
| ----- | ----------- |
| `application_level` | The invoice has no application rows of the other level, and its `SettlementLevel` does not name the other level. Line rows: `PaymentLineInvoiceLine`, `CreditMemoLineInvoiceLine`. Header rows: `PaymentLineInvoice`, `CreditMemoInvApplication`. |
| `invoice_balance` | `Balance = TotalAmountWithTax - NetCreditsApplied - NetPaymentsApplied`, and each rollup equals the net of the invoice's credit or payment rows (both levels). |
| `invoice_line_balance` | Per line, `Balance = LineAmount - NetCreditsApplied - NetPaymentsApplied`, and each rollup equals the net of that line's rows. Skipped for an invoice whose rows are header rows only. |
| `payment_balance` | `Balance = Amount - NetApplied`, and `NetApplied` equals the net of the payment's rows on any invoice. |
| `unapplied_rows` | Every `Unapplied` row pairs, by its self-lookup, with an `Applied` row marked unapplied (`UnappliedStatus` or `HasBeenUnapplied` = `Yes`), and every `Applied` row marked unapplied has its pair. |

The level to expect comes from `--expect-level`, or else from the records: application
rows of one level, or a `SettlementLevel` of `InvoiceLine` or `Invoice`. With neither,
`application_level` is skipped; with both levels present, it fails. The Billing Settings
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
(including the sign of their `Amount`), refunds against a payment, and invoices with
header-level tax or separate tax lines. A failure in one of those cases may be the
formula, not the data; measure the fields with SOQL before changing either.

## Validation Checks

- `python -m pytest tests/txn_data_harness/test_verify_billing.py` runs every check
  against recorded query results for both levels, plus one failing case per check.
- On a live org, `--expect-level` set to the wrong level must exit 1 naming
  `application_level`.
