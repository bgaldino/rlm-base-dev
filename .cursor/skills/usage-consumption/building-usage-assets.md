# Building Usage Assets — Transactional Data for Metered Demos

Read this when you need an **asset that carries usage entitlements**, which is the
precondition for any rating work. Parent skill: [SKILL.md](SKILL.md).

Usage rating can only run against assets holding entitlement buckets ("wallets"), and
the interesting cases are **backdated** — purchased early enough that a billing period
has actually closed. Producing that by hand takes minutes per account and is easy to
get subtly wrong (a line starting today, a quote in the running user's currency
instead of the account's). `scripts/build_quote_to_asset.py` produces it reproducibly.

```bash
python scripts/build_quote_to_asset.py --org <sf-alias> \
    --accounts "Infinitech,Kingsbridge Digital" \
    --sku QB-DB --start 2026-06-01 --end 2027-05-31
```

Exits 0 when every account reaches an asset with usage buckets, 1 otherwise.

## The chain, and why each step uses what it does

| Step | Mechanism | Why not something else |
|------|-----------|------------------------|
| Opportunity | Direct insert mirroring `RLM_QuickQuote` field-for-field | That flow is a **screen** flow, so Apex cannot invoke it — but every automation it relies on is record-triggered, so the same insert fires the same behaviour (including account-currency defaulting) |
| Quote + line | `POST /connect/rev/sales-transaction/actions/place` (Place Sales Transaction) with an object graph | Direct `QuoteLineItem` DML is **not viable** for a TermDefined product: the platform requires `BillingFrequency` and simultaneously refuses to let you set it unless the line's BillingTreatment has `CanChangeBillingFrequency = true` |
| Order | `createOrdersFromQuote` invocable | Same call the Create Order quick action runs via `RLM_CreateOrdersFromQuote` |
| Activation | Draft → Activated status transition | v67.0 exposes **no** Connect resource for order activation |

### ⛔ Endpoints that are gone in v67.0

Older Postman collections still list these; they return `NOT_FOUND`:

- `/commerce/sales-transactions/actions/place`
- `/commerce/quotes/actions/create-order`
- `/connect/revenue-management/orders/actions/activate`

## Selling model — not product — decides which line fields are legal

| Selling model | `BillingFrequency` | `EndDate` |
|---------------|--------------------|-----------|
| `TermDefined` | **required** | allowed |
| `Evergreen` | **required** | **rejected** |
| `OneTime` | must be null / `MilestonePlan` | **rejected** |

A single product may expose several — `QB-DAT-THPT` has Evergreen, Term Monthly, and
Term Annual — so `--selling-model` picks which `PricebookEntry` to use. Choosing the
wrong one produces a validation error that names the *field*, not the model, which
sends you looking in the wrong place.

## Commitment products: sold separately, linked afterwards

A commitment and its anchor are sold as **separate quotes**, assetized
independently, then tied together through `UsageCmtAssetRelatedObj`:

```bash
python scripts/build_quote_to_asset.py --org <alias> --accounts "<acct>" --sku QB-DB-TOKEN
python scripts/build_quote_to_asset.py --org <alias> --accounts "<acct>" \
    --sku QB-CMT-TKN-TIER --link-commitment QB-DB-TOKEN
```

**Nothing in the catalog can express this pairing.** `UsagePrdGrantBindingPolicy`
rejects commit products outright — *"Select a Product with the Usage Model Type as
Anchor or Pack"* and *"You can't bind a commitment-based usage product to a target."*

Without the junction the commitment is **inert**: consumption drains the anchor's
grant and rates at the anchor's rate, with no error to tell you the commitment was
ignored.

> Because the junction joins two **Assets**, it is transactional data and can
> **never** live in a design-time SFDMU plan.

Binding a commitment to an existing *asset* at quote time is also rejected
(*"selected the correct usage product for the associated quote or order"*), which is
why `--bind-extra-lines` is off by default.

## Pack products need an anchor

A `UsageModelType = Pack` product draws down against an anchor's wallet and cannot
stand alone — activation fails with *"the usage product is missing a binding
instance"*. Bind it to an anchor asset that already exists on the account:

```bash
python scripts/build_quote_to_asset.py --org <alias> --accounts "<acct>" \
    --sku QB-TOKENS-PACK --anchor-sku QB-DB-TOKEN
```

## Prerequisites and gotchas

- **Reset the account first.** `Asset` carries no lookup back to the Order or Quote
  it came from, so the script matches on **account + product** — a pre-existing asset
  for the same SKU makes the result ambiguous.
- **Not every account can transact.** Several scratch accounts ship with no shipping
  address or bill-to contact and fail with `FAILED_ACTIVATION`. The QuantumBit demo
  accounts (Infinitech, Kingsbridge Digital, Coralbay Technologies, Helvetia Cloud,
  Northlight Systems, Rheintech Solutions, Sakura Systems, Global Media) all have both.
- **Backdate deliberately.** `--start` must be early enough that a billing period has
  closed, or there is nothing for rating to settle.

## Key options

| Option | Purpose |
|--------|---------|
| `--sku` / `--accounts` / `--org` | What to sell, to whom, where |
| `--start` / `--end` / `--term` | Backdating and term (default start `2026-06-01`) |
| `--selling-model` | Pick the PricebookEntry when a product exposes several |
| `--link-commitment ANCHOR_SKU` | Post-assetization `UsageCmtAssetRelatedObj` link — **required** for a commitment to affect rating |
| `--anchor-sku ANCHOR_SKU` | Bind to an existing anchor asset (required for Pack) |
| `--with-sku SKU` | Additional product on the **same** quote |
| `--billing-frequency` | Mandatory for TermDefined/Evergreen (default `Monthly`) |
| `--billing-timing` | Substring picking among a currency's BillingTreatments (default `Advance`) |
| `--period-boundary` | Default `Anniversary` |

## Related

- General Quote→Order→**Invoice** demo volume: `.cursor/skills/txn-data-harness/SKILL.md`
- REST API reference: `.cursor/skills/rlm-business-apis/SKILL.md`
- What to do once the asset exists: [SKILL.md](SKILL.md) step 2 onward
