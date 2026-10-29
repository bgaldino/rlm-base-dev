# Backdated Asset Changes — API, UI and Billing Runbook

Read this when you need an asset change that **took effect in the past**: an amendment,
cancellation, renewal, transfer, swap, upgrade or downgrade with an effective date before
today, verified all the way to the invoice. Parent skill: [SKILL.md](SKILL.md).

**Evidence base:** live runs on 264, 2026-10-28, on pk049-r1 (`ent-r1`, todos 246 and 306) and on
a fresh `ent-r1` build of main (`r1-306`, todo 306). Plain term product `QB-API-PROD` (Term
Annual, billed monthly at 270.00, USD); ramps on `QB-GEN-AI-LIC`; usage on `QB-DB`. Effective
date 2026-08-01, invoiced through today (2026-10-28) before the change; monthly advance billing
bills October in full. Treat every "measured" below as those runs, not as a general rule. Other
selling models weren't run.

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
- **Usage-based products can't be backdated at all on 264 (measured).** Amend, cancel and renew
  with a past date are refused with *"Operations with dates in the past aren't supported for
  usage-based products"*, with either Order or Quote output. The same asset accepts a future
  date. Help's rule about usage products with "both a future-dated and a backdated change"
  reads as if such changes could exist; the platform doesn't allow them. `RLM_ARC_Assets` now
  stops a past date for usage-based assets with its own error screen (todo 306).

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

Measured in the UI run (2026-10-28: amend, cancel, renew, transfer, swap, upgrade and downgrade
each continued through invoice with the verifier and passed; rollback refused in the viewer with
*"We couldn't complete the rollback. The asset's amendment period has started"*):

- **The flow creates quotes**; Create Order → Create Single Order makes the order.
- **Swap/upgrade/downgrade product picker** lists only products in a catalog category. QB API
  Management Solution (`QB-API-MGMT`) is in none, so it can't be picked; Additional QB DataGraph
  and Additional API Flex/Pre-Prod can.
- **The incoming swap/upgrade line uses the product's own term and billing frequency**: here a
  year from the swap date (08-01 → 2027-07-31) billed **Annual**, not co-termed with the outgoing
  asset as the API run was. So billing differs between paths: the UI swap's catch-up invoice bills
  the incoming product's full annual period (3,240.00) against three monthly credits (−810.00).
- **Transfer: run Create Order on one transfer quote only.** `RLM_CreateOrdersFromQuote` makes
  both the source and target orders from either quote; running it on the second quote makes a
  duplicate pair. Activate the source order first.
- **Early renewal with a ramp schedule (UI, todo 306).** Override → *Create a ramp schedule* →
  Yearly, 24 months. The End Date field hides; the ramp duration sets the end. The quote matched
  the API run exactly: Year 1 814.43, Year 2 3,242.23. Its order invoiced to net 0.00.
- **Usage-based assets (UI, todo 306).** A past date on Amend, Cancel or Renew shows the flow's
  error, *"This change can't be backdated: the selected assets include usage-based products…"*,
  with the asset listed; Previous returns to the date screen. A future date goes straight to the
  quote.
- **Billing info on swap/upgrade/downgrade quotes.** These quotes leave `OriginalActionType`
  blank and have no Opportunity, so `RLM_Update_Quote_Billing_Info_From_Opportunity_Account`
  used to skip them and Create Order stopped at *"This quote isn't ready to create orders yet"*.
  It now also defaults bill-to contact and addresses from the account for any quote without an
  Opportunity (todo 305).

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
| Early renewal (Override) of an active asset | +1 renewal, −1 refund of the current term's rest | net 0.00 for the elapsed months (lines netted, see below) |
| Billing frequency Monthly → Quarterly (zero-quantity field amendment) | −1 monthly, +1 quarterly | net 0.00 (−810.00 monthly credit, +810.00 first quarter) |

