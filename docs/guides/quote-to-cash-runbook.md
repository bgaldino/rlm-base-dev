# Guide: Quote-to-Cash Runbook

How to carry one transaction from a quote to an applied payment on a Revenue
Cloud org, checking each stage as it lands, and how to check a built org in one
command. The chain:

```text
Quote (Place Sales Transaction) → Order → Activation (billing schedules, assets)
   → Draft invoice → Posted invoice → Credit memo applied → Payment applied
```

Everything here drives the
[Transaction Data Harness](txn-data-harness.md) (`scripts/txn_data_harness/`)
and its read-only verifier (`cli verify`). Read the harness guide for
prerequisites, flags and the full cleanup recipes; this page is the procedure.
What the verifier checks, and the formulas, are in the `billing-operations`
skill: [`verification.md`](../../.cursor/skills/billing-operations/verification.md).

## Before you start

- **An `sf` alias or username**, not a CCI alias (CCI `beta` is sf
  `rlm-base__beta`).
- **A billing-ready account**: one with a `BillingAccount`. Without one the
  harness caps the run at `order_draft`, before activation. The shipped
  scenario uses **Infinitech** and **QB-API-FLEX** from the QuantumBit data a
  standard build loads.
- **Line Level application.** The org's Credit, Payment and Refund Application
  Level is read from Billing Settings at run time. Line Level, the Foundations
  default, is live-verified. Header Level is not measured: the verifier skips
  its balance checks, so `cli quote-to-cash` fails there with "no balance was
  checked" even when every stage ran.
