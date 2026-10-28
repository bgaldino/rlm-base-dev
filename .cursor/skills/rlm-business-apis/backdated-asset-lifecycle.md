# Backdated Amend, Cancel and Renew — API Runbook

Read this when you need an asset change that **took effect in the past**: an amendment,
cancellation or renewal with an effective date before today. Parent skill: [SKILL.md](SKILL.md).

**Evidence base:** one live run on 264. Org pk049-r1 (`ent-r1`), 2026-10-28, todo 246; one product,
`QB-API-FLEX` on Term Annual. Treat every "measured" below as that run, not as a general rule.

## API path vs UI path

- **API path.** With the build's `RLM_ARC_Assets` set as the Manage Assets flow, all three
  backdated calls below were accepted, and the orders activated. Not tested against the standard
  flow, and not with other selling models or usage products.
- **UI path** (Managed Asset viewer → Amend / Renew / Cancel). Help says backdated changes *require*
  the standard flow `runtime_revenue_arcflows__arcFlow`, and names `RLM_ARC_Assets` as a custom or
  earlier flow to replace (`ind.qocal_backdate_asset_transactions.htm`).
  - `RLM_ARC_Assets` was cloned from that standard flow (`<sourceTemplate>` in its flow XML).
  - QB and TSO builds set it (`prepare_revenue_settings` → `configure_revenue_settings`, a Robot UI
    task).
  - Its UI path has not been run with a past date.

## Preconditions

- An **active asset** whose `LifecycleStartDate` is on or before the effective date. To build one:
  `scripts/build_quote_to_asset.py --start <past start> --end <end>`, adding `--skip-usage-verify`
  for a non-usage SKU. To renew an **expired** term, pass an `--end` that is also in the past
  (the script defaults it otherwise).
- Help's other limits (`ind.qocal_considerations_for_assets_with_backdated_changes.htm`; not
  measured here):
  - no backdating before the asset's start date;
  - none on an asset that has a future-dated cancel;
  - no amending a usage product that has both a future-dated and a backdated change;
  - no reducing quantity below what's available in the line's date range.

## 1. Amend

POST `/services/data/v68.0/connect/revenue-management/assets/actions/amend`:

```json
{"assetIds":["<assetId>"],"amendmentStartDate":"<effective-date>T00:00:00.000Z",
 "outputRecordType":"Order","quantityChange":1}
```

Returns `amendmentRecordId`: a Draft order whose `EffectiveDate` is the effective date, with one line
from that date to the asset's end. For a usage product the dev guide says to use
`outputRecordType: "Quote"`; not measured here.

## 2. Cancel

POST `.../assets/actions/cancel`:

```json
{"assetIds":["<assetId>"],"cancellationDate":"<effective-date>T00:00:00.000Z","outputRecordType":"Order"}
```

Returns `cancellationRecordId`: a negative-quantity line from the cancellation date to the end of
the term.

## 3. Renew an expired term

POST `.../assets/actions/renew`:

```json
{"assetIds":["<assetId>"],"outputRecordType":"Order",
 "renewalStartDate":"<effective-date>T00:00:00.000Z","renewalEndDate":"<end-date>T00:00:00.000Z"}
```

- ⚠ **Pass `renewalStartDate`.** Without it, the measured run rejected the expired asset:
  *"Select Override Renewal Term to renew expired or future-dated assets."*
- A **past** start date was not rejected in the measured run. The dev guide's request description
  says "today's date or a future date", though its own sample request uses a past one.

## Activating the order

Set `Status = Activated` on the returned order. In the measured run, amend, cancel and renew
orders needed all of these first:

- **shipping address**. The asset-action APIs don't copy the account's, just as quote-created orders
  don't. See `usage-consumption/building-usage-assets.md` → *FAILED_ACTIVATION*.
- **billing address and a bill-to contact**. Otherwise: *"We couldn't activate the Order. Enter the
  billing address and bill to contact associated with the account, and try again."*
  - This differs from new-sale orders on 262, which activated without them (txn-data-harness:
    `scripts/txn_data_harness/docs/contracts-sales-txn-quote.md`).
  - On 264, one new-sale order activated without Order billing fields (`building-usage-assets.md`).
    Whether new-sale orders need a bill-to contact wasn't isolated.

Fill them from what exists:
- **`BillToContactId` and `Billing*`:** take them from the account's original order when they're set.
  They're often null, because new-sale paths don't set them. Otherwise use `Billing*` from the
  Account and any account Contact for `BillToContactId`:
  `SELECT Id FROM Contact WHERE AccountId = '<accountId>' LIMIT 1`.
- **`Shipping*`:** from the Account.

## Verify

```bash
sf data query -o <sf-alias> -q "SELECT StartDate, EndDate, Quantity, Mrr FROM AssetStatePeriod WHERE AssetId = '<assetId>' ORDER BY StartDate"
sf data query -o <sf-alias> -q "SELECT LifecycleStartDate, LifecycleEndDate FROM Asset WHERE Id = '<assetId>'"
```

Worked example from the measured run:

| Action | Asset term | Effective date | After activation |
|---|---|---|---|
| Amend +1 | 2026-06-01 → 2027-05-31 | 2026-08-01 | periods `06-01→07-31` qty 1, `08-01→2027-05-31` qty 2 (order line 535.96) |
| Cancel (same asset) | — | 2026-09-01 | ends `2026-08-31`, and `LifecycleEndDate` 2026-08-31 (line qty −2, −962.61) |
| Renew an expired term (a different asset, qty 1) | 2025-06-01 → 2026-05-31 | 2026-06-01 | new period `2026-06-01→2027-05-31` qty 1, and `LifecycleEndDate` 2027-05-31 (line 394.50) |

## Not covered yet

- **The UI path on `RLM_ARC_Assets`.** Porting the backdated date input into it is todo 246.
- **A zero-quantity amendment that changes billing frequency** (INV-12 in the 264 solution overview). The amend API
  has no billing-frequency input, so it's a quote-side change.
- **Billing effects.** Per Help, credit memos are issued for previously invoiced periods; these
  scenarios ran without invoicing.