**Ramped assets** (a 2-year line ramp of `QB-GEN-AI-LIC`, Year-1 qty 1 at 12.50/month, Year-2
qty 2, from 2026-05-01; built with `build_quote_to_asset.py --ramp-years 2 --ramp-quantities 1,2`):

| Scenario | What the platform did | Invoice after the change |
|---|---|---|
| Amend +1 | Changes only the segment it falls in: Year-1 +1 from 08-01; the Year-2 line has quantity 0 | 37.50 (3 × 12.50) |
| Amend −1 (a 2,3 ramp) | Year-1 only | −37.50 → credit memo |
| Cancel | Credits Year-1 from 08-01 **and** Year-2 from its own start (2027-05-01), which isn't billable yet | −37.50 → credit memo |
| Renew an expired 2-year ramp | One unramped year at the **last segment's quantity** (2) | 75.00 (3 × 25.00) |
| Early renewal **with a ramp** (`rampOptionsDetails`: Yearly, 24 months) of a plain asset | Year-1 and Year-2 segments (one `RampIdentifier`) + a refund of the current term's rest | net 0.00 |

**Group-ramp assets** (multi-schedule: a `RampScheduleGroup` parent with Yearly segment groups),
`QB-API-PROD` at 270.00/month. Built with `build_quote_to_asset.py --ramp-years 2 --ramp-quantities 1,2 --ramp-kind group`
(from 2026-05-01, segments 2026-05-01 and 2027-05-01), change effective 2026-08-01:

