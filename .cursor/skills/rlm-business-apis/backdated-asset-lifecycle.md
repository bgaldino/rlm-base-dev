# Backdated Asset Changes — API, UI and Billing Runbook

Read this when you need an asset change that **took effect in the past**: an amendment,
cancellation, renewal, transfer, swap, upgrade or downgrade with an effective date before
today, verified all the way to the invoice. Parent skill: [SKILL.md](SKILL.md).

**Evidence base:** live runs on 264, org pk049-r1 (`ent-r1`), 2026-10-28, todo 246. One plain
term product, `QB-API-PROD` (Term Annual, billed monthly at 270.00, USD), effective date
2026-08-01, invoiced through today (2026-10-28) before the change; monthly advance billing bills
October in full. Treat every "measured" below as those
runs, not as a general rule. Other selling models, ramped and usage assets weren't run.

## What Help allows

From *Backdate Asset Transactions* and *Considerations for Assets with Backdated Changes*
(`docs/salesforce/264/help/articles/ind.qocal_*backdate*`):

- **Amend, renew, cancel:** standard and ramped assets. **Transfer, swap** (and so upgrade and
  downgrade, which are swap variants): standard assets only.
- The date must be on or after the asset's start date. No backdating on an asset that has a
  future-dated cancel. No amending a usage product that has both a future-dated and a backdated
  change. No reducing quantity below what's available in the line's date range.
- **Rollback can't undo a backdated change.** Only future-dated transactions that haven't started
  can be rolled back (*Transaction Rollbacks Considerations*). Measured: the rollback of a
  backdated amendment is refused with *"We couldn't complete the rollback. The asset's amendment
  period has started."*
- With Revenue Cloud Billing, billing aligns to the backdated date, prorates the affected period
  and credits periods already invoiced. Measured: true for every action below.

## UI path: `RLM_ARC_Assets`

Help says backdating needs the standard flow `runtime_revenue_arcflows__arcFlow` and names
`RLM_ARC_Assets` as a flow to replace. Ours is now **the 264 template plus our additions**, so it
doesn't need replacing:

- **From the 264 template:** no "today or later" rule on the date screen (the old copy had one;
  that was the only UI block), and the early-renewal ramp schedule fields (`rampOptionsDetails`
  on `initiateRenewal`). Ours sends ramp options only when the user ticks *Create a ramp
  schedule*; the template sends them whenever group ramps are enabled, with null segment fields
  on a plain renewal.
- **Ours on top:** the `RLM_ARC_AssetValidator` pre-check (blocks swap/upgrade/downgrade,
  transfer and rollback for the asset types 264 Help still excludes), separate Swap/Upgrade/
  Downgrade choices, English labels, and a **confirmation screen for every backdated date**
  (amend/cancel, renew, transfer, swap/upgrade/downgrade), which Help recommends.