- **A scratch or demo org.** Every run adds a new transaction. Posted
  invoices, billing schedules and the settlement records cannot be deleted
  (see [Cleanup limits](#cleanup-limits)).
- **One run at a time per account**: posting an invoice applies the account's
  open payment balance to it, so parallel runs on one account can take each
  other's payment. The commands below use `--concurrency 1`.

## One command

```bash
python -m scripts.txn_data_harness.cli quote-to-cash --org <sf-alias>
```

It runs [`20-quote-to-cash.yaml`](../../scripts/txn_data_harness/scenarios/sales_txn_quote/20-quote-to-cash.yaml)
at `--concurrency 1` (one quote, a 10% credit, a payment for exactly what is
left), fails unless every scenario reaches `payment_applied`, then runs the
`cli verify` checks on the invoices and payments the run recorded. On exit 0
or 1 the last line is `QUOTE-TO-CASH: pass (...)` or `QUOTE-TO-CASH: fail
(...)`; otherwise an `ERROR:` line on stderr says why.

| Exit | Meaning |
|------|---------|
| 0 | Every scenario reached `payment_applied`, at least one balance was checked, none failed. |
| 1 | A scenario stopped short (its `FAIL:` line names the run and the stage it reached), or a balance check failed, or nothing was checked. |
| 2 | An error, not a verdict: authentication failed, `sf` is not on `PATH`, a Salesforce request was refused, or a manifest could not be read. |
| 3 | Discovery failed before any write, for example an unknown account or product. |
| 4 | The config could not be read, or a scenario in it does not target `payment_applied`; refused before any write. |

`--config <file>` runs another config; its scenarios must target
`payment_applied`. Measured on a 264 scratch org (2026-11-26, Line Level): a
495.00 invoice, 49.50 credit, 445.50 payment, every balance 0, exit 0.

### Checking a built org

`verify_quote_to_cash` wraps the same command as a CCI task:

```bash
cci task run verify_quote_to_cash --org <cci-alias>
cci task run verify_quote_to_cash --org <cci-alias> -o config <path-from-repo-root>
```

It passes the org's username to the harness, runs it with CumulusCI's Python
from the repo root, and fails when the command exits non-zero. It is opt-in and
in no flow, because it writes records that cannot be deleted. Run it after
`prepare_rlm_org` when you want proof that the org can bill and settle.

## Stage by stage

Use this to walk a transaction through by hand, for a demo or to find which
stage breaks. Start a run that stops at the quote, then step it on with
`cli step`, checking after each stage. Set these first:

```bash
ORG=<sf-alias>
CFG=scripts/txn_data_harness/scenarios/sales_txn_quote/20-quote-to-cash.yaml
python -m scripts.txn_data_harness.cli plan --org $ORG --config $CFG   # no writes
python -m scripts.txn_data_harness.cli run --org $ORG --config $CFG \
  --target-stage quote_placed --concurrency 1
RUN=<the run id it prints after "run base">
```

Then, for each stage in the table:

```bash
python -m scripts.txn_data_harness.cli step --org $ORG --manifest $RUN --to-stage <stage>
python -m scripts.txn_data_harness.cli inspect --manifest $RUN
python -m scripts.txn_data_harness.cli verify --org $ORG --manifest $RUN   # from invoice_draft on
```

| Stage | What the step does | What to check |
|-------|--------------------|---------------|
| `quote_placed` | Places the quote (Place Sales Transaction). | `inspect` shows a `quote:` id. `verify` exits 2 here and at the two order stages: the manifest names no invoice yet. |
| `order_draft` | Creates the order from the quote. | `inspect` shows an `order:` id; the Order is `Draft`. |
| `order_activated` | Activates the order and waits for billing schedules and assets. | `inspect` shows `billing_schedules:` and `assets:` ids; the Order is `Activated`. |
| `invoice_draft` | Generates the invoice (passes through `usage_upload` for a non-usage product). | `verify`: `RESULT: pass (no balances checked; 2 skipped)`; Draft invoices are not checked. |
| `invoice_posted` | Posts the invoice. | `verify`: `invoice_balance` passes (balance = total); the line check skips, because nothing applied yet shows the level. |
| `credit_applied` | Creates the credit memo and applies it. Pass `--config $CFG` on this step: the run stopped before the settlement stages, so its manifest has no settlement block yet. | `verify`: invoice and line balances = total − credit (445.50 = 495.00 − 49.50 measured). |
| `payment_applied` | Creates one external payment (no gateway) for what is left and applies it. No `--config`: the credit step recorded the whole block. | `verify`: `application_level` (line), invoice and line balances 0, `payment_balance` 0. |

All seven steps and every check above passed on a 264 scratch org on
2026-11-26.

A `--config` on a later step must match the recorded block exactly; changing
settlement options means a new run. A manifest recorded before 2026-11-26 that
stopped at `credit_applied` holds only the credit: rerun its credit step
without `--config` (the file's payment part no longer matches the recorded
block), and start a new run for the payment.

The same steps apply to other scenarios. For `invoice_ingestion` (an invoice
minted directly, no quote or order), start at `invoice_draft` or
`invoice_posted` with
[`invoice_ingestion/17-settlement.yaml`](../../scripts/txn_data_harness/scenarios/invoice_ingestion/17-settlement.yaml).

## When a stage fails

1. `inspect --manifest $RUN --json` shows `reached_stage`, `error` and
   `failure_class` (the text form leaves out `failure_class`).
2. A transient failure (a timeout, a lock) usually clears on a rerun of the
   same `cli step`; the steps are safe to resend (at most one credit memo and
   one payment per run, looked up by tag rather than sent twice).
3. A deterministic failure names its remedy. Common ones:
   - capped at `order_draft`: the account has no `BillingAccount`;
   - the application level could not be read: rerun the step with
     `--application-level line` (or `header`);
   - posted-invoice tax treatment missing (ingestion only): seed the
     `TaxTreatment` the error names.
4. Rules for resuming, the write rule and the failure classes are in
   [`contracts-billing-settlement.md`](../../scripts/txn_data_harness/docs/contracts-billing-settlement.md).

## Cleanup limits

Drive any cleanup from the manifest ids
([harness guide → Cleanup](txn-data-harness.md#cleanup)). What stays behind:

- **Posted invoices**: only Draft or Canceled invoices can be deleted, and
  `Status` cannot be set to Canceled.
- **Billing schedules**: system-managed.
- **Credit memos, payments and their applications**: no unapply, void or
  cancel path was measured.

Assets, the activated order (revert to Draft first) and the quote can be
deleted, child first (and the opportunity, for a config that sets
`with_opportunity: true`; the shipped one does not).

## Related procedures

Linked, not repeated here:

- **Backdated asset chains for usage rating** (a billing period already
  closed): `scripts/build_quote_to_asset.py`; see
  [`usage-consumption/building-usage-assets.md`](../../.cursor/skills/usage-consumption/building-usage-assets.md).
- **Usage rating**: the [`usage-consumption`](../../.cursor/skills/usage-consumption/SKILL.md)
  skill, and `cli rate` after a `usage_upload` run.
- **Renewals**: the [`renewal-asset-creation`](../../.cursor/skills/renewal-asset-creation/SKILL.md)
  skill.
- **Billing behaviour behind each stage**: the
  [`billing-operations`](../../.cursor/skills/billing-operations/SKILL.md) and
  [`billing-setup`](../../.cursor/skills/billing-setup/SKILL.md) skills.