| Scenario | What the platform did | Invoice after the change |
|---|---|---|
| Amend +1 (a 1,2 ramp) | Year-1 segment only, as with line ramps; the Year-2 line has quantity 0 | 810.00 (3 × 270) |
| Amend −1 (a 2,3 ramp) | Year-1 only | −810.00 → credit memo |
| Cancel (a 1,2 ramp) | Credits Year-1 from 08-01 and Year-2 (qty 2) from its own start | −810.00 → credit memo |
| Cancel (a 3-year 1,2,3 ramp) | Credits Year-1 from 08-01, Years 2 and 3 from their own starts | −810.00 → credit memo |
| Renew an expired 2-year ramp (1,2, 2024-08-01 → 2026-07-31) | One unramped year at the last segment's quantity (2) | 1,620.00 (3 × 540) |
| Early renewal (with a ramp; without one it's refused, below) | Prices the new segments at **zero** (null `UnitPrice`) and refunds the current ramp. Same future-dated, and on a ramp from an earlier ramped renewal. | not run through billing |

The same amend ±1 and cancel also passed on group ramps made by an earlier ramped renewal
(segments 2026-08-01 and 2027-08-01, change effective 09-01 or 10-01); there the Year-2 credit
starts 2027-08-01, a year after the renewal, not after the asset's start. The zero-priced early
renewal is open as todo 309: the cause, platform or this repo's pricing procedure, isn't known.

- An early renewal of a ramp asset without a ramp is refused: *"You can only renew a ramped asset
  early by turning on Create a Ramp Schedule when setting the renewal terms on the renewal
  quote."*
- The credit schedules of a ramp cancel carry **no** `RampIdentifier` or `SegmentName`.
- After a cancel, the asset keeps only its first state period. So `AssetStatePeriod` gives the
  segment boundaries only before the change; the verifier reads them first.
- `RLM_ARC_AssetValidator` still blocks swap, upgrade/downgrade, transfer and rollback for ramped
  assets, as 264 Help requires.

**Netted lines.** Billing can combine a group's schedules into invoice lines with **no
`BillingScheduleId`**, carrying only `BillingScheduleGroupId`. Measured on early renewals: the
renewal's Year-1 charge and the refund became zero-quantity 0.00 lines. Match those by group.

**Changing billing frequency (INV-12).** Help: on an active subscription, only a zero-quantity
amendment with the **FieldAmendment** subtype can change it. Billing then cancels the old
schedule and starts the new cadence from the effective date. Through the API:

1. `initiateAmendment` with `quantityChange: 0` and `amendOutputType: Quote`. Its
   `actionSubtype` input offers only `StartDateAdjustment` and `Rollback`.
2. Set the line's `QuoteAction` to `Type = Amend`, `Subtype = FieldAmendment`. Without this, Place
   refuses the next step: *"You can only change the Billing Frequency of a Quote Line Item when
   the Quote Action is amend and the Quote Action subtype is FieldAmendment."* In the UI, editing
   the field does this.
3. Place a `QuoteLineItem` PATCH with the new `BillingFrequency`, then order and activate as
   usual. The line's billing treatment needs *Change Billing Frequency*.

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
the first order is on the asset's account, signs fit the action's sign class (only + for
amend-up/renew-expired, only − for amend-down/cancel, one − and one + for transfer, swap,
upgrade, downgrade and billing-frequency, one − refund and at least one + for renew-early), and a
transfer's target order is on another account.

- Scenarios: `amend-up`, `amend-down`, `cancel`, `renew-expired`, `renew-early`,
  `billing-frequency`, `transfer`, `swap`, `upgrade`, `downgrade`, `rollback`.
- Ramps:
  - `--ramp-years N --ramp-quantities 1,2` builds the asset as a Yearly line ramp. Its product
    needs `Product2.CanRamp`; in QB that's `QB-GEN-AI-LIC`, `QB-API`, `QB-DB-TOKEN` or
    `QB-SUPP-2000`. Add `--ramp-kind group` for a group ramp, which any term product can be. A
    group ramp whose first year contains 29 February is refused: segment 1 is 365 days but the
    clones end on calendar dates.
  - Ramps run through the API only (no `--order`), and amend-down needs a Year-1 quantity of 2 or
    more. To change an existing ramp asset, pass `--asset <id> --ramp-years N`.
  - With a ramp asset, only amend-up, amend-down, cancel and renew-expired are offered: Help
    allows amend, renew and cancel, and an early renewal *of* a ramp asset is zero-priced (above).
  - The built ramp runs N years, so the effective-date limit below is stricter than it needs to be.
  - `renew-early --renewal-ramp-years N` renews into a Yearly ramp.
- Usage products: their usage-resource schedules bill through rating, so the check skips them
  (`scripts/apex/validateRatedUsage.apex` covers rating). Backdating them is refused anyway, see
  *What Help allows*.
- Use one account per scenario. It needs a contact and a billing address, and no asset of
  `--sku` (default `QB-API-PROD`) yet. A transfer's `--target-account` needs a contact and a
  billing address too: its order is activated and invoiced as well. `rollback` has no UI mode.
- `--effective` must be a 1st of the month (so periods align) and recent enough that the term
  is still running today: at most 8 months before the current month (the built asset is a
  one-year term from the 1st three months before it), or 11 for `renew-expired` (the renewal is
  a one-year term from the effective date).
- The check waits until every non-zero line of the change's order(s) has a schedule (matched
  per line; billing-frequency also waits on its quantity-0 line) and a further poll finds no
  new ones. Then, **per schedule**: it starts on the
  effective date (in ramp mode, a later segment may start on its own order line's start, a whole
  number of years after the asset start or one of its state periods' starts; with
  `--renewal-ramp-years`, after the effective date), its first invoice line
  starts there, and its lines sum to sign × the
  schedule's `BillingPeriodAmount` × the billing periods of that schedule's own term
  (Month, Quarter, Semi-Annual, Year; any other unit fails as unmodelled) started since then.
  A schedule that hasn't started must not be invoiced. Netted lines are checked per
  `BillingScheduleGroupId` with the same sum and first-line rules; a group that nets to zero
  proves only that its lines net out, not each schedule's share.
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

- **Early renewal of a ramp asset.** Zero-priced, as measured above, so a backdated one can't be
  verified yet (todo 309).