To diff against a newer template: Flow Builder → open *Amend, Renew, and Cancel Assets* → Save
As a new flow (don't activate) → retrieve it. The template itself can't be retrieved (it's a
managed template, `IsTemplate = true`).

## API path

The flow calls standard invocable actions. Calling them through
`POST /services/data/v68.0/actions/standard/<action>` with `{"inputs":[{...}]}` exercises the
same path. All of these accepted a past date (measured):

| Action | Invocable / resource | Inputs | Returns |
|---|---|---|---|
| Amend | `initiateAmendment` | `amendAssetIds`, `amendStartDate`, `quantityChange`, `amendOutputType` | `amendRecordId` (order or quote) |
| Cancel | `initiateCancellation` | `cancelAssetIds`, `cancelStartDate`, `cancelOutputType` | `cancelRecordId` |
| Renew | `initiateRenewal` | `renewAssetIds`, `renewOutputType`, `renewStartDate`, `renewEndDate` | `renewRecordId` |
| Transfer | `initiateTransfer` | `transferRecords` `[{assetId, transferQuantity}]`, `transferDate`, `outputRecordType`, `targetAccountId` | `assetTransferSourceId`, `assetTransferTargetId` |
| Swap / Upgrade / Downgrade | `POST /revenue/transaction-management/assets/actions/{swap,upgrade,downgrade}` | `swapStartDate`, `outputRecordType`, `swapGroups` (below) | `salesTransactionId` (the quote) |
| Rollback | `initiateRollBackLastAction` | `assetIds`, `outputType` | `recordId` |

Dates are DATETIMEs: `"2026-08-01T00:00:00.000Z"`. The Connect equivalents of amend, cancel and
renew (`/connect/revenue-management/assets/actions/{amend,cancel,renew}`) also accept past dates;
their bodies use `amendmentStartDate`, `cancellationDate` and `renewalStartDate`.

Gotchas, all measured:

- **Renew an expired asset:** pass a start date. Without one: *"Select Override Renewal Term to
  renew expired or future-dated assets"*. A past start date is accepted, although the dev guide
  says "today's date or a future date".
- **Asset quantity:** read `Asset.CurrentQuantity`. `Asset.Quantity` stays null on these assets.
- **Swap/upgrade/downgrade incoming line** (`inGroup.records[]`, a `QuoteLineItem` POST): give it
  `Product2Id`, `PricebookEntryId`, `UnitPrice`, `Quantity`, `StartDate` (the effective date) and
  `EndDate` (co-term with the outgoing asset's `LifecycleEndDate`). Without `EndDate`: *"Specify
  either the end date or add the Subscription Term…"*. `BillingFrequency` also needs a
  `BillingTreatmentId` (*"Add a Billing Treatment to make sure that you can change the Billing
  Frequency"*); the outgoing asset's order line has one to reuse.
- **Transfer** returns two records. Help: activate the source order first, then the target.

## Activating the order

Set `Status = Activated` on each returned order (create the order from a returned quote first,
`createOrdersFromQuote`). Backdated-change orders needed all of these first:

- **shipping address**. The asset-action APIs don't copy the account's, just as quote-created orders
  don't. See `usage-consumption/building-usage-assets.md` → *FAILED_ACTIVATION*.
- **billing address and a bill-to contact**. Otherwise: *"We couldn't activate the Order. Enter the
  billing address and bill to contact associated with the account, and try again."*
  - This differs from new-sale orders on 262, which activated without them (txn-data-harness:
    `scripts/txn_data_harness/docs/contracts-sales-txn-quote.md`).
  - On 264, one new-sale order activated without Order billing fields (`building-usage-assets.md`).
    Whether new-sale orders need a bill-to contact wasn't isolated.

Fill them from the Account (`Billing*`, `Shipping*`) and any account Contact for
`BillToContactId`.

## Billing: invoice before and after the change

1. **Before:** invoice the asset through today and post, so periods are already billed.
2. **Make the change** and activate. Each new order line gets its own `BillingSchedule` whose
   `BillingScheduleStartDate` and `NextBillingDate` are the **effective date**. A reduction or
   cancel adds a **negative** schedule and stamps `CancellationDate` on the original one.
3. **After:** invoice the **new** schedules through today and post. Generate rejects the whole
   request if any schedule in it is already billed past the target date (*"don't meet the filter
   criteria for invoice creation"*), so send only schedules with `NextBillingDate <= today`.
4. A **negative** invoice posts as a posted **CreditMemo** whose `ReferenceEntityId` is the
   invoice. The memo carries the tax too (810.00 + 81.00 tax = 891.00 against an invoice of
   −891.00 with tax). The invoice's `Balance` drops to 0 **a moment after** the memo appears;
   read it straight after posting and it still shows the full negative amount.

```bash
# generate (Draft) and post — /services/data/v68.0/commerce/invoicing/invoices/collection/actions/…
POST …/generate {"billingScheduleIds":["<id>"],"action":"Draft","invoiceDate":"<today>","targetDate":"<today>"}
POST …/post     {"invoiceIds":["<draftInvoiceId>"]}
sf data query -o <sf-alias> -q "SELECT InvoiceNumber, Status, TotalAmount, Balance FROM Invoice WHERE Id = '<id>'"
sf data query -o <sf-alias> -q "SELECT CreditMemoNumber, Status, TotalAmount FROM CreditMemo WHERE ReferenceEntityId = '<invoiceId>'"
```

### Measured results

Asset from 2026-05-01 (renew: an expired term 2025-08-01 → 2026-07-31), 270.00/month, change
effective 2026-08-01, so August–October (3 periods) were affected:

| Scenario | New schedule(s) from 2026-08-01 | Invoice after the change |
|---|---|---|
| Amend +1 | +1 | 810.00 (3 × 270) |
| Amend −1 (from 2) | −1 | −810.00 → credit memo 810.00 |
| Cancel | −1 | −810.00 → credit memo 810.00 |
| Renew expired | +1, to 2027-07-31 | 810.00 |
| Transfer (full quantity) | −1 source, +1 target | source −810.00 → credit memo 810.00; target 810.00 |
| Swap → `QB-API-PREP` (same price) | −1 out, +1 in | one invoice, net 0.00 |
| Upgrade → `QB-API-MGMT` | −1 out, +1 in | one invoice, net 2,190.00 |
| Downgrade → `QB-API-FLEX` | −1 out, +1 in | net −695.01: credit memo 810.00 for the credits, offsetting 114.99 of new charges |
| Rollback of a backdated amend | — | refused (amendment period has started) |

Line amounts round to the currency's precision: a JPY run billed 44,033 per period against a
period amount of 44,033.42.

## Verifier script

`scripts/backdated_arc/verify_backdated_billing.py` runs one scenario end to end on one account
(build, invoice, change, activate, invoice, check), and prints `PASS`/`FAIL` with the reason:

```bash
# API path
python scripts/backdated_arc/verify_backdated_billing.py --org <sf-alias> --scenario cancel --account "<acct>"
python scripts/backdated_arc/verify_backdated_billing.py --org <sf-alias> --scenario transfer \
    --account "<from>" --target-account "<to>"
python scripts/backdated_arc/verify_backdated_billing.py --org <sf-alias> --scenario upgrade \
    --account "<acct>" --to-sku QB-API-MGMT
# UI path: prepare, make the change in the Managed Asset viewer, then continue from its order(s)
python scripts/backdated_arc/verify_backdated_billing.py --org <sf-alias> --scenario amend-up \
    --account "<acct>" --prepare-only
python scripts/backdated_arc/verify_backdated_billing.py --org <sf-alias> --scenario amend-up \
    --account "<acct>" --asset <assetId> --effective <same date> --order <orderId>
# a UI transfer passes both orders, source first
python scripts/backdated_arc/verify_backdated_billing.py --org <sf-alias> --scenario transfer \
    --account "<from>" --asset <assetId> --effective <same date> --order <sourceOrderId> --order <targetOrderId>
```

Pass the same `--effective` to both steps: its default moves with the calendar month. The
prepare step prints the full continue command. In UI mode the orders must match the scenario:
the first order is on the asset's account, signs fit the action's sign class (only + for amend-up/renew,
only − for amend-down/cancel, one − and one + for transfer/swap/upgrade/downgrade), and a
transfer's target order is on another account.

- Scenarios: `amend-up`, `amend-down`, `cancel`, `renew-expired`, `transfer`, `swap`, `upgrade`,
  `downgrade`, `rollback`.
- Use one account per scenario. It needs a contact and a billing address, and no asset of
  `--sku` (default `QB-API-PROD`) yet. A transfer's `--target-account` needs a contact and a
  billing address too: its order is activated and invoiced as well. `rollback` has no UI mode.
- `--effective` must be a 1st of the month (so periods align) and recent enough that the term
  is still running today: at most 8 months before the current month (the built asset is a
  one-year term from the 1st three months before it), or 11 for `renew-expired` (the renewal is
  a one-year term from the effective date).
- The check waits until every non-zero line of the change's order(s) has a schedule (matched
  per line) and a further poll finds no new ones. Then, **per schedule**: it starts on the
  effective date, its first invoice line starts there, and its lines sum to sign × the
  schedule's `BillingPeriodAmount` × the periods elapsed since the effective date.
  A zero-quantity schedule must bill nothing. Every negative invoice must have a credit memo and settle
  to `Balance = 0`. The expectation uses the platform's own period amount, so the check proves
  the invoice matches the schedule, not that the price is right.

## Verify the asset

```bash
sf data query -o <sf-alias> -q "SELECT StartDate, EndDate, Quantity FROM AssetStatePeriod WHERE AssetId = '<assetId>' ORDER BY StartDate"
sf data query -o <sf-alias> -q "SELECT LifecycleStartDate, LifecycleEndDate, CurrentQuantity FROM Asset WHERE Id = '<assetId>'"
```

From the first API run on pk049-r1 (a `QB-API-FLEX` asset, 2026-06-01 → 2027-05-31, not a
verifier run): a backdated amend +1 on 2026-08-01 split the asset's periods into `06-01→07-31`
qty 1 and `08-01→2027-05-31` qty 2. A backdated cancel on 2026-09-01 then ended them, and
`LifecycleEndDate`, on 2026-08-31.

## Not covered yet

- **Ramped and usage assets.** Help allows backdating amend, renew and cancel for ramped assets;
  none were run. `RLM_ARC_AssetValidator` still blocks swap, transfer and rollback for them, as
  264 Help requires.
- **A zero-quantity amendment that changes billing frequency** (INV-12 in the 264 solution
  overview). The amend API has no billing-frequency input, so it's a quote-side change.
- **Early renewal with a ramp schedule** (ported from the 264 template; shown only when the
  Managed Asset viewer passes `groupRampsEnabled = true`, and only for an Override renewal).
